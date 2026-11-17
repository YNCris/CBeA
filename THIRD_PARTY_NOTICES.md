# Third-party notices and redistribution scope

This document describes the manuscript submission package, not a license for third-party components. The project's PolyForm Noncommercial 1.0.0 license covers only the original software specified in NOTICE, to the extent its rightsholder is entitled to license it. It does not change any upstream permission, restriction, copyright, or source-distribution obligation. The institution cannot grant commercial rights to third-party software merely by licensing its own core.

## Included original components

The native core implements custom Fourier-descriptor and centroid-motion measurements. It is not a compiled redistribution of CPDINO, Trackastra, ACA/DTAK, MATLAB, UMAP, or Behavior-Atlas. The native build targets CPython 3.10 on Windows x64. Python and scientific-library distributions are installed separately; this package is not a bundled Python interpreter or a complete standalone acquisition-to-atlas pipeline.

The public replay script recalculates balanced factorial ANOVA and Tukey quantities from retained derived point measurements and draws diagnostic plots. It uses the mathematical/library APIs of separately installed dependencies; it does not incorporate their source into the project's restricted license. The native demo and statistical replay do not re-run segmentation, tracking, temporal segmentation, or atlas fitting from the complete raw acquisitions.

## Separately installed replay dependencies

The following versions were used for validation. They are pinned in `requirements-replay.txt` and were not modified for this release.

| Component | Validated version | License identified in the installed distribution | Distribution in this package |
|---|---|---|---|
| CPython | 3.10.20; native ABI 3.10 | Python Software Foundation license and historical notices in `LICENSE_PYTHON.txt` | Interpreter not bundled |
| NumPy | 2.2.6 | BSD 3-Clause for NumPy; its wheel's `LICENSE.txt` also lists bundled third-party components | Wheel, source, OpenBLAS, and other library binaries not bundled |
| SciPy | 1.15.3 | BSD 3-Clause for SciPy; its wheel's `LICENSE.txt` also lists bundled third-party components | Wheel, source, and numerical-library binaries not bundled |
| pandas | 2.3.3 | BSD 3-Clause, installed `LICENSE` | Wheel and source not bundled |
| Matplotlib | 3.10.8 | Matplotlib license agreement for versions 1.3.0 and later, based on the PSF license; installed `LICENSE` | Wheel, source, fonts, and backend dependencies not bundled |

These summaries identify the main projects' terms and are not substitutes for their complete licenses. Dependencies may install additional packages or bundled runtime libraries with their own notices. Preserve all upstream notices supplied with those distributions. An installer or repackager who later redistributes a wheel, Python runtime, numerical library, font, or other dependency must assess that actual redistribution and include the corresponding complete license materials; this document is not a blanket permission to bundle them.

Official upstream references: [Python license](https://docs.python.org/3.10/license.html), [NumPy source](https://github.com/numpy/numpy), [SciPy source](https://github.com/scipy/scipy), [pandas source](https://github.com/pandas-dev/pandas), [Matplotlib license](https://matplotlib.org/stable/project/license.html). Version-specific evidence was checked in the locally installed distributions, including their bundled notices rather than package classifiers alone.

## External workflow components not redistributed

- **CPDINO / Cellpose and Trackastra:** upstream segmentation/tracking software and model weights are not included or relicensed. Existing segmentations, trajectories, and derived measurements are retained as study outputs. Anyone re-running these upstream stages must obtain the original software and required weights separately and assess their respective licenses and provenance. No commercial clearance for their software or weights is implied here.
- **ACA and DTAK:** original MATLAB/C++ temporal segmentation and alignment implementations are not included in the public core. In the inspected Behavior-Atlas snapshot, `src/aca/readme` expressly states that the software is free for research projects and requests citation to Zhou, De la Torre, and Hodgins, *Aligned Cluster Analysis for Temporal Segmentation of Human Motion* (FG 2008). That research permission is not evidence of unrestricted commercial redistribution or a right to put ACA under this project's license. Obtain any additional rights from the relevant upstream rightsholder.
- **Behavior-Atlas:** inspected commit `ca31d29b66b8afecf5fbde60b6ee1d8c126d0fb6` of [huangkang314/Behavior-Atlas](https://github.com/huangkang314/Behavior-Atlas). Its top-level `LICENSE` is MIT, copyright 2020 Kang Huang. That top-level license must not be treated as overriding separately stated terms for inherited subdirectories, particularly the ACA research-use statement. No upstream repository code is being redistributed as the project's own native core.
- **MATLAB and MATLAB UMAP:** MATLAB is an external commercial product and is not bundled. The inspected Behavior-Atlas `src/UMAP/license.txt` names Stephen Meehan (2019) and contains BSD-style redistribution conditions; the complete corresponding implementation and its dependencies still require their own provenance/license assessment. This MATLAB UMAP implementation is not distributed with the package. Neither MATLAB access nor a full atlas-refitting environment is supplied.
- **igraph and Leiden trial code:** exploratory graph-clustering dependencies are excluded from this release. The inspected local igraph 0.11.9 license text is GNU GPL version 2; the local leidenalg 0.10.2 license text is GNU GPL version 3. They are not required by the replay or Fourier/motion demo. No GPL-covered trial implementation or binary is being relicensed under the project's PolyForm Noncommercial license. If such code is distributed later, the applicable full license and corresponding-source obligations must be assessed separately.

Data, microscopy images, pretrained weights, upstream source, and original project code are different categories of material. The software PolyForm Noncommercial license does not itself grant data rights or establish ownership of any third-party material. Data-release terms must be specified separately. The public package's verified scope is the supplied minimal demo and replay of retained derived study results; it is not a claim of complete raw-image-to-final-figure reproduction.

The native build also depends on Microsoft's external Visual C++ 2015-2022 runtime on Windows. That runtime is not bundled or relicensed here; obtain it from Microsoft under Microsoft's terms. The Python wrapper imports the separately installed NumPy distribution. The compiled core itself contains the custom arc-length contour sampling, Fourier/DFT invariants, and centroid-motion calculations, not copied upstream algorithm implementations.
