"""
Utility geometry functions shared across measurement modules.
Provides angle calculations and vector operations for posture analysis.
"""

import math


def angle_between(v1, v2):
    """Compute the angle (in degrees) between two 2D vectors.

    Args:
        v1: tuple (x1, y1) – first vector.
        v2: tuple (x2, y2) – second vector.

    Returns:
        Angle in degrees between vectors v1 and v2.
        Returns 0 if vectors are invalid or zero-length.
    """
    x1, y1 = v1
    x2, y2 = v2

    dot = x1 * x2 + y1 * y2
    mag1 = math.sqrt(x1 * x1 + y1 * y1)
    mag2 = math.sqrt(x2 * x2 + y2 * y2)

    if mag1 == 0 or mag2 == 0:
        return 0.0

    cos_angle = max(min(dot / (mag1 * mag2), 1.0), -1.0)
    return math.degrees(math.acos(cos_angle))


def vector(p1, p2):
    """Create a vector from p1 → p2 in 2D.

    Args:
        p1: tuple (x, y)
        p2: tuple (x, y)

    Returns:
        Tuple (dx, dy) representing vector p1→p2.
    """
    return (p2[0] - p1[0], p2[1] - p1[1])
