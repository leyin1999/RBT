from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from rbt.devices.mock import MockCamera, MockRobot
from rbt.geometry import transform_point, validate_transform
from rbt.calibration import synthetic_T_E_C
from rbt.vision import backproject
from rbt.safety import Interlock
from rbt.recording import append_event, replay


class OfflineTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.config = json.loads((root / 'config/sim.json').read_text())
        self.frame = MockCamera().capture(10.0)
        self.robot = MockRobot().read_state(10.0)
        self.point = np.array([0.12, 0.2, 0.85])

    def test_known_coordinate_chain(self):
        result = transform_point(self.robot.T_B_E @ synthetic_T_E_C(), backproject(self.frame))
        np.testing.assert_allclose(result, self.point, atol=1e-12)

    def test_rotation_and_inverse(self):
        T = np.array([[0, -1, 0, 1], [1, 0, 0, 2], [0, 0, 1, 3], [0, 0, 0, 1]])
        np.testing.assert_allclose(transform_point(T, [1, 0, 0]), [1, 3, 3])
        np.testing.assert_allclose(transform_point(np.linalg.inv(T), [1, 3, 3]), [1, 0, 0])

    def test_reject_reflection(self):
        T = np.eye(4)
        T[0, 0] = -1
        with self.assertRaises(ValueError):
            validate_transform(T)

    def test_bad_depth(self):
        for depth in (0, -1, float('nan')):
            with self.subTest(depth=depth), self.assertRaises(ValueError):
                backproject(replace(self.frame, depth_m=depth))

    def test_interlocks(self):
        cases = [
            (replace(self.frame, valid=False), self.robot, self.point),
            (replace(self.frame, captured_s=9), self.robot, self.point),
            (replace(self.frame, captured_s=10.1), self.robot, self.point),
            (replace(self.frame, captured_s=9.9), self.robot, self.point),
            (self.frame, replace(self.robot, connected=False), self.point),
            (self.frame, replace(self.robot, joints_rad=(0,) * 6), self.point),
            (self.frame, self.robot, np.array([9, 0, 0])),
            (self.frame, self.robot, np.array([float('nan'), 0, 0])),
        ]
        for frame, robot, point in cases:
            with self.subTest(frame=frame, point=point):
                self.assertFalse(Interlock(self.config).check(frame, robot, point, 10)[0])

    def test_latch_and_acknowledged_reset(self):
        gate = Interlock(self.config)
        gate.trip('camera_timeout')
        self.assertFalse(gate.check(self.frame, self.robot, self.point, 10)[0])
        with self.assertRaises(ValueError):
            gate.reset()
        gate.reset(operator_ack=True)
        self.assertTrue(gate.check(self.frame, self.robot, self.point, 10)[0])

    def test_record_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'events.jsonl'
            event = {'synthetic': True, 'decision': 'blocked', 'motion_sent': False}
            append_event(path, event)
            self.assertEqual(replay(path), [event])


if __name__ == '__main__':
    unittest.main()
