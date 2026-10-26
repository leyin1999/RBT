import numpy as np
from rbt.geometry import validate_transform


class Interlock:
    """Software validation latch; never a substitute for hardware emergency stop."""
    def __init__(self, config):
        self.config = config
        self.fault = None

    def check(self, frame, robot, point_B, now):
        if self.fault:
            return False, self.fault
        try:
            if not robot.connected:
                raise ValueError("robot_disconnected")
            if not frame.valid:
                raise ValueError("camera_invalid")
            for stamp in (frame.captured_s, robot.captured_s):
                if not np.isfinite(stamp) or not 0 <= now - stamp <= self.config['max_age_s']:
                    raise ValueError("stale_or_future_sample")
            if abs(frame.captured_s - robot.captured_s) > self.config['max_skew_s']:
                raise ValueError("unsynchronized_samples")
            if len(robot.joints_rad) != 7 or not np.isfinite(robot.joints_rad).all():
                raise ValueError("invalid_joints")
            validate_transform(robot.T_B_E)
            p = np.asarray(point_B)
            if p.shape != (3,) or not np.isfinite(p).all():
                raise ValueError("invalid_target")
            if not ((p >= self.config['workspace_min_m']).all()
                    and (p <= self.config['workspace_max_m']).all()):
                raise ValueError("outside_synthetic_workspace")
        except (ValueError, TypeError) as exc:
            self.fault = str(exc)
            return False, self.fault
        return True, "accepted_for_preview"

    def trip(self, reason):
        self.fault = reason

    def reset(self, *, operator_ack=False):
        if not operator_ack:
            raise ValueError("operator acknowledgement required")
        self.fault = None  # Next sample still must pass every check.
