# Third-party software

CBeA's original code and compiled Fourier/motion core are covered by [LICENSE](LICENSE) and [NOTICE](NOTICE). Third-party packages and external workflow components retain their own licenses. They are installed or obtained separately; their code, model weights and runtimes are not bundled here.

## Runtime dependencies

Exact tested dependency versions are pinned in [requirements-replay.txt](requirements-replay.txt).

| Component | Upstream terms | Project |
| --- | --- | --- |
| CPython | Python Software Foundation license and historical notices | [Python](https://docs.python.org/3.10/license.html) |
| NumPy | BSD 3-Clause; binary distributions include additional notices | [NumPy](https://github.com/numpy/numpy) |
| SciPy | BSD 3-Clause; binary distributions include additional notices | [SciPy](https://github.com/scipy/scipy) |
| pandas | BSD 3-Clause | [pandas](https://github.com/pandas-dev/pandas) |
| Matplotlib | Matplotlib license agreement based on the PSF license | [Matplotlib](https://matplotlib.org/stable/project/license.html) |

Preserve the complete notices supplied by each dependency, including notices for bundled numerical libraries, fonts and transitive packages. The license summaries above do not replace those terms.

The native extension uses the external Microsoft Visual C++ runtime on Windows. Obtain it from Microsoft under its terms if it is not already installed.

## External components used in the study

- **CPDINO / Cellpose:** [MouseLand/cellpose](https://github.com/MouseLand/cellpose), for cell segmentation.
- **Trackastra:** [weigertlab/trackastra](https://github.com/weigertlab/trackastra), for cell tracking.
- **Behavior Atlas:** [huangkang314/Behavior-Atlas](https://github.com/huangkang314/Behavior-Atlas), for dynamic temporal segmentation and DTAK similarity. The upstream repository includes inherited components with their own notices, including research-use terms. Its top-level license does not override those component-specific terms.
- **MATLAB and the upstream UMAP implementation:** obtained separately under their corresponding terms for the original atlas construction.

These external implementations are not included in the CBeA native binary or the statistical reproduction scripts. Commercial authorization for CBeA's original code does not grant rights to external code or model weights.

## Data

The [Zenodo dataset](https://doi.org/10.5281/zenodo.24302450) is licensed separately under CC BY-NC 4.0. Software licensing does not change data licensing or separately identified third-party rights.
