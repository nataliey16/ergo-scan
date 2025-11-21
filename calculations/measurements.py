"""
Utilities to compute body measurements (in pixels) from landmark lists.

Expected input: a list of landmark dicts in the shape:
  [{"name": "nose", "x": 0.5, "y": 0.4, "z": 0.0}, ...]

Landmark coordinates may be normalized (0..1). If so, pass `image_size=(width, height)`
to convert to pixels. If landmarks are already in pixel coordinates, pass `image_size=None`.

This module performs only geometric calculations and returns measurements in pixels.
No file I/O or validation beyond presence checks is performed.
"""
from typing import Dict, List, Optional, Tuple
import math

Landmark = Dict[str, float]


def _landmarks_to_map(landmarks: List[Landmark]) -> Dict[str, Landmark]:
    """Return a mapping from landmark name -> landmark dict.
    Accepts a list of dicts; if a dict mapping is passed, behavior still works (keys ignored).
    """
    out: Dict[str, Landmark] = {}
    for lm in landmarks:
        name = lm.get("name")
        if not name:
            continue
        out[name] = lm
    return out


def landmarks_to_pixels(landmarks: List[Landmark], image_size: Optional[Tuple[int, int]]):
    """Convert normalized landmarks (0..1) to pixel coordinates.

    Args:
      landmarks: list of landmark dicts with keys 'name','x','y','z'
      image_size: tuple (width, height). If None, assumes 'x' and 'y' are already pixels.

    Returns:
      dict mapping landmark name -> (x_px, y_px, z)
    """
    lm_map = _landmarks_to_map(landmarks)
    out: Dict[str, Tuple[float, float, float]] = {}
    if image_size is None:
        # assume coordinates are already in pixels
        for name, lm in lm_map.items():
            out[name] = (float(lm.get("x", 0.0)), float(lm.get("y", 0.0)), float(lm.get("z", 0.0)))
        return out

    width, height = image_size
    for name, lm in lm_map.items():
        x = lm.get("x")
        y = lm.get("y")
        z = lm.get("z", 0.0)
        if x is None or y is None:
            continue
        # normalized coords: multiply by dimension
        px = float(x) * float(width)
        py = float(y) * float(height)
        out[name] = (px, py, float(z))
    return out


def _dist(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def compute_body_measurements_px(landmarks: List[Landmark], image_size: Optional[Tuple[int, int]] = None) -> Dict[str, Optional[float]]:
    """Compute common body measurements (in pixels) from landmarks.

    Measurements returned (keys):
      - height_px
      - shoulder_width_px
      - hip_width_px
      - torso_length_px
      - arm_length_px
      - leg_length_px
      - left_arm_px, right_arm_px, left_leg_px, right_leg_px (component values)

    Missing measurements will be returned as None.

    Args:
      landmarks: list of landmark dicts
      image_size: (width, height) to convert normalized -> pixels; if None, landmarks are assumed pixel coords
    """
    lm_px = landmarks_to_pixels(landmarks, image_size)

    # helper to safely get 2D tuple
    def g(name: str) -> Optional[Tuple[float, float]]:
        v = lm_px.get(name)
        if not v:
            return None
        return (v[0], v[1])

    results: Dict[str, Optional[float]] = {
        'height_px': None,
        'shoulder_width_px': None,
        'hip_width_px': None,
        'torso_length_px': None,
        'arm_length_px': None,
        'leg_length_px': None,
        'left_arm_px': None,
        'right_arm_px': None,
        'left_leg_px': None,
        'right_leg_px': None,
    }

    # Height: nose -> average(ankles) (pixel vertical distance)
    nose = g('nose')
    left_ankle = g('left_ankle')
    right_ankle = g('right_ankle')
    if nose and (left_ankle or right_ankle):
        ankle_y = None
        if left_ankle and right_ankle:
            ankle_y = (left_ankle[1] + right_ankle[1]) / 2.0
        elif left_ankle:
            ankle_y = left_ankle[1]
        else:
            ankle_y = right_ankle[1]
        # use euclidean distance (more robust) between nose and ankle center
        ankle_center = ((left_ankle[0] + right_ankle[0]) / 2.0, ankle_y) if (left_ankle and right_ankle) else (left_ankle or right_ankle)
        results['height_px'] = _dist(nose, ankle_center)

    # Shoulder width
    left_shoulder = g('left_shoulder')
    right_shoulder = g('right_shoulder')
    if left_shoulder and right_shoulder:
        results['shoulder_width_px'] = _dist(left_shoulder, right_shoulder)

    # Hip width
    left_hip = g('left_hip')
    right_hip = g('right_hip')
    if left_hip and right_hip:
        results['hip_width_px'] = _dist(left_hip, right_hip)

    # Torso length: shoulder center -> hip center
    if left_shoulder and right_shoulder and left_hip and right_hip:
        shoulder_center = ((left_shoulder[0] + right_shoulder[0]) / 2.0, (left_shoulder[1] + right_shoulder[1]) / 2.0)
        hip_center = ((left_hip[0] + right_hip[0]) / 2.0, (left_hip[1] + right_hip[1]) / 2.0)
        results['torso_length_px'] = _dist(shoulder_center, hip_center)

    # Arm lengths: shoulder -> elbow -> wrist (sum of segments)
    left_elbow = g('left_elbow')
    right_elbow = g('right_elbow')
    left_wrist = g('left_wrist')
    right_wrist = g('right_wrist')
    if left_shoulder and left_elbow and left_wrist:
        left_arm = _dist(left_shoulder, left_elbow) + _dist(left_elbow, left_wrist)
        results['left_arm_px'] = left_arm
    if right_shoulder and right_elbow and right_wrist:
        right_arm = _dist(right_shoulder, right_elbow) + _dist(right_elbow, right_wrist)
        results['right_arm_px'] = right_arm
    # average
    left_arm_val = results.get('left_arm_px')
    right_arm_val = results.get('right_arm_px')
    if left_arm_val and right_arm_val:
        results['arm_length_px'] = (left_arm_val + right_arm_val) / 2.0
    elif left_arm_val:
        results['arm_length_px'] = left_arm_val
    elif right_arm_val:
        results['arm_length_px'] = right_arm_val

    # Leg lengths: hip -> knee -> ankle
    left_knee = g('left_knee')
    right_knee = g('right_knee')
    if left_hip and left_knee and left_ankle:
        left_leg = _dist(left_hip, left_knee) + _dist(left_knee, left_ankle)
        results['left_leg_px'] = left_leg
    if right_hip and right_knee and right_ankle:
        right_leg = _dist(right_hip, right_knee) + _dist(right_knee, right_ankle)
        results['right_leg_px'] = right_leg
    left_leg_val = results.get('left_leg_px')
    right_leg_val = results.get('right_leg_px')
    if left_leg_val and right_leg_val:
        results['leg_length_px'] = (left_leg_val + right_leg_val) / 2.0
    elif left_leg_val:
        results['leg_length_px'] = left_leg_val
    elif right_leg_val:
        results['leg_length_px'] = right_leg_val

    return results


def example_usage():
    """Small self-check example. Not executed on import.
    Replace the landmarks and image_size with your data.
    """
    sample_landmarks = [
        {"name": "nose", "x": 0.5, "y": 0.1, "z": 0.0},
        {"name": "left_shoulder", "x": 0.4, "y": 0.3, "z": 0.0},
        {"name": "right_shoulder", "x": 0.6, "y": 0.3, "z": 0.0},
        {"name": "left_hip", "x": 0.45, "y": 0.6, "z": 0.0},
        {"name": "right_hip", "x": 0.55, "y": 0.6, "z": 0.0},
        {"name": "left_elbow", "x": 0.35, "y": 0.45, "z": 0.0},
        {"name": "right_elbow", "x": 0.65, "y": 0.45, "z": 0.0},
        {"name": "left_wrist", "x": 0.3, "y": 0.6, "z": 0.0},
        {"name": "right_wrist", "x": 0.7, "y": 0.6, "z": 0.0},
        {"name": "left_knee", "x": 0.45, "y": 0.8, "z": 0.0},
        {"name": "right_knee", "x": 0.55, "y": 0.8, "z": 0.0},
        {"name": "left_ankle", "x": 0.45, "y": 0.95, "z": 0.0},
        {"name": "right_ankle", "x": 0.55, "y": 0.95, "z": 0.0},
    ]
    # Example: 1280x720 image
    results = compute_body_measurements_px(sample_landmarks, image_size=(1280, 720))
    return results


if __name__ == "__main__":
    print(example_usage())
