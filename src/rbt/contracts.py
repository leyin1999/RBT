from dataclasses import dataclass
from typing import Protocol
import numpy as np


@dataclass(frozen=True)
class Frame:
    sequence: int
    captured_s: float  # host monotonic seconds, normalized at adapter boundary
    depth_m: float
    uv: tuple[float, float]
    intrinsics: tuple[float, float, float, float]  # fx, fy, cx, cy
    valid: bool = True


@dataclass(frozen=True)
class RobotState:
    captured_s: float
    joints_rad: tuple[float, ...]  # exactly seven joints
    T_B_E: np.ndarray
    connected: bool = True


class Camera(Protocol):
    def capture(self, now: float) -> Frame: ...


class Robot(Protocol):
    def read_state(self, now: float) -> RobotState: ...

# Deliberately no motion API in phase-one read-only contract.
