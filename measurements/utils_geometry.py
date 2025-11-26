"""
Utility geometry functions shared across measurement modules.
Provides angle and vector operations for posture analysis.

All functions expect 2D tuples (x, y) as input.
"""

import math
from typing import Tuple


def angle_between(v1: Tuple[float, float], v2: Tuple[float, float]) -> float:
    """Compute the angle (in degrees) between two 2D vectors.

    Args:
        v1: tuple (x1, y1) – first vector.
        v2: tuple (x2, y2) – second vector.

    Returns:
        Angle in degrees between vectors v1 and v2.
        Returns 0.0 if vectors are invalid or zero-length.
    """
    x1, y1 = float(v1[0]), float(v1[1])
    x2, y2 = float(v2[0]), float(v2[1])

    dot = x1 * x2 + y1 * y2
    mag1 = math.sqrt(x1 * x1 + y1 * y1)
    mag2 = math.sqrt(x2 * x2 + y2 * y2)

    if mag1 == 0 or mag2 == 0:
        return 0.0

    cos_angle = max(min(dot / (mag1 * mag2), 1.0), -1.0)
    return math.degrees(math.acos(cos_angle))


def vector(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float]:
    """Create a vector from p1 → p2 in 2D.

    Args:
        p1: tuple (x, y)
        p2: tuple (x, y)

    Returns:
        Tuple (dx, dy) representing vector p1→p2.
    """
    return (float(p2[0]) - float(p1[0]), float(p2[1]) - float(p1[1]))


if __name__ == '__main__':
    # Quick test
    v1 = (1.0, 0.0)
    v2 = (0.0, 1.0)
    print(f"Angle between {v1} and {v2}: {angle_between(v1, v2)} degrees")
    
    p1 = (0.0, 0.0)
    p2 = (3.0, 4.0)
    v = vector(p1, p2)
    print(f"Vector from {p1} to {p2}: {v}")
