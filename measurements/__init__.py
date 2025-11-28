"""
Measurement package for ErgoScan.

Provides:
- Conversion utilities (normalized → pixel coordinates)
- Body segment length calculations (pixel space)
- Posture angle calculations (side-view ergonomic metrics)
- Integrated measurement computation pipeline

Usage:
    from measurements import compute_all_measurements
    
    # Assuming normalized_landmarks is list of dicts: [{"name": "nose", "x": 0.5, "y": 0.4, "z": 0.0}, ...]
    results = compute_all_measurements(
        normalized_landmarks,
        image_size=(1280, 720),
        person_height_cm=170.0
    )
"""

from typing import Dict, List, Optional, Tuple, Union, Any

from .normalized_to_px import (
    normalized_to_pixels,
    convert_normalized_to_pixel,
)
from .segment_lengths import (
    distance,
    neck_length,
    torso_length,
    upper_leg_length,
    lower_leg_length,
    full_leg_length,
    shoulder_width,
    hip_width,
)
from .posture_metrics import (
    compute_forward_head_angle,
    compute_chin_to_chest_angle,
    compute_torso_lean_angle,
    compute_upper_back_angle,
)
from .utils_geometry import angle_between, vector

Coord3D = Tuple[float, float, float]
Landmark = Dict[str, float]


def compute_body_measurements_px(landmarks_px: Dict[str, Coord3D]) -> Dict[str, Optional[float]]:
    """Compute all body segment lengths in pixel space.
    
    Args:
        landmarks_px: dict mapping landmark name -> (x, y, z) in pixels
    
    Returns:
        dict with keys like 'torso_length_px', 'leg_length_px', etc.
    """
    return {
        'neck_length_px': neck_length(landmarks_px),
        'torso_length_px': torso_length(landmarks_px),
        'upper_leg_px': upper_leg_length(landmarks_px),
        'lower_leg_px': lower_leg_length(landmarks_px),
        'full_leg_px': full_leg_length(landmarks_px),
        'shoulder_width_px': shoulder_width(landmarks_px),
        'hip_width_px': hip_width(landmarks_px),
    }


def convert_measurements_px_to_cm(
    measurements_px: Dict[str, Optional[float]],
    scale_factor: Optional[float]
) -> Dict[str, Optional[float]]:
    """Convert pixel measurements to centimeters.
    
    Args:
        measurements_px: dict of measurements with '_px' suffix
        scale_factor: cm per pixel (or None to skip conversion)
    
    Returns:
        dict with '_cm' suffixes replacing '_px'
    """
    if scale_factor is None or scale_factor <= 0:
        return {}
    
    cm_dict = {}
    for key, value in measurements_px.items():
        if value is None:
            continue
        if key.endswith('_px'):
            cm_key = key.replace('_px', '_cm')
            cm_dict[cm_key] = value * scale_factor
    return cm_dict


def compute_posture_angles(landmarks_px: Dict[str, Coord3D]) -> Dict[str, Optional[float]]:
    """Compute all posture-related angles.
    
    Args:
        landmarks_px: dict mapping landmark name -> (x, y, z) in pixels
    
    Returns:
        dict with angle measurements
    """
    return {
        'forward_head_angle_deg': compute_forward_head_angle(landmarks_px),
        'chin_to_chest_angle_deg': compute_chin_to_chest_angle(landmarks_px),
        'torso_lean_angle_deg': compute_torso_lean_angle(landmarks_px),
        'upper_back_angle_deg': compute_upper_back_angle(landmarks_px),
    }


def compute_height_from_landmarks(landmarks_px: Dict[str, Coord3D]) -> Optional[float]:
    """Compute overall height from nose to average ankle position.
    
    Args:
        landmarks_px: dict mapping landmark name -> (x, y, z)
    
    Returns:
        height in pixels, or None if ankles not found
    """
    nose = landmarks_px.get('nose') or landmarks_px.get('NOSE')
    left_ankle = landmarks_px.get('left_ankle') or landmarks_px.get('LEFT_ANKLE')
    right_ankle = landmarks_px.get('right_ankle') or landmarks_px.get('RIGHT_ANKLE')
    
    if not nose:
        return None
    
    if left_ankle and right_ankle:
        ankle_y = (left_ankle[1] + right_ankle[1]) / 2.0
        ankle_x = (left_ankle[0] + right_ankle[0]) / 2.0
    elif left_ankle:
        ankle_x, ankle_y = left_ankle[0], left_ankle[1]
    elif right_ankle:
        ankle_x, ankle_y = right_ankle[0], right_ankle[1]
    else:
        return None
    
    return distance((nose[0], nose[1]), (ankle_x, ankle_y))


def compute_all_measurements(
    normalized_landmarks: Union[List[Landmark], Dict[str, Coord3D]],
    image_size: Tuple[int, int],
    person_height_cm: Optional[float] = None
) -> Dict[str, Any]:
    """
    High-level wrapper that computes all measurements from normalized landmarks.
    
    Pipeline:
      1. Convert normalized landmarks to pixel coordinates
      2. Compute body height in pixels
      3. Calculate scale factor (cm_per_px) if person height known
      4. Compute all segment lengths in pixels
      5. Convert segments to cm
      6. Compute posture angles
    
    Args:
        normalized_landmarks: list of dicts or dict of tuples with normalized coords (0..1)
        image_size: tuple (width, height) of the camera frame
        person_height_cm: optional real-world height in cm (used for scaling)
    
    Returns:
        dict containing:
            - pixel_height: overall height in pixels
            - scale_factor_cm_per_pixel: derived scale factor (or None)
            - pixel_measurements: dict of all segment measurements in pixels
            - cm_measurements: dict of all segment measurements in cm
            - posture_angles: dict of angle measurements
            - debug: info about landmarks used
    """
    if not image_size or len(image_size) != 2:
        raise ValueError("image_size must be a tuple (width, height)")
    
    # (1) Convert to pixel coordinates
    pixel_landmarks = convert_normalized_to_pixel(normalized_landmarks, image_size)
    
    # (2) Compute overall pixel height
    pixel_height = compute_height_from_landmarks(pixel_landmarks)
    
    # (3) Calculate scale factor
    scale_factor = None
    if pixel_height and pixel_height > 0 and person_height_cm and person_height_cm > 0:
        scale_factor = person_height_cm / pixel_height
    
    # (4) Body segment lengths in pixels
    pixel_measurements = compute_body_measurements_px(pixel_landmarks)
    
    # (5) Convert to cm
    cm_measurements = convert_measurements_px_to_cm(pixel_measurements, scale_factor)
    
    # (6) Posture angles
    posture_angles = compute_posture_angles(pixel_landmarks)
    
    return {
        'pixel_height': pixel_height,
        'scale_factor_cm_per_pixel': scale_factor,
        'pixel_measurements': pixel_measurements,
        'cm_measurements': cm_measurements,
        'posture_angles': posture_angles,
        'debug': {
            'landmarks_used': list(pixel_landmarks.keys()),
            'total_landmarks': len(pixel_landmarks),
        },
    }


__all__ = [
    'normalized_to_pixels',
    'convert_normalized_to_pixel',
    'compute_body_measurements_px',
    'convert_measurements_px_to_cm',
    'compute_posture_angles',
    'compute_height_from_landmarks',
    'compute_all_measurements',
    'distance',
    'angle_between',
    'vector',
    'neck_length',
    'torso_length',
    'upper_leg_length',
    'lower_leg_length',
    'full_leg_length',
    'shoulder_width',
    'hip_width',
    'compute_forward_head_angle',
    'compute_chin_to_chest_angle',
    'compute_torso_lean_angle',
    'compute_upper_back_angle',
]
