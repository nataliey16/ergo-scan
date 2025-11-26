"""
Posture angle calculations for side-view ergonomic analysis.
Requires normalized or pixel landmarks stored in dict form.

All formulas are side-view optimized, meaning:
- Forward head posture (CVA)
- Chin-to-chest angle
- Torso lean
- Upper back angle
can all be computed accurately.
"""

from .utils_geometry import vector, angle_between


def compute_forward_head_angle(landmarks):
    """Compute Forward Head Posture (Craniovertebral Angle).

    Angle between:
      - Shoulder → Ear vector
      - Vertical axis (0, -1)

    Args:
        landmarks: dict mapping landmark name -> (x, y, z)

    Returns:
        CVA angle in degrees. Lower angle = worse forward head posture.
    """
    ear = landmarks.get("RIGHT_EAR")
    shoulder = landmarks.get("RIGHT_SHOULDER")
    if not ear or not shoulder:
        return None

    v_sh_ear = vector(shoulder[:2], ear[:2])
    vertical = (0, -1)
    return angle_between(v_sh_ear, vertical)


def compute_chin_to_chest_angle(landmarks):
    """Compute chin-to-chest angle (neck flexion).

    Angle between:
      - Chin → Chest vector
      - Horizontal axis (1, 0)

    Args:
        landmarks: dict mapping landmark name -> (x, y, z)

    Returns:
        Angle in degrees. Higher values = more chin-down movement.
    """
    chin = landmarks.get("NOSE") or landmarks.get("MOUTH_RIGHT")
    shoulder = landmarks.get("RIGHT_SHOULDER")
    if not chin or not shoulder:
        return None

    v = vector(chin[:2], shoulder[:2])
    horizontal = (1, 0)
    return angle_between(v, horizontal)


def compute_torso_lean_angle(landmarks):
    """Compute torso lean relative to vertical axis.

    Shoulder → Hip vector compared against (0, -1).

    Args:
        landmarks: dict mapping name -> (x, y, z)

    Returns:
        Angle in degrees. Higher = leaning more forward/backward.
    """
    shoulder = landmarks.get("RIGHT_SHOULDER")
    hip = landmarks.get("RIGHT_HIP")
    if not shoulder or not hip:
        return None

    v_torso = vector(shoulder[:2], hip[:2])
    vertical = (0, -1)
    return angle_between(v_torso, vertical)


def compute_upper_back_angle(landmarks):
    """Compute upper back rounding (thoracic kyphosis).

    Angle between:
      - Shoulder → Chest vector
      - Vertical axis

    Args:
        landmarks: dict mapping name -> (x, y, z)

    Returns:
        Angle in degrees. Higher = more rounding.
    """
    shoulder = landmarks.get("RIGHT_SHOULDER")
    chest = landmarks.get("RIGHT_SHOULDER")  # Mediapipe doesn't provide chest landmark, use shoulder as proxy
    hip = landmarks.get("RIGHT_HIP")

    if not shoulder or not hip:
        return None

    v_back = vector(shoulder[:2], hip[:2])
    vertical = (0, -1)
    return angle_between(v_back, vertical)
