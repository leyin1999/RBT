import math
import numpy as np
from rbt.contracts import Frame


def backproject(frame: Frame):
    """Synthetic aligned, undistorted pinhole sample; outputs camera-frame metres."""
    fx, fy, cx, cy = frame.intrinsics
    u, v = frame.uv
    z = frame.depth_m
    if not frame.valid or not all(map(math.isfinite, (fx, fy, cx, cy, u, v, z))):
        raise ValueError("invalid camera frame")
    if z <= 0 or fx <= 0 or fy <= 0:
        raise ValueError("invalid depth/intrinsics")
    return np.array([(u - cx) * z / fx, (v - cy) * z / fy, z])
