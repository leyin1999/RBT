# RBT Navigation architecture v2

Purpose: 3D Slicer rabbit brain atlas navigation, non-executable candidate markings, Mercury A1 read-only telemetry, Gemini 215 read-only RGB-D and offline validation.

Stages: (1) Slicer MRI/atlas UI, (2) Webots and robot telemetry, (3) hand-eye camera calibration, (4) ANTs atlas-to-individual MRI and physical registration, (5) integrated simulation, (6) inert phantom sensing studies.

Modules: apps/slicer_extension/RBTNavigation (UI), src/rbt/atlas (labels), registration (ANTs), coordinates (frames), planning (candidate annotations), robot (read-only), camera (read-only), simulation (virtual motion), sensing (inert experiments). Existing calibration.py, safety.py, geometry.py, vision.py, app.py and devices/mock.py remain intact for backward compatibility.

No Slicer UI action can command a real drill or injection. Keep atlas, individual MRI, fixture, robot, camera and tool frames distinct, explicitly identifying units, transform direction, timestamp and uncertainty.
