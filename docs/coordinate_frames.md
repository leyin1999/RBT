# Coordinate contract

Frames: A atlas, I individual MRI, K skull CT, F physical fixture, B robot base, E end-effector, C camera, T inert tool.

T_X_Y maps point coordinates Y -> X. p_X = T_X_Y @ p_Y. T_B_C = T_B_E @ T_E_C.

Distinguish image IJK voxels from RAS/LPS physical coordinates in millimeters and robot/world units. LPS-to-RAS flips X and Y. Preserve transform direction and inversion explicitly. Atlas labels mapped to individual images require nearest-neighbor interpolation and independent landmark validation.

Minimum metadata: source frame, destination frame, units, timestamp, calibration ID, validation status, error metrics.
