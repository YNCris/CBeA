# Reproducing the quantitative analyses

The statistical workflow recalculates the manuscript's quantitative results from the deposited derived measurements. It uses the reference exports only to verify the new calculations.

## Requirements and execution

Use Python 3.10 or later with the NumPy, SciPy, pandas, and Matplotlib versions specified in [requirements-replay.txt](requirements-replay.txt). This workflow does not load the compiled feature module or require MATLAB. The tested environment is Windows with CPython 3.10.

From the repository directory, run:

```text
python -m pip install -r requirements-replay.txt
python reproduce.py --data ../dataset --out ../results/statistics
```

Use the extracted [Zenodo dataset](https://doi.org/10.5281/zenodo.24302450) as `--data`, and an output directory outside that dataset. The script uses one BLAS/OpenMP thread and leaves the source files unchanged. Input file hashes are recorded in the output verification report.

## Calculations

| Figure | Source observations | Recomputed analysis |
| --- | --- | --- |
| Figure 1 | Time-mean cell-count and mean-cell-area ΔF/F₀ for both cell models | Drug × Nitrate ANOVA and all within-family Tukey comparisons |
| Figure 2 | Corresponding measurements for the continuous and three-dose gradients | Drug × Nitrate ANOVA and all within-family Tukey comparisons |
| Figure 3 | Covered-cell-frame counts and motif fractions | Point-level fractions, Drug × Nitrate ANOVA, and motif-specific Tukey comparisons |

The balanced two-way ANOVA includes both main effects and their interaction. Each Tukey analysis recomputes group means, signed differences, pooled mean squared error, the studentized-range q statistic, simultaneous 95% confidence intervals, and the 0.05 significance decision. The script checks that every expected pair appears exactly once and rejects incomplete or unbalanced factorial designs.

### Numeric adjusted p values

By default, the significance decision is recalculated for every pair from q and its critical value. Numeric adjusted p values are evaluated for up to three deterministic comparisons per family: the smallest q, largest q, and q closest to the critical value. Other entries in `p_Tukey_recomputed` are left blank and have `p_recomputed` set to false. Reference p values remain in a separately named column.

To recompute every numeric adjusted p value, use:

```text
python reproduce.py --data ../dataset --out ../results/statistics_full --full-p
```

This option evaluates tens of thousands of studentized-range integrals and takes longer than the default mode.

## Analysis conventions

Each observation is an imaging point. Multiple points can share a well; they are not treated as independent biological replicates in the interpretation. The workflow reproduces the study's point-level statistical calculations and does not add a well-level mixed model.

Tukey families comprise all Drug × Nitrate groups separately for each outcome, cohort, and motif. No additional correction across different motifs is applied.

Motif IDs **1–20** refer to separate dictionaries for MDA-MB-231 and iDMSC. The same number in the two models does not imply the same phenotype. Label **0** denotes unassigned observations and remains in each point's denominator. The script checks that fractions, including label 0, sum to 100% and agree with the covered-frame counts.

Signed differences follow the deposited source conventions: group 1 minus group 2 for Figures 1 and 2, and group 2 minus group 1 for Figure 3. The convention is written beside each recomputed comparison.

## Outputs and validation

| File | Content |
| --- | --- |
| `group_means_recomputed.csv` | Newly calculated group means and sample counts |
| `ANOVA_recomputed.csv` | ANOVA effects, degrees of freedom, F statistics, and p values |
| `Tukey_recomputed.csv` | Newly calculated pairwise results and reference comparisons |
| `verification.json` | Input hashes, numerical checks, computation mode, and environment |
| `figure1_quantitative_replay.png` | Recomputed Figure 1 quantitative plots |
| `figure2_quantitative_replay.png` | Recomputed Figure 2 quantitative plots |
| `figure3_motif_difference_replay.png` | Recomputed motif-difference heatmaps |

A successful run returns exit status 0 and reports `passed: true`. The script returns exit status 2 when verification fails. Numerical comparisons generally use an absolute tolerance of 1e-8 and relative tolerance of 2e-7, with an absolute tolerance of 2e-7 for adjusted p values. The verification report records the results of these checks.

The PNGs show the recalculated quantities; the publication's arranged figure layouts are supplied separately in the dataset. This workflow begins with derived point measurements. Feature extraction is demonstrated separately in [NATIVE_CORE_README.md](NATIVE_CORE_README.md), and upstream image processing and atlas construction are described in [PIPELINE_SCOPE.md](PIPELINE_SCOPE.md).
