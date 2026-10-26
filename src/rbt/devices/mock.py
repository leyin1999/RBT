import numpy as np
from rbt.contracts import Frame, RobotState


class MockCamera:
    def __init__(self):
        self.sequence = 0

    def capture(self, now):
        self.sequence += 1
        return Frame(self.sequence, now, 0.5, (320, 240), (500, 500, 320, 240))


class MockRobot:
    def read_state(self, now):
        T = np.eye(4)
        T[:3, 3] = [0.1, 0.2, 0.3]
        return RobotState(now, (0.0,) * 7, T)
