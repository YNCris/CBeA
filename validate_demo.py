# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Validate the compiled feature core against two real, frozen cell tracks.

Usage: python validate_demo.py --data PATH/TO/minimal_demo --out validation.json
This tests contour and motion features, not re-segmentation, ACA or atlas fitting.
"""
import argparse
import hashlib
import json
import platform
from pathlib import Path
import sys
import numpy as np
from cellatlas_repro import describe, derive_motion, feature_names, __version__, _native


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(actual, expected, name, atol, rtol):
    actual, expected = np.asarray(actual), np.asarray(expected)
    if actual.shape != expected.shape:
        raise AssertionError(f'{name}: shape mismatch {actual.shape} vs {expected.shape}')
    np.testing.assert_allclose(actual, expected, atol=atol, rtol=rtol, equal_nan=True,
                               err_msg=name)
    finite = np.isfinite(actual) & np.isfinite(expected)
    return dict(shape=list(actual.shape), atol=atol, rtol=rtol,
                max_absolute_error=float(np.max(np.abs(actual[finite] - expected[finite]))) if finite.any() else 0.,
                nan_pattern_equal=bool(np.array_equal(np.isnan(actual), np.isnan(expected))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    native = Path(_native.__file__)
    if native.suffix.lower() not in ('.pyd', '.so'):
        raise RuntimeError('Expected a compiled native extension, not Python fallback')
    manifest = json.loads((args.data/'schema.json').read_text(encoding='utf-8-sig'))
    records = []
    for item in manifest['samples']:
        inp_path, exp_path = args.data/item['inputs_file'], args.data/item['expected_file']
        assert sha(inp_path) == item['inputs_sha256'], 'Input checksum mismatch'
        assert sha(exp_path) == item['expected_sha256'], 'Reference checksum mismatch'
        with np.load(inp_path, allow_pickle=False) as z:
            inputs = {k: z[k] for k in z.files}
        with np.load(exp_path, allow_pickle=False) as z:
            expected = {k: z[k] for k in z.files}
        offsets = inputs['contour_offsets']
        features = [describe(inputs['contour_xy_um'][a:b]) for a, b in zip(offsets[:-1], offsets[1:])]
        invariants = np.stack([r[0] for r in features])
        coefficients = np.stack([r[1] for r in features])
        count = len(features)
        metadata = np.zeros((count, 6), dtype=float)
        metadata[:, 0] = 1
        metadata[:, 1] = inputs['frame_index']
        metadata[:, 2] = inputs['raw_time_h']
        metadata[:, 3] = inputs['time_h']
        metadata[:, 4:6] = inputs['centroid_xy_um']
        motion = derive_motion(metadata, invariants)
        checks = dict(
            invariants=compare(invariants, expected['fourier_invariants'], '60 Fourier invariants', 1e-6, 1e-5),
            coefficients=compare(coefficients, expected['raw_fourier_coefficients'], '33 complex Fourier coefficients', 1e-6, 1e-6),
            motion=compare(motion, expected['motion'], 'Seven motion features', 1e-5, 5e-6))
        args.out.parent.mkdir(parents=True, exist_ok=True)
        output_name = item['sample_id'] + '_native_recomputed.npz'
        np.savez_compressed(args.out.parent/output_name, fourier_invariants=invariants,
                            raw_fourier_coefficients=coefficients, motion=motion,
                            scale=np.asarray([r[2] for r in features]),
                            perimeter=np.asarray([r[3] for r in features]),
                            sampled=np.stack([r[4] for r in features]), feature_names=np.asarray(feature_names()))
        records.append(dict(sample_id=item['sample_id'], n_frames=count, checks=checks,
                            inputs_sha256=sha(inp_path), expected_sha256=sha(exp_path),
                            native_output=output_name, passed=True))
    result = dict(passed=True, core_version=__version__, python=sys.version,
                  platform=platform.platform(), numpy_version=np.__version__,
                  native_extension_filename=native.name, native_sha256=sha(native),
                  samples=records,
                  scope='Native Fourier/motion reproduction on two real 16-frame sequences; no ACA/atlas/refitting or raw segmentation claim.')
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
