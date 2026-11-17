# Compiled feature core

The original Fourier/motion feature software is licensed under **PolyForm Noncommercial License 1.0.0**. See the unmodified LICENSE and scope/contact information in NOTICE. Third-party components retain their original terms.

## Supported binary platform

- CPython 3.10, 64-bit Windows (`cp310-win_amd64`). Python 3.11/3.12 and Linux/macOS cannot load this binary.
- Separately installed NumPy 1.23 or later, below 3.
- Microsoft Visual C++ 2015-2022 Redistributable (x64), if not already installed.

The Python interpreter, NumPy/OpenBLAS, Microsoft runtime and compiler are not bundled. The author-only C++ source/build recipe is retained outside the public code archive. Additional operating systems require separate author builds; they have not been validated by this release.

## Run the real-data demo

From this code directory, using a CPython 3.10 environment with NumPy:

```powershell
python validate_demo.py --data ..\dataset\minimal_demo --out ..\demo_output\native_validation.json
```

Replace the dataset path with the extracted dataset archive's `minimal_demo` folder. The local `cellatlas_repro` package contains the native extension, so no wheel installation is necessary for this command. Alternatively install the matching wheel from `wheels/` into a Python 3.10 environment. The same PolyForm terms and NOTICE are included inside the wheel.

The validation first checks SHA-256 checksums of the input and reference files, then independently recomputes all 60 Fourier invariants, 33 reconstructible complex coefficients and seven motion columns for two 16-frame real-cell sequences. It compares those values to the original analysis exports and writes JSON diagnostics plus recomputed NPZ files. It exits with an error if any check fails. This is a numerical equivalence test, not evidence that every scientific inference is reproduced from this small demo.

## What is and is not compiled

Compiled functions perform contour orientation handling, equal arc-length sampling (256 points), complex Fourier coefficients and scale-normalized invariants through harmonic order 16, and motion on contiguous observed identity intervals. Python wrappers only adapt arrays and expose column names.

Inputs are already extracted physical contour vertices and measured centroids. Image-y is negated for Cartesian contours, while motion retains the original image-coordinate signed-turn convention. The first undefined speed/turn values remain NaN. There is no temporal interpolation.

This binary does **not** include or perform CPDINO/Cellpose segmentation, Trackastra tracking, original MATLAB ACA/DTAK dynamic segmentation, UMAP embedding, or full frozen-atlas projection. Those manuscript stages retain their external dependencies and licenses. The demo's raw image/mask crops and pre-existing motif labels are supporting data; motif labels are not recomputed by this feature demo. Follow the release reproducibility matrix for the separate full-derived-data statistics replay and external-stage instructions.

No Python bytecode is used as a substitute for the native feature implementation. Native compilation is a distribution format and does not prevent reverse engineering.

