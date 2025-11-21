"""
Pixel <-> Centimeter conversion helpers.

This module contains small utilities to compute scale (cm per pixel) from a
reference measurement (for example: known person height) and to convert the
measurements produced by `measurements.compute_body_measurements_px` into cm.

Functions are intentionally pure and contain no I/O.
"""
from typing import Dict, Optional


def compute_cm_per_pixel_from_reference(reference_px: float, reference_cm: float) -> float:
    """Compute cm_per_pixel (centimeters represented by one pixel).

    Args:
      reference_px: length measured in pixels
      reference_cm: the same length in centimeters (real-world)

    Returns:
      cm_per_px (float). Raises ValueError for invalid inputs.
    """
    if reference_px <= 0:
        raise ValueError("reference_px must be > 0")
    if reference_cm <= 0:
        raise ValueError("reference_cm must be > 0")
    return float(reference_cm) / float(reference_px)


def compute_pixels_per_cm_from_reference(reference_px: float, reference_cm: float) -> float:
    """Inverse of compute_cm_per_pixel_from_reference: pixels per cm."""
    cm_per_px = compute_cm_per_pixel_from_reference(reference_px, reference_cm)
    return 1.0 / cm_per_px


def convert_measurements_px_to_cm(measurements_px: Dict[str, float], cm_per_px: float) -> Dict[str, float]:
    """Convert a dictionary of pixel measurements to centimeters.

    The function returns a new dict where keys ending with '_px' are converted
    to corresponding keys ending with '_cm'. Other keys are ignored.

    Example: {'leg_length_px': 500} -> {'leg_length_cm': 500 * cm_per_px}
    """
    out: Dict[str, float] = {}
    for k, v in measurements_px.items():
        if v is None:
            continue
        if not k.endswith('_px'):
            continue
        base = k[:-3]
        out[f"{base}_cm"] = float(v) * float(cm_per_px)
    return out


def derive_scale_from_measurements(measurements_px: Dict[str, float], known_value_cm: float, key_px: str = 'height_px') -> Optional[float]:
    """Derive cm_per_px from measurements if a known measurement is available.

    Args:
      measurements_px: dict of pixel measurements (as returned by compute_body_measurements_px)
      known_value_cm: the real-world size in cm for the provided key
      key_px: which measurement to use (default 'height_px')

    Returns cm_per_px or None if key not found or invalid.
    """
    val_px = measurements_px.get(key_px)
    if val_px is None or val_px <= 0:
        return None
    return compute_cm_per_pixel_from_reference(val_px, known_value_cm)


if __name__ == '__main__':
    # tiny demo
    cm_per_px = compute_cm_per_pixel_from_reference(800.0, 170.0)  # e.g., 800 px = 170 cm
    print('cm_per_px=', cm_per_px)
    print(convert_measurements_px_to_cm({'leg_length_px': 400}, cm_per_px))
