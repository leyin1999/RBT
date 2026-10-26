import numpy as np


def synthetic_T_E_C():
    """Known fixture, not an estimated or measured hand-eye calibration."""
    T = np.eye(4)
    T[:3, 3] = [0.02, 0, 0.05]
    return T
