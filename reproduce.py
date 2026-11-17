# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Recompute manuscript point-level ANOVA/Tukey quantities from retained inputs.

No image segmentation, tracking, atlas fitting, or raw acquisition reprocessing
is performed here. Scientific source observations and frozen tables remain read-only.
"""
import os
for variable in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS'):
    os.environ[variable] = '1'

import argparse
from functools import lru_cache
import hashlib
from itertools import combinations
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np
import pandas as pd
import scipy
from scipy.stats import f as f_distribution, studentized_range

DRUGS = ['Vehicle', 'Cisplatin', 'DEM', 'Etp', 'Hydroxyurea', 'ISA-2011B']


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read_table(root, relative, manifest):
    path = root / relative
    frame = pd.read_csv(path, dtype={'batch': str})
    for column in ('drug', 'drug1', 'drug2'):
        if column in frame:
            frame[column] = frame[column].replace({'ISA-2011b': 'ISA-2011B'})
    manifest.append({'file': relative, 'sha256': digest(path), 'rows': len(frame)})
    return frame


def factorial(frame, value):
    """Ordinary balanced full Drug x Nitrate model; no repeated-measures claim."""
    columns = ['drug', 'nitrate_mM', 'point_id', value]
    if frame[columns].isna().any().any() or not np.isfinite(frame[value]).all():
        raise ValueError('Missing or nonfinite factorial input')
    if frame.point_id.duplicated().any():
        raise ValueError('A point is duplicated within one statistical family')
    drugs = [drug for drug in DRUGS if drug in frame.drug.unique()]
    if set(drugs) != set(frame.drug.unique()):
        raise ValueError('Unrecognized drug label')
    doses = sorted(frame.nitrate_mM.unique())
    groups = [(drug, float(dose)) for drug in drugs for dose in doses]
    observations = {key: group[value].to_numpy(float)
                    for key, group in frame.groupby(['drug', 'nitrate_mM'], sort=False)}
    if set(observations) != set(groups):
        raise ValueError('Incomplete factorial design')
    sizes = {len(observations[group]) for group in groups}
    if len(sizes) != 1 or min(sizes) < 2:
        raise ValueError('Expected a balanced replicated design; refusing silent model substitution')
    n = sizes.pop()
    a, b = len(drugs), len(doses)
    means = np.array([observations[group].mean() for group in groups]).reshape(a, b)
    grand = means.mean()
    drug_mean, dose_mean = means.mean(1), means.mean(0)
    ss_error = sum(np.square(observations[group] - observations[group].mean()).sum() for group in groups)
    df_error = a * b * (n - 1)
    mse = float(ss_error / df_error)
    if mse <= 0:
        raise ValueError('Degenerate residual variance; no silent p-value replacement')
    components = [
        ('Drug', float(b * n * np.square(drug_mean - grand).sum()), a - 1),
        ('Nitrate', float(a * n * np.square(dose_mean - grand).sum()), b - 1),
        ('Drug:Nitrate', float(n * np.square(means - drug_mean[:, None] - dose_mean[None, :] + grand).sum()), (a - 1) * (b - 1)),
    ]
    effects = []
    for term, ss, df in components:
        statistic = ss / df / mse
        effects.append(dict(term=term, SS=ss, df_num=df, MS=ss / df, F=statistic,
                            p_ANOVA=float(f_distribution.sf(statistic, df, df_error)),
                            SS_error=float(ss_error), df_error=df_error, MSE=mse,
                            partial_eta_squared=ss / (ss + ss_error)))
    flat = {group: float(means.ravel()[i]) for i, group in enumerate(groups)}
    return dict(groups=groups, means=flat, n=n, k=a * b, df_error=df_error,
                MSE=mse, effects=effects)


@lru_cache(None)
def critical_q(groups, df_error):
    return float(studentized_range.ppf(.95, groups, df_error))


class Verification:
    def __init__(self):
        self.fields = {}
        self.failures = []

    def check(self, name, actual, expected, context, atol=1e-8, rtol=2e-7):
        actual, expected = float(actual), float(expected)
        ok = bool(np.isfinite(actual) and np.isfinite(expected) and
                  np.isclose(actual, expected, atol=atol, rtol=rtol))
        entry = self.fields.setdefault(name, {'checked': 0, 'failed': 0, 'max_abs_error': 0.})
        entry['checked'] += 1
        entry['failed'] += int(not ok)
        error = abs(actual - expected)
        entry['max_abs_error'] = max(entry['max_abs_error'], error if np.isfinite(error) else float('inf'))
        if not ok and len(self.failures) < 100:
            self.failures.append(dict(field=name, context=context, actual=actual, expected=expected))


def pair_key(first, second):
    return tuple(sorted((first, second)))


def compare_family(model, frozen, metadata, verifier, full_p):
    figure = metadata['figure']
    is_motif = figure == 'figure3'
    dose1, dose2 = ('dose1', 'dose2') if is_motif else ('nitrate1_mM', 'nitrate2_mM')
    difference = 'diff_percent_points' if is_motif else 'difference_1minus2'
    low, high = ('ci_low', 'ci_high') if is_motif else ('CI95_low', 'CI95_high')
    pairs = [((row.drug1, float(getattr(row, dose1))), (row.drug2, float(getattr(row, dose2))))
             for row in frozen.itertuples(index=False)]
    keys = [pair_key(*pair) for pair in pairs]
    expected = {pair_key(first, second) for first, second in combinations(model['groups'], 2)}
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError(f'Frozen pair table is incomplete or duplicated: {metadata}')
    standard_error = np.sqrt(model['MSE'] / model['n'])
    threshold = critical_q(model['k'], model['df_error'])
    output = []
    for index, ((first, second), reference) in enumerate(zip(pairs, frozen.to_dict('records'))):
        mean1, mean2 = model['means'][first], model['means'][second]
        diff = mean2 - mean1 if is_motif else mean1 - mean2
        q = abs(diff) / standard_error
        record = dict(**metadata, drug1=first[0], dose1=first[1], drug2=second[0], dose2=second[1],
                      mean1=mean1, mean2=mean2, difference=diff,
                      difference_definition='mean2-minus-mean1' if is_motif else 'mean1-minus-mean2',
                      q_statistic=q, CI95_low=diff - threshold * standard_error,
                      CI95_high=diff + threshold * standard_error,
                      significant_alpha_0p05=bool(q > threshold), family_groups=model['k'],
                      family_pairs=len(pairs), n_points_per_group=model['n'], df_error=model['df_error'],
                      MSE=model['MSE'], p_Tukey_recomputed=np.nan, p_recomputed=False,
                      reference_p_Tukey=float(reference['p_Tukey']))
        context = f'{metadata}/{first}/{second}'
        for target, source in [('difference', difference), ('q_statistic', 'q_statistic'),
                               ('MSE', 'MSE'), ('CI95_low', low), ('CI95_high', high),
                               ('df_error', 'df_error'), ('family_groups', 'family_groups')]:
            if source in reference:
                verifier.check('Tukey_' + target, record[target], reference[source], context)
        for name in ('mean1', 'mean2'):
            if name in reference:
                verifier.check('Tukey_' + name, record[name], reference[name], context)
        if abs(reference['p_Tukey'] - .05) > 1e-8:
            verifier.check('Tukey_significant_alpha_0p05', record['significant_alpha_0p05'],
                           reference['p_Tukey'] < .05, context, atol=0, rtol=0)
        output.append(record)
    qvalues = np.array([row['q_statistic'] for row in output])
    # Numeric p checks span both tails and the decision boundary in every family.
    selected = np.arange(len(output)) if full_p else np.unique([
        int(np.argmin(qvalues)), int(np.argmax(qvalues)), int(np.argmin(abs(qvalues - threshold)))])
    values = studentized_range.sf(qvalues[selected], model['k'], model['df_error'])
    for index, value in zip(selected, values):
        output[index]['p_Tukey_recomputed'] = float(value)
        output[index]['p_recomputed'] = True
        verifier.check('Tukey_adjusted_p_selected', value, output[index]['reference_p_Tukey'],
                       f'{metadata}/pair{index}', atol=2e-7, rtol=2e-6)
    return output


def compare_anova(model, frozen, metadata, verifier):
    term_column = 'effect' if 'effect' in frozen else 'term'
    if set(frozen[term_column]) != {effect['term'] for effect in model['effects']} or len(frozen) != 3:
        raise ValueError(f'Unexpected ANOVA terms: {metadata}')
    result = []
    for effect in model['effects']:
        reference = frozen[frozen[term_column] == effect['term']].iloc[0].to_dict()
        for target, alternatives in [('SS', ['SS']), ('F', ['F']), ('MSE', ['MSE']),
                                     ('MS', ['MS']), ('df_num', ['df_num', 'df']),
                                     ('df_error', ['df_error']), ('p_ANOVA', ['p_ANOVA', 'p'])]:
            source = next((name for name in alternatives if name in reference), None)
            if source:
                verifier.check('ANOVA_' + target, effect[target], reference[source],
                               f'{metadata}/{effect["term"]}')
        result.append(dict(**metadata, **effect))
    return result


def plot_values(long_data, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 6, 'axes.linewidth': .5})
    for figure in ('figure1', 'figure2'):
        frame = long_data[long_data.figure == figure]
        combinations_ = list(frame[['batch', 'measure']].drop_duplicates().itertuples(index=False, name=None))
        fig, axes = plt.subplots(len(combinations_), 6, figsize=(11.5, 2 * len(combinations_)), squeeze=False)
        for row, (batch, measure) in enumerate(combinations_):
            for column, drug in enumerate(DRUGS):
                ax = axes[row, column]
                data = frame[(frame.batch == batch) & (frame.measure == measure) & (frame.drug == drug)]
                doses = sorted(data.nitrate_mM.unique())
                for i, dose in enumerate(doses):
                    values = data[data.nitrate_mM == dose].value.to_numpy()
                    x = np.full(len(values), i) + np.linspace(-.16, .16, len(values))
                    ax.scatter(x, values, s=4, c=[plt.cm.viridis(i / max(1, len(doses) - 1))], linewidths=0)
                    ax.plot([i - .22, i + .22], [values.mean()] * 2, color='black', linewidth=.7)
                ax.set_xticks(range(len(doses)), [f'{dose:g}' for dose in doses])
                ax.set_xlabel('Nitrate (mM)')
                ax.spines[['top', 'right']].set_visible(False)
                if row == 0:
                    ax.set_title(drug)
                if column == 0:
                    ax.set_ylabel(f'{batch}\n{measure}: time-mean ΔF/F₀')
        fig.suptitle('Quantitative replay from retained point observations; each dot is an imaging point', fontsize=9)
        fig.tight_layout(rect=(0, 0, 1, .97))
        fig.savefig(output / f'{figure}_quantitative_replay.png', dpi=200)
        plt.close(fig)


def plot_motifs(means, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import TwoSlopeNorm
    data = means[means.figure == 'figure3']
    matrices = []
    for batch in ('231', '1005', 'grad0_10', 'grad148'):
        reference = 1. if batch == 'grad148' else 0.
        subset = data[data.batch == batch]
        left = subset[subset.nitrate_mM == reference].pivot(index='drug', columns='motif', values='mean')
        right = subset[subset.nitrate_mM == 4.].pivot(index='drug', columns='motif', values='mean')
        matrix = (right - left).reindex(index=DRUGS, columns=range(1, 21)).to_numpy()
        matrices.append((batch, reference, matrix))
    limit = max(float(np.abs(matrix).max()) for _, _, matrix in matrices)
    fig, axes = plt.subplots(2, 2, figsize=(11, 5.4), layout='constrained')
    for ax, (batch, reference, matrix) in zip(axes.ravel(), matrices):
        graphic = ax.imshow(matrix, aspect='auto', cmap='BrBG_r', norm=TwoSlopeNorm(vmin=-limit, vcenter=0, vmax=limit))
        ax.set(title=f'{batch}: 4 − {reference:g} mM nitrate', xticks=range(20), xticklabels=range(1, 21),
               yticks=range(6), yticklabels=DRUGS, xlabel='Motif ID within its own cell-model dictionary')
    fig.colorbar(graphic, ax=axes, label='Difference in motif fraction (percentage points)', shrink=.8)
    fig.suptitle('Recomputed group means; matching motif IDs across 231 and iDMSC do not imply correspondence', fontsize=9)
    fig.savefig(output / 'figure3_motif_difference_replay.png', dpi=200)
    plt.close(fig)


def run(data_root, output, full_p=False):
    start = time.perf_counter()
    output.mkdir(parents=True, exist_ok=True)
    manifest, input_long, families = [], [], []
    f1 = 'figure1/'
    t1 = read_table(data_root, f1 + 'statistics/Prism_Tukey66_all_pairs_v36.csv', manifest)
    a1 = read_table(data_root, f1 + 'statistics/Prism_two_way_ANOVA_v36.csv', manifest)
    for measure in ('count', 'area'):
        frame = read_table(data_root, f1 + f'source_data/point_time_mean_{measure}_values_dff.csv', manifest)
        for batch, group in frame.groupby('batch', sort=False):
            metadata = dict(figure='figure1', batch=batch, measure=measure, motif=0)
            families.append((group, f'time_mean_{measure}_dff', t1[(t1.batch == batch) & (t1.measure == measure)],
                             a1[(a1.batch == batch) & (a1.measure == measure)], metadata))
            input_long.append(group.assign(figure='figure1', measure=measure, value=group[f'time_mean_{measure}_dff']))
    f2 = 'figure2/'
    points = read_table(data_root, f2 + 'source_data/point_time_means_dff.csv', manifest)
    t2 = read_table(data_root, f2 + 'statistics/Prism_Tukey_all_pairs.csv', manifest)
    a2 = read_table(data_root, f2 + 'statistics/Prism_two_way_ANOVA.csv', manifest)
    for batch, group in points.groupby('batch', sort=False):
        for measure in ('count', 'area'):
            metadata = dict(figure='figure2', batch=batch, measure=measure, motif=0)
            families.append((group, f'time_mean_{measure}_dff', t2[(t2.batch == batch) & (t2.measure == measure)],
                             a2[(a2.batch == batch) & (a2.measure == measure)], metadata))
            input_long.append(group.assign(figure='figure2', measure=measure, value=group[f'time_mean_{measure}_dff']))
    f3 = 'figure3/'
    points = read_table(data_root, f3 + 'source_data/point_motif_occupancy.csv', manifest)
    points = points[points.window == 'whole'].copy()
    if not np.allclose(points.percent, points.fraction * 100, atol=1e-9, rtol=1e-9):
        raise ValueError('Motif percent and fraction disagree')
    if not np.allclose(points.fraction, points.covered_cell_frames / points.all_covered_cell_frames, atol=1e-10, rtol=1e-9):
        raise ValueError('Motif fractions disagree with covered-cell-frame counts')
    sums = points.groupby(['batch', 'point_id']).percent.sum()
    if not np.allclose(sums, 100, atol=1e-8, rtol=1e-9):
        raise ValueError('Motif fractions including undefined label 0 do not sum to 100%')
    for pairs_file, anova_file, batches in [
        ('Tukey_all12_pairs.csv', 'two_way_ANOVA.csv', ('231', '1005')),
        ('gradient_Tukey_all_pairs_v15.csv', 'gradient_two_way_ANOVA_v15.csv', ('grad0_10', 'grad148')),
    ]:
        pairs = read_table(data_root, f3 + 'statistics/' + pairs_file, manifest)
        anova = read_table(data_root, f3 + 'statistics/' + anova_file, manifest)
        for batch in batches:
            if set(pairs[pairs.batch == batch].motif) != set(range(1, 21)):
                raise ValueError('Expected dictionary motif IDs 1..20; label 0 is undefined, not motif 1')
            for motif in range(1, 21):
                group = points[(points.batch == batch) & (points.motif == motif)]
                metadata = dict(figure='figure3', batch=batch, measure='fraction_percent', motif=motif)
                families.append((group, 'percent', pairs[(pairs.batch == batch) & (pairs.motif == motif)],
                                 anova[(anova.batch == batch) & (anova.motif == motif)], metadata))
    verifier = Verification()
    effects, pairs, means = [], [], []
    for index, (frame, value, frozen_pairs, frozen_anova, metadata) in enumerate(families, 1):
        model = factorial(frame, value)
        effects.extend(compare_anova(model, frozen_anova, metadata, verifier))
        pairs.extend(compare_family(model, frozen_pairs, metadata, verifier, full_p))
        for (drug, dose), mean in model['means'].items():
            means.append(dict(**metadata, drug=drug, nitrate_mM=dose, mean=mean, n_points=model['n']))
        print(f'REPLAY {index}/{len(families)} {metadata}', flush=True)
    effects, pairs, means = pd.DataFrame(effects), pd.DataFrame(pairs), pd.DataFrame(means)
    effects.to_csv(output / 'ANOVA_recomputed.csv', index=False)
    pairs.to_csv(output / 'Tukey_recomputed.csv', index=False)
    means.to_csv(output / 'group_means_recomputed.csv', index=False)
    plot_values(pd.concat(input_long, ignore_index=True), output)
    plot_motifs(means, output)
    passed = all(entry['failed'] == 0 for entry in verifier.fields.values())
    report = dict(passed=passed, elapsed_seconds=time.perf_counter() - start,
                  statistical_families=len(families), anova_effects=len(effects), tukey_pairs=len(pairs),
                  adjusted_p_values_recomputed=int(pairs.p_recomputed.sum()), full_p=full_p,
                  fields=verifier.fields, failures=verifier.failures, inputs=manifest,
                  versions=dict(python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__, scipy=scipy.__version__),
                  scope='Recompute point-level balanced ANOVA, all Tukey means/differences/MSE/q/CI/significance from retained derived inputs. No segmentation, tracking, atlas refit, or raw-acquisition replay.',
                  adjusted_p_policy='All numeric adjusted p values' if full_p else 'Per family: smallest q, largest q, and q nearest the 0.05 critical value. All remaining numeric p fields are empty, not copied as recomputed.',
                  motif_convention='Data and tests both use motif IDs 1..20. Label 0 is undefined/unassigned and stays in fraction denominators; it is not renumbered.',
                  effect_direction='Figures 1/2: mean1-minus-mean2. Figure3: mean2-minus-mean1, as in frozen tables.',
                  limitations=['Imaging points share wells; the replay preserves the published exploratory point-level model and does not add a well-level random effect.',
                               'Tukey correction is within each full factorial family, not across motifs or separate outcomes.',
                               'Plots are quantitative diagnostic regenerations, not pixel-identical recreations of manuscript layouts.'])
    (output / 'verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    print(f'VERIFICATION {"PASS" if passed else "FAIL"}: {len(pairs)} pairs, {int(pairs.p_recomputed.sum())} numeric p values', flush=True)
    return 0 if passed else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True, help='Extracted dataset root containing figure1/, figure2/, figure3/')
    parser.add_argument('--out', type=Path, required=True, help='Output directory; scientific source tables are never modified')
    parser.add_argument('--full-p', action='store_true', help='Recompute every studentized-range adjusted p; substantially slower than the default')
    args = parser.parse_args()
    if args.data.resolve() == args.out.resolve() or args.data.resolve() in args.out.resolve().parents:
        parser.error('Use an output directory outside the read-only dataset root')
    return run(args.data.resolve(), args.out.resolve(), full_p=args.full_p)


if __name__ == '__main__':
    raise SystemExit(main())
