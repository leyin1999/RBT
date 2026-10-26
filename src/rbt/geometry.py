import numpy as np


def validate_transform(T):
    T = np.asarray(T, dtype=float)
    if T.shape != (4, 4) or not np.isfinite(T).all():
        raise ValueError("invalid transform shape/nonfinite")
    R = T[:3, :3]
    if not (np.allclose(T[3], [0, 0, 0, 1], atol=1e-8)
            and np.allclose(R.T @ R, np.eye(3), atol=1e-8)
            and np.isclose(np.linalg.det(R), 1, atol=1e-8)):
        raise ValueError("not a rigid transform")
    return T


def transform_point(T, p):
    T = validate_transform(T)
    p = np.asarray(p, dtype=float)
    if p.shape != (3,) or not np.isfinite(p).all():
        raise ValueError("invalid point")
    return (T @ np.r_[p, 1])[:3]
