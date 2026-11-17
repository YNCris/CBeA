# Fourier and motion feature extraction

The compiled CBeA module calculates cell-shape descriptors from contours and locomotion measurements from tracked centroids. The demonstration uses the same feature definitions as the study.

## Requirements

- CPython 3.10 on 64-bit Windows (`cp310-win_amd64`).
- NumPy; the tested environment is specified in [requirements-replay.txt](requirements-replay.txt).
- Microsoft Visual C++ 2015–2022 Redistributable (x64), where it is not already installed.

The native extension is included in `cellatlas_repro/` and is imported directly from this repository. It does not require a compiler or a GPU at runtime. The supplied binary is specific to this Python and operating-system combination; other platforms require a compatible build.

To install only the feature demonstration's dependency, run:

```text
python -m pip install -r requirements-demo.txt
```

## Demonstration

Download and extract the [Zenodo dataset](https://doi.org/10.5281/zenodo.24302450). From the repository directory, run:

```text
python validate_demo.py --data ../dataset/minimal_demo --out ../results/native/validation.json
```

Change `--data` if the dataset was extracted elsewhere. The output directory is created automatically.

The two demonstration sequences contain 16 frames each, from one MDA-MB-231 cell and one iDMSC cell. The script first checks the SHA-256 hashes specified in the demo schema, then calculates and validates:

| Measurement | Values per frame | Comparison tolerance (absolute / relative) |
| --- | --- | --- |
| Fourier invariants | 60 real values | 1e-6 / 1e-5 |
| Complex Fourier coefficients | 33 complex values | 1e-6 / 1e-6 |
| Centroid-motion and shape-change measurements | 7 real values | 1e-5 / 5e-6 |

A successful run returns exit status 0 and writes `validation.json` with `passed: true`. It also writes a `*_native_recomputed.npz` file for each sequence containing the calculated invariants, coefficients, motion, scale, perimeter, sampled contours, and feature names. Failed hash or numerical comparisons raise an error.

## Feature definitions

Contours are oriented consistently and resampled at 256 equally spaced arc-length positions. Complex Fourier coefficients and scale-normalized invariants are calculated through harmonic order 16. Contour coordinates are in micrometres and use a Cartesian convention, with image y coordinates negated.

Motion calculations use contiguous observed identity intervals. The seven columns are displacement in x and y, speed, signed acceleration, the cosine and sine of the turning angle, and the rate of change of the Fourier-invariant vector. Motion retains the signed-turn convention of the image coordinates. Undefined initial speed or turning values remain NaN, and missing observations are not temporally interpolated.

The Python interface exposes `describe`, `feature_names`, and `derive_motion` in `cellatlas_repro`. Array conversion and column naming are handled by Python; feature calculations run in the compiled module.

## Relationship to the behavior atlas

This demonstration starts with tracked contours and centroids. The supplied image crops and masks show the source cells, while reference motif labels describe their existing atlas assignments. Dynamic temporal segmentation, DTAK similarity, embedding, and motif assignment are separate stages described in [pipeline coverage](PIPELINE_SCOPE.md).

The module is distributed under the [software license](LICENSE). Attribution and upstream software terms are documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
