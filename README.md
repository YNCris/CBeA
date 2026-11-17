# CBeA: Cellular Behavior Atlas

CBeA combines cell-shape dynamics and centroid motion to characterize cellular behavior. This repository accompanies *Nitrate shapes stress-resilient behavioral dynamics during sustained cellular expansion* and provides the compiled feature-extraction module, a real-cell demonstration, and scripts to reproduce the quantitative analyses in Figures 1–3.

## Data

[Download the accompanying data from Zenodo](https://zenodo.org/records/24302450). The deposit contains two real-cell examples, derived measurements, motif definitions, atlas visualization coordinates, statistical reference results, and figure exports.

**Dataset DOI:** [10.5281/zenodo.24302450](https://doi.org/10.5281/zenodo.24302450). Use this DOI to cite the data used by these analyses. The [all-versions DOI](https://doi.org/10.5281/zenodo.24302449) points to the latest dataset deposit.

Extract the archive beside the repository so that the directories are arranged as follows:

```text
working_directory/
├── CBeA/          # this repository
└── dataset/      # extracted Zenodo data
```

Verify the extracted data and repository checksums before analysis:

```text
python verify_release.py --code . --data ../dataset
```

## Installation

The supplied compiled module requires **CPython 3.10 on 64-bit Windows**. Statistical analysis uses NumPy, SciPy, pandas, and Matplotlib; the tested dependency versions are specified in [requirements-replay.txt](requirements-replay.txt). Computation runs on the CPU; a GPU is not required. The statistical script uses one BLAS/OpenMP thread.

From the repository directory, in a Python 3.10 environment, install the dependencies:

```text
python -m pip install -r requirements-replay.txt
```

The compiled module is included in `cellatlas_repro/` and is loaded directly by the demonstration script. For binary compatibility and runtime requirements, see [the feature-extraction guide](NATIVE_CORE_README.md).

## Run the demonstration

```text
python validate_demo.py --data ../dataset/minimal_demo --out ../results/native/validation.json
```

This command recomputes Fourier descriptors and motion measurements for one MDA-MB-231 cell and one iDMSC cell, each followed for 16 frames. It checks the input-file hashes and compares the calculated features with the supplied reference values. A successful run writes `validation.json` with `passed: true` and one recomputed NPZ file per cell.

## Reproduce the figure analyses

```text
python reproduce.py --data ../dataset --out ../results/statistics
```

The script independently calculates group means, two-way ANOVA, and Tukey comparisons from the deposited point-level measurements. It produces:

| Output | Content |
| --- | --- |
| `group_means_recomputed.csv` | Group means and sample counts |
| `ANOVA_recomputed.csv` | Main effects, interaction, and ANOVA statistics |
| `Tukey_recomputed.csv` | Pairwise differences, confidence intervals, and significance |
| `verification.json` | Numerical comparisons against the reference results |
| Three PNG files | Recomputed quantitative plots for Figures 1–3 |

The default mode evaluates every comparison's significance and a subset of numeric adjusted p values. To calculate **all** numeric Tukey adjusted p values, run:

```text
python reproduce.py --data ../dataset --out ../results/statistics_full --full-p
```

See [the statistical analysis guide](REPLAY_README.md) for the calculation conventions, validation tolerances, and output interpretation.

## Runtime

Measured in a fresh CPython 3.10.20 environment on Windows x64 (Intel(R) Core(TM) i9-14900K, 127.7 GiB RAM), with one BLAS/OpenMP thread and no GPU:

| Step | Elapsed time |
| --- | ---: |
| Create isolated environment | 4.5 s |
| Download and install dependencies | 44.9 s |
| Run the two-cell demonstration | 0.63 s |
| Reproduce statistics, default mode | 11.6 s |

Installation time depends on network access; analysis time depends on hardware and storage. These measurements include process startup. The default replay passed verification for 88 statistical families, 264 ANOVA effects, all 45,210 Tukey significance decisions and 253 numeric adjusted p values. See [the environment record](validation/environment.json) and [the feature-validation report](validation/demo.json).

The retained [full adjusted-p verification](validation/statistics.json) additionally checked all 45,210 numeric adjusted p values and completed in 372 s in its recorded run.

## Analysis scope

The executable workflows cover feature extraction from tracked contours and centroids, and statistical analysis of derived measurements. The study's full imaging workflow additionally uses segmentation, tracking, dynamic temporal segmentation, DTAK similarity, embedding, and motif identification. Full image processing and atlas refitting require inputs and upstream software beyond the deposited demonstration. [Pipeline coverage](PIPELINE_SCOPE.md) identifies the available inputs and computations for each stage.

## Citation

> Han, Y., Hou, X., Li, X., Zhang, R., Chen, M., & Wang, S. *Nitrate shapes stress-resilient behavioral dynamics during sustained cellular expansion: source data and minimal demonstration*. Zenodo. https://doi.org/10.5281/zenodo.24302450

Machine-readable software and data references are provided in [CITATION.cff](CITATION.cff). The DOI above identifies the dataset. [Data and code availability](DATA_AVAILABILITY.md) provides the accompanying availability statement.

## License and contact

The software is distributed under the [PolyForm Noncommercial License](LICENSE); the data use [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). Commercial uses outside the relevant license permissions require institutional authorization. See [NOTICE](NOTICE) and [third-party notices](THIRD_PARTY_NOTICES.md) for scope and attribution.

For scientific questions or authorization enquiries, contact Songlin Wang ([slwang@ccmu.edu.cn](mailto:slwang@ccmu.edu.cn)) or Mo Chen ([chenm7@sustech.edu.cn](mailto:chenm7@sustech.edu.cn)).
