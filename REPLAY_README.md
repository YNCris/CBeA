# Quantitative replay of the retained manuscript data

Run from any directory with Python 3.10 or later and NumPy, pandas, SciPy, and Matplotlib installed:

```text
python reproduce.py --data /path/to/extracted/dataset --out /path/to/replay_results
```

Use an output directory outside the data package. The script runs with one BLAS/OpenMP thread and does not modify source observations or frozen statistics.

The input directory must contain `figure1/source_data`, `figure1/statistics`, `figure2/source_data`, `figure2/statistics`, `figure3/source_data`, and `figure3/statistics`. Exact files and SHA256 values are recorded in each `verification.json`. No original workstation paths or network shares are required.

## What is actually recomputed

- Figure 1: the two cell cohorts' time-mean cell-count and mean-area ΔF/F₀ point observations.
- Figure 2: the continuous and 1/4/8 mM gradients' corresponding time-mean point observations.
- Figure 3: whole-window motif fractions from covered-cell-frame counts, separately for each cohort and motif.
- Balanced Drug × Nitrate ANOVA with interaction, residual sum of squares, degrees of freedom, F statistics, and ANOVA p values.
- Every complete-family Tukey comparison: group means, signed difference, pooled MSE, q statistic, 95% simultaneous confidence limits, and the 0.05 significance decision.

The script verifies all of these available frozen quantities, checks that every pair is present exactly once, and exits with status 2 when numeric checks fail. It refuses an unbalanced or incomplete factorial design instead of silently substituting another statistical model. Default tolerances are recorded in the code: generally absolute 1e-8 and relative 2e-7, with a wider absolute 2e-7 allowance for adjusted p calculations.

Numeric Tukey adjusted p values require more expensive studentized-range integration. By default, three or fewer deterministic comparisons per family are checked: the smallest q, largest q, and q nearest the 0.05 critical value. All remaining `p_Tukey_recomputed` fields are blank and `p_recomputed` is false. Frozen reference p values are retained in a separately named comparison column. The significance decision for **every** pair is independently recomputed from q and its critical value. To also recompute all numeric adjusted p values, use:

```text
python reproduce.py --data /path/to/extracted/dataset --out /path/to/full_p_replay --full-p
```

The full-p mode can be substantially slower; it performs integrations for tens of thousands of comparisons. No performance or completion claim is made until a run's verification report is available.

## Conventions that matter

The Figure 3 source table already uses motif IDs **1–20**. Label **0** means undefined/unassigned; it remains in each point's denominator. Do not add one to the motif IDs. The script checks that all fractions including label 0 sum to 100% and that percentages agree with the covered-frame counts. Motif numbers belong to their own cell-model dictionary; a 231 motif and an iDMSC motif bearing the same number are not assumed biologically equivalent.

Figures 1 and 2 store signed differences as **group 1 minus group 2**. Figure 3 stores them as **group 2 minus group 1**. The code explicitly preserves these different conventions and writes the convention beside each regenerated comparison.

Each statistical observation is an imaging point. Points can share wells. This replay reproduces the manuscript's exploratory point-level analysis; it does not convert those points into independent biological replicates or introduce a well-level mixed model. Tukey families cover all Drug × Nitrate combinations separately for each outcome, cohort, and motif. There is no extra across-motif correction in this replay.

## Outputs and limits

`ANOVA_recomputed.csv`, `Tukey_recomputed.csv`, `group_means_recomputed.csv`, and `verification.json` are newly calculated from source observations. Three PNGs regenerate point plots and motif-difference heatmaps from those observations; they are diagnostic quantitative plots, not copies or pixel-identical reconstructions of the manuscript's layouts.

This path begins with retained derived point measurements. It does **not** rerun raw-image segmentation, tracking, Fourier extraction, ACA segmentation, reference sampling, atlas embedding, or full acquisition processing. A separate demo or private audit source bundle may cover some of those stages; describe its actual coverage separately. Running this script is not evidence that an omitted upstream stage has been reproduced.
