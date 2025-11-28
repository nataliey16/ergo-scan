"""
Normalized landmark to pixel coordinate conversion.
Handles both list-of-dicts and dict-of-tuples input formats.
"""
from typing import Dict, List, Optional, Tuple, Union

Landmark = Dict[str, float]
Coord3D = Tuple[float, float, float]


def normalized_to_pixels(
    landmarks: Union[List[Landmark], Dict[str, Coord3D]],
    image_size: Optional[Tuple[int, int]] = None
) -> Dict[str, Coord3D]:
    """Convert normalized landmarks (0..1) to pixel coordinates.

    Args:
        landmarks: either a list of landmark dicts with keys 'name','x','y','z',
                   or a dict mapping landmark_name -> (x, y, z) tuple.
        image_size: tuple (width, height). If None, returns original values.

    Returns:
        dict mapping landmark name -> (x_px, y_px, z)
    """
    result: Dict[str, Coord3D] = {}

    # Handle list of dicts (from normalized output)
    if isinstance(landmarks, list):
        for lm in landmarks:
            name = lm.get("name")
            x = lm.get("x")
            y = lm.get("y")
            z = lm.get("z", 0.0)

            if x is None or y is None or name is None:
                continue

            if image_size is None:
                result[name] = (float(x), float(y), float(z))
            else:
                w, h = image_size
                result[name] = (float(x) * w, float(y) * h, float(z))

    # Handle dict of tuples (already normalized as dict)
    elif isinstance(landmarks, dict):
        for name, coord in landmarks.items():
            if not coord or len(coord) < 2:
                continue
            x, y = coord[0], coord[1]
            z = coord[2] if len(coord) > 2 else 0.0

            if image_size is None:
                result[name] = (float(x), float(y), float(z))
            else:
                w, h = image_size
                result[name] = (float(x) * w, float(y) * h, float(z))

    return result


def convert_normalized_to_pixel(
    landmarks: Union[List[Landmark], Dict[str, Coord3D]],
    image_size: Tuple[int, int]
) -> Dict[str, Coord3D]:
    """Alias for normalized_to_pixels with required image_size."""
    if not image_size:
        raise ValueError("image_size (width, height) is required")
    return normalized_to_pixels(landmarks, image_size)
