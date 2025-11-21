import math
from datetime import datetime, timezone

# Use the converter you already have
from test_converter import convert_mediapipe_coords

# Storage helpers
from calibration.storage import save_calibration_json

# Example: frame and scale settings
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
PX_PER_CM = 37.8  # pixels per cm (example). cm_per_pixel = 1 / PX_PER_CM

def euclidean(px_a, px_b):
    dx = px_a[0] - px_b[0]
    dy = px_a[1] - px_b[1]
    dz = px_a[2] - px_b[2]
    return math.sqrt(dx*dx + dy*dy + dz*dz)

def build_payload_from_mediapipe(landmarks_norm, pose_type="t_pose"):
    """
    landmarks_norm: list of dicts {name, x, y, z, visibility}
      - x,y,z are normalized (0..1), visibility 0..1
    Returns a payload matching calibration_schema + storage validator expectations.
    """
    # raw_landmarks: keep normalized inputs
    raw_landmarks = {
        "frame_count": 1,
        "landmarks": [
            {"name": lm["name"], "x": lm["x"], "y": lm["y"], "z": lm.get("z", 0.0), "visibility": lm.get("visibility", 1.0)}
            for lm in landmarks_norm
        ]
    }

    # Build normalized block (same as raw here)
    normalized = {
        "landmarks_normalized": [
            {"name": lm["name"], "x": lm["x"], "y": lm["y"], "z": lm.get("z", 0.0)}
            for lm in landmarks_norm
        ]
    }

    # Convert key landmarks to pixels/centimeters using convert_mediapipe_coords
    converted = {}
    for lm in landmarks_norm:
        c = convert_mediapipe_coords(lm["name"], lm["x"], lm["y"], lm.get("z", 0.0),
                                     FRAME_WIDTH, FRAME_HEIGHT, scale_px_per_cm=PX_PER_CM)
        converted[lm["name"]] = c

    # Simple pixel_height estimate: vertical span of landmarks in pixels
    ys = [lm["y"] for lm in landmarks_norm]
    pixel_height = int((max(ys) - min(ys)) * FRAME_HEIGHT) if ys else FRAME_HEIGHT

    # cm per pixel
    scale_factor_cm_per_pixel = 1.0 / PX_PER_CM

    # Compute torso length (example): distance between left_shoulder and left_hip if available
    torso_px = None
    torso_cm = None
    if "left_shoulder" in converted and "left_hip" in converted:
        dist_px = euclidean(converted["left_shoulder"]["pixels"], converted["left_hip"]["pixels"])
        torso_px = round(dist_px, 2)
        torso_cm = round(dist_px * scale_factor_cm_per_pixel, 3)

    # Also compute leg_length as example (right_hip to right_ankle if available)
    leg_px = None
    leg_cm = None
    if "right_hip" in converted and "right_ankle" in converted:
        dist_px = euclidean(converted["right_hip"]["pixels"], converted["right_ankle"]["pixels"])
        leg_px = round(dist_px, 2)
        leg_cm = round(dist_px * scale_factor_cm_per_pixel, 3)

    measurements = {
        "pixel_height": pixel_height,
        "scale_factor_cm_per_pixel": scale_factor_cm_per_pixel,
        # example placeholders or computed values
        "shoulder_width_px": converted.get("shoulder_width", {}).get("pixels", (None, None, None))[0] if "shoulder_width" in converted else None,
        "shoulder_width_cm": None,
        "arm_length_px": None,
        "arm_length_cm": None,
        "leg_length_px": leg_px,
        "leg_length_cm": leg_cm,
        "torso_length_px": torso_px,
        "torso_length_cm": torso_cm,
        "baseline_angles": {"neck_deg": 0.0, "spine_deg": 0.0}
    }

    camera_meta = {
        "resolution": [FRAME_WIDTH, FRAME_HEIGHT],
        "camera_distance_estimate_cm": 100.0
    }

    payload = {
        "version": "1.0",
        "user_id": None,
        "pose_type": pose_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw_landmarks": raw_landmarks,
        "measurements": measurements,
        "normalized": normalized,
        "camera_meta": camera_meta
    }

    return payload

if __name__ == "__main__":
    # Example normalized landmarks set (MediaPipe-like). Add more landmarks as needed.
    sample_landmarks = [
        {"name": "left_shoulder", "x": 0.34, "y": 0.45, "z": -0.02, "visibility": 0.98},
        {"name": "right_shoulder", "x": 0.66, "y": 0.45, "z": -0.02, "visibility": 0.97},
        {"name": "left_hip", "x": 0.40, "y": 0.70, "z": 0.01, "visibility": 0.95},
        {"name": "right_hip", "x": 0.60, "y": 0.70, "z": 0.01, "visibility": 0.95},
        {"name": "right_ankle", "x": 0.60, "y": 0.98, "z": 0.0, "visibility": 0.9}
    ]

    payload = build_payload_from_mediapipe(sample_landmarks, pose_type="standing")

    # Save using storage.save_calibration_json (will validate with validate_calibration_data)
    out_path = save_calibration_json(payload, folder="calibration/samples", overwrite=True)
    print(f"Saved calibration payload to: {out_path}")