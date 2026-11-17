# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
"""Version 0.1.0rc2: thin interface to the compiled study-owned feature core."""
import numpy as np
from . import _native
__version__='0.1.0rc2'
MOTION_COLUMNS=['dx_um','dy_um','speed_um_h','signed_acceleration_um_h2','turn_cos','turn_sin','invariant_vector_change_L2_per_h']
def describe(xy,order=16,n=256):
    """Cartesian contour coordinates: image y must be negated; units are um."""
    r=_native.describe(np.asarray(xy,dtype=float).reshape(-1,2).tolist(),order,n)
    return np.asarray(r['invariants'],dtype=np.float32),np.asarray(r['raw_coefficients'],dtype=np.complex64),r['scale'],r['perimeter'],np.asarray(r['sampled'])
def feature_names(order=16):
    return ([f'fd_amp_pos_{k:02d}' for k in range(1,order+1)]+[f'fd_amp_neg_{k:02d}' for k in range(1,order+1)]+[f'fd_phase_real_{k:02d}' for k in range(3,order+1)]+[f'fd_phase_imag_{k:02d}' for k in range(3,order+1)])
def derive_motion(metadata,invariants):
    """Metadata starts track_id,frame,raw_time_h,elapsed_h,x_um,y_um; sorted rows."""
    return np.asarray(_native.motion(np.asarray(metadata).tolist(),np.asarray(invariants).tolist()),dtype=np.float32).reshape(-1,7)

