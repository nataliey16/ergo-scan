"""
Body segment length calculations for posture measurement.
Uses 2D pixel-space coordinates extracted from normalized landmarks.

Accepts landmarks as dict mapping name -> (x, y, z) tuples.
"""

import math
from typing import Dict, Optional, Tuple

Coord3D = Tuple[float, float, float]


def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Compute Euclidean distance between two 2D points.

    Args:
        p1: tuple (x, y)
        p2: tuple (x, y)

    Returns:
        Float distance between p1 and p2.
    """
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def _get_2d(landmark: Optional[Coord3D]) -> Optional[Tuple[float, float]]:
    """Extract 2D (x, y) from 3D coordinate, handling None."""
    if not landmark or len(landmark) < 2:
        return None
    return (landmark[0], landmark[1])


def neck_length(landmarks: Dict[str, Coord3D]) -> Optional[float]:
    """Compute neck length as distance between ear and shoulder.

    Args:
        landmarks: dict mapping name -> (x, y, z)

    Returns:
        Neck length in same units as input (pixels), or None if missing.
    """
    ear = _get_2d(landmarks.get("right_ear") or landmarks.get("RIGHT_EAR"))
    shoulder = _get_2d(landmarks.get("right_shoulder") or landmarks.get("RIGHT_SHOULDER"))
    if not ear or not shoulder:
        return None
    return distance(ear, shoulder)


def torso_length(landmarks: Dict[str, Coord3D]) -> Optional[float]:
    """Compute torso length as shoulder→hip distance (right side).

    Args:
        landmarks: dict mapping name -> (x, y, z)

    Returns:
        Torso length in same units as input (pixels), or None if missing.
    """
    shoulder = _get_2d(landmarks.get("right_shoulder") or landmarks.get("RIGHT_SHOULDER"))
    hip = _get_2d(landmarks.get("right_hip") or landmarks.get("RIGHT_HIP"))
    if not shoulder or not hip:
        return None
    return distance(shoulder, hip)


def upper_leg_length(landmarks: Dict[str, Coord3D]) -> Optional[float]:
    """Compute upper leg length as hip→knee distance (right side)."""
    hip = _get_2d(landmarks.get("right_hip") or landmarks.get("RIGHT_HIP"))
    knee = _get_2d(landmarks.get("right_knee") or landmarks.get("RIGHT_KNEE"))
    if not hip or not knee:
        return None
    return distance(hip, knee)


def lower_leg_length(landmarks: Dict[str, Coord3D]) -> Optional[float]:
    """Compute lower leg length as knee→ankle distance (right side)."""
    knee = _get_2d(landmarks.get("right_knee") or landmarks.get("RIGHT_KNEE"))
    ankle = _get_2d(landmarks.get("right_ankle") or landmarks.get("RIGHT_ANKLE"))
    if not knee or not ankle:
        return None
    return distance(knee, ankle)


def full_leg_length(landmarks: Dict[str, Coord3D]) -> Optional[float]:
    """Compute full leg length as hip→ankle distance (right side)."""
    hip = _get_2d(landmarks.get("right_hip") or landmarks.get("RIGHT_HIP"))
    ankle = _get_2d(landmarks.get("right_ankle") or landmarks.get("RIGHT_ANKLE"))
    if not hip or not ankle:
        return None
    return distance(hip, ankle)


def shoulder_width(landmarks: Dict[str, Coord3D]) -> Optional[float]:
    """Compute shoulder width as distance between left and right shoulders."""
    left_shoulder = _get_2d(landmarks.get("left_shoulder") or landmarks.get("LEFT_SHOULDER"))
    right_shoulder = _get_2d(landmarks.get("right_shoulder") or landmarks.get("RIGHT_SHOULDER"))
    if not left_shoulder or not right_shoulder:
        return None
    return distance(left_shoulder, right_shoulder)


def hip_width(landmarks: Dict[str, Coord3D]) -> Optional[float]:
    """Compute hip width as distance between left and right hips."""
    left_hip = _get_2d(landmarks.get("left_hip") or landmarks.get("LEFT_HIP"))
    right_hip = _get_2d(landmarks.get("right_hip") or landmarks.get("RIGHT_HIP"))
    if not left_hip or not right_hip:
        return None
    return distance(left_hip, right_hip)
