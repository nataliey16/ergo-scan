"""
Body segment length calculations for posture measurement.
Uses 2D normalized or pixel-space coordinates.
"""

import math


def distance(p1, p2):
    """Compute Euclidean distance between two 2D points.

    Args:
        p1: tuple (x, y)
        p2: tuple (x, y)

    Returns:
        Float distance between p1 and p2.
    """
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def neck_length(landmarks):
    """Compute neck length as distance between ear and shoulder.

    Args:
        landmarks: dict mapping name -> (x, y, z)

    Returns:
        Neck length in same units as input (normalized or pixels).
    """
    ear = landmarks.get("RIGHT_EAR")
    shoulder = landmarks.get("RIGHT_SHOULDER")
    if not ear or not shoulder:
        return None
    return distance(ear[:2], shoulder[:2])


def torso_length(landmarks):
    """Compute torso length as shoulder→hip distance.

    Args:
        landmarks: dict mapping name -> (x, y, z)

    Returns:
        Torso length in same units as input.
    """
    shoulder = landmarks.get("RIGHT_SHOULDER")
    hip = landmarks.get("RIGHT_HIP")
    if not shoulder or not hip:
        return None
    return distance(shoulder[:2], hip[:2])


def upper_leg_length(landmarks):
    """Compute upper leg length as hip→knee distance."""
    hip = landmarks.get("RIGHT_HIP")
    knee = landmarks.get("RIGHT_KNEE")
    if not hip or not knee:
        return None
    return distance(hip[:2], knee[:2])


def lower_leg_length(landmarks):
    """Compute lower leg length as knee→ankle distance."""
    knee = landmarks.get("RIGHT_KNEE")
    ankle = landmarks.get("RIGHT_ANKLE")
    if not knee or not ankle:
        return None
    return distance(knee[:2], ankle[:2])
