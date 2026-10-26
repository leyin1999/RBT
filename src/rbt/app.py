import argparse
from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from uuid import uuid4
import numpy as np
from rbt.devices.mock import MockCamera, MockRobot
from rbt.calibration import synthetic_T_E_C
from rbt.geometry import transform_point
from rbt.vision import backproject
from rbt.safety import Interlock
from rbt.recording import append_event, replay


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', default='config/sim.json')
    parser.add_argument('--fault', choices=['none', 'camera', 'stale', 'disconnect', 'bounds'], default='none')
    parser.add_argument('--output', default='data/runs')
    parser.add_argument('--replay')
    args = parser.parse_args()
    if args.replay:
        for event in replay(args.replay):
            print(json.dumps(event, ensure_ascii=False))
        return 0
    config = json.loads(Path(args.config).read_text(encoding='utf-8'))
    if config['backend'] != 'mock':
        raise ValueError('Only mock backend implemented; no hardware commands available')
    camera, robot = MockCamera(), MockRobot()
    gate = Interlock(config)
    run = Path(args.output) / uuid4().hex
    run.mkdir(parents=True)
    (run / 'config.json').write_text(json.dumps(config, indent=2), encoding='utf-8')
    now = time.monotonic()
    frame, state = camera.capture(now), robot.read_state(now)
    if args.fault == 'camera':
        frame = replace(frame, valid=False)
    elif args.fault == 'stale':
        frame = replace(frame, captured_s=now - 1)
    elif args.fault == 'disconnect':
        state = replace(state, connected=False)
    T_E_C = synthetic_T_E_C()
    point = None
    try:
        point = transform_point(state.T_B_E @ T_E_C, backproject(frame))
        if args.fault == 'bounds':
            point = np.array([9.0, 0, 0])
        ok, reason = gate.check(frame, state, point, now)
    except ValueError as exc:
        gate.trip(str(exc))
        ok, reason = False, gate.fault
    event = {
        'schema_version': 1, 'backend': 'mock', 'synthetic': True,
        'utc': datetime.now(timezone.utc).isoformat(), 'sequence': frame.sequence,
        'camera_time_s': frame.captured_s, 'robot_time_s': state.captured_s,
        'joints_rad': state.joints_rad, 'T_B_E': state.T_B_E.tolist(),
        'T_E_C': T_E_C.tolist(), 'calibration_id': 'synthetic-fixture-v1',
        'point_B_m': point.tolist() if point is not None else None,
        'decision': 'preview' if ok else 'blocked', 'reason': reason,
        'motion_sent': False,
    }
    append_event(run / 'events.jsonl', event)
    print(json.dumps(event, ensure_ascii=False))
    print(f'Log: {run / "events.jsonl"}')
    return 0 if ok else 2


if __name__ == '__main__':
    raise SystemExit(main())
