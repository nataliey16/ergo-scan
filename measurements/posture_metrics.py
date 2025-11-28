"""
Posture angle calculations for side-view ergonomic analysis.
Requires pixel-space landmarks stored as dict mapping name -> (x, y, z) tuples.

All formulas are side-view optimized for:
- Forward head posture (CVA)
- Chin-to-chest angle
- Torso lean
- Upper back angle
"""

from typing import Dict, Optional, Tuple
from .utils_geometry import vector, angle_between

Coord3D = Tuple[float, float, float]


def _get_2d(landmark: Optional[Coord3D]) -> Optional[Tuple[float, float]]:
    """Extract 2D (x, y) from 3D coordinate."""
    if not landmark or len(landmark) < 2:
        return None
    return (landmark[0], landmark[1])


def compute_forward_head_angle(landmarks: Dict[str, Coord3D]) -> Optional[float]:
    """Compute Forward Head Posture (Craniovertebral Angle).

    Angle between:
      - Shoulder → Ear vector
      - Vertical axis (0, -1)

    Args:
        landmarks: dict mapping landmark name -> (x, y, z)

    Returns:
        CVA angle in degrees. Lower angle = worse forward head posture.
    """
    ear = _get_2d(landmarks.get("right_ear") or landmarks.get("RIGHT_EAR"))
    shoulder = _get_2d(landmarks.get("right_shoulder") or landmarks.get("RIGHT_SHOULDER"))
    if not ear or not shoulder:
        return None

    v_sh_ear = vector(shoulder, ear)
    vertical = (0, -1)
    return angle_between(v_sh_ear, vertical)


def compute_chin_to_chest_angle(landmarks: Dict[str, Coord3D]) -> Optional[float]:
    """Compute chin-to-chest angle (neck flexion).

    Angle between:
      - Nose → Shoulder vector (as chin proxy)
      - Horizontal axis (1, 0)

    Args:
        landmarks: dict mapping landmark name -> (x, y, z)

    Returns:
        Angle in degrees. Higher values = more chin-down movement.
    """
    chin = _get_2d(landmarks.get("nose") or landmarks.get("NOSE"))
    shoulder = _get_2d(landmarks.get("right_shoulder") or landmarks.get("RIGHT_SHOULDER"))
    if not chin or not shoulder:
        return None

    v = vector(chin, shoulder)
    horizontal = (1, 0)
    return angle_between(v, horizontal)


def compute_torso_lean_angle(landmarks: Dict[str, Coord3D]) -> Optional[float]:
    """Compute torso lean relative to vertical axis.

    Shoulder → Hip vector compared against (0, -1).

    Args:
        landmarks: dict mapping name -> (x, y, z)

    Returns:
        Angle in degrees. Higher = leaning more forward/backward.
    """
    shoulder = _get_2d(landmarks.get("right_shoulder") or landmarks.get("RIGHT_SHOULDER"))
    hip = _get_2d(landmarks.get("right_hip") or landmarks.get("RIGHT_HIP"))
    if not shoulder or not hip:
        return None

    v_torso = vector(shoulder, hip)
    vertical = (0, -1)
    return angle_between(v_torso, vertical)


def compute_upper_back_angle(landmarks: Dict[str, Coord3D]) -> Optional[float]:
    """Compute upper back rounding (thoracic kyphosis).

    Angle between:
      - Shoulder → Hip vector (proxy for back curvature)
      - Vertical axis

    Args:
        landmarks: dict mapping name -> (x, y, z)

    Returns:
        Angle in degrees. Higher = more rounding.
    """
    shoulder = _get_2d(landmarks.get("right_shoulder") or landmarks.get("RIGHT_SHOULDER"))
    hip = _get_2d(landmarks.get("right_hip") or landmarks.get("RIGHT_HIP"))

    if not shoulder or not hip:
        return None

    v_back = vector(shoulder, hip)
    vertical = (0, -1)
    return angle_between(v_back, vertical)
