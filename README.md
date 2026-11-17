# Cellular Behavior Atlas (CBeA): manuscript reproduction package

Submission candidate **0.1.0-rc2**, prepared for *Nitrate shapes stress-resilient behavioral dynamics during sustained cellular expansion* (V14).

This repository contains a compiled **original Fourier contour/motion feature core**, a small real-data demo interface, and inspectable scripts for reproducing derived quantitative analyses. It is not a compiled redistribution of the original ACA/DTAK implementation or a substitute for its license. No model-training jobs or complete raw acquisitions are included.

## Quick start

The native core build targets **64-bit Windows, CPython 3.10**. Other platforms require a separately built and validated binary; they have not been tested by this release. The statistical replay itself is portable Python and does not require the native extension or MATLAB.

1. Extract the code and dataset archives into separate directories.
2. Use a Python 3.10 environment. Install the supplied native wheel as described in `NATIVE_CORE_README.md`, and install `requirements-replay.txt` for statistical replay.
3. Run the documented compiled-core demo against `dataset/minimal_demo`. It checks computed features against original expected outputs. See `NATIVE_CORE_README.md` for the exact command and tested build information.
4. Recompute derived statistics:

```text
python reproduce.py --data ../dataset --out ../replayed_statistics
python reproduce.py --data ../dataset --out ../replayed_all_probabilities --full-p
```

Default mode independently recomputes all group means, ANOVA effects, Tukey differences/q/CI/significance, and a declared subset of numeric adjusted p values. `--full-p` recomputes every numeric adjusted p value. Both modes produce `verification.json` and fresh quantitative plots. The comparison uses original frozen exports solely as references, never as substitute computed results. More details and numerical tolerances are in `REPLAY_README.md`.

## Reproduction scope

| Included computation | Input | Coverage |
| --- | --- | --- |
| Native Fourier and motion demo | Two real tracked-cell contour/position/time sequences | Exact feature equivalence check; neither segmentation nor ACA fitting |
| ANOVA and Tukey replay | Full retained point-level derived values | All manuscript cohorts, outcomes and 20 named motifs per cell model |
| Quantitative plots | Retained source point measurements | Independently redrawn statistical panels; not decorative or pixel-identical final layouts |
| Frozen atlas visualization sources | 5,000 coordinates/model and displayed similarity overview | Visualization of original atlas results, not full atlas refitting |

Full raw-image reprocessing additionally requires original acquisition files, CPDINO/Trackastra weights and configuration, original ACA/DTAK and MATLAB dependencies, reference features and full fitted atlas artifacts. They are not bundled. The two-cell demo and frozen coordinate tables do not establish a full raw-to-paper reproduction. See `THIRD_PARTY_NOTICES.md` and the dataset README.

The statistical unit remains the original imaging point, with its known within-well dependence. This is verification of the manuscript's exploratory computation, not a new biological-replication design. Motif IDs are model-specific: zero is undefined and the named classes are 1–20; do not renumber zero as class 1. The latest Figure 2 uses untransformed ΔF/F0 values.

## License and institutional authorization

The original software in this release is licensed under **PolyForm Noncommercial License 1.0.0** (SPDX: PolyForm-Noncommercial-1.0.0). The complete, unmodified terms are in LICENSE; software scope and commercial-inquiry routes are in NOTICE.

The license permits noncommercial purposes and the uses expressly covered by its other provisions. Its Noncommercial Organizations provision permits use by the listed charitable, educational, public research, public safety or health, environmental protection, and government organizations regardless of funding source or resulting funding obligations. This release does not narrow those permissions.

Uses outside the permission granted by that license require separate authorization from the relevant institutional rightsholder(s), acting through an authorized representative. Commercial inquiries may be routed through Songlin Wang (slwang@ccmu.edu.cn) or Mo Chen (chenm7@sustech.edu.cn); these contacts are not assertions of personal ownership or authority to bind every institution.

Third-party components keep their original terms. The dataset, microscopy images, figures and manuscript tables are licensed separately and are not covered by this software grant. This is a partially source-available software distribution with a compiled core; it is not described as an OSI-approved open-source release.

The C++ source and build records remain in a separate author-private bundle for institutional/editorial review and reproducibility auditing. They are excluded from the public binary package. Compilation does not guarantee protection against reverse engineering. Journal code-access requirements are assessed separately from the license choice.

## Version and citation

Use CITATION.cff as citation metadata. This code is staged in the private repository https://github.com/YNCris/CBeA; access requires authorization from its owner. Version 0.1.0-rc2 is a submission candidate; no public release or DOI has been issued. The separately prepared dataset is licensed under CC BY-NC 4.0, with its hosting repository still to be selected. Dataset and code manifests contain content hashes; verify them after transfer. Original data, manuscript and historical analyses were not overwritten.

