"""
MEASUREMENTS PACKAGE INTEGRATION SUMMARY

This document summarizes the measurements package architecture and how all
files work together to process normalized landmarks into body measurements
and posture angles.
"""

# ============================================================================
# FILE STRUCTURE & DEPENDENCIES
# ============================================================================

"""
measurements/
├── __init__.py                      # Main API - orchestrates all modules
├── normalized_to_px.py              # Step 1: Convert normalized→pixel coords
├── segment_lengths.py               # Step 2: Calculate body segment lengths
├── posture_metrics.py               # Step 3: Calculate posture angles
├── utils_geometry.py                # Shared: Vector & angle utilities
├── test_measurements_integration.py # Integration tests
└── README.md                        # User documentation

DEPENDENCY GRAPH:
    __init__.py
        ├─→ normalized_to_px.py
        ├─→ segment_lengths.py ──→ utils_geometry.py
        ├─→ posture_metrics.py ──→ utils_geometry.py
        └─→ utils_geometry.py

IMPORT STRUCTURE:
    When user imports:
        from measurements import compute_all_measurements
    
    The __init__.py automatically imports:
        - convert_normalized_to_pixel (from normalized_to_px.py)
        - segment_lengths functions (from segment_lengths.py)
        - posture angle functions (from posture_metrics.py)
        - geometry utilities (from utils_geometry.py)
"""

# ============================================================================
# MODULE RESPONSIBILITIES
# ============================================================================

"""
1. normalized_to_px.py
   ├─ Input: List of dicts OR dict of tuples with normalized coords (0..1)
   ├─ Purpose: Convert normalized coordinates to pixel space
   ├─ Key functions:
   │  ├─ normalized_to_pixels()
   │  └─ convert_normalized_to_pixel()
   └─ Output: Dict mapping name → (x_px, y_px, z)

2. segment_lengths.py
   ├─ Input: Dict of landmarks with pixel coordinates
   ├─ Purpose: Compute distances between landmark pairs
   ├─ Key functions:
   │  ├─ distance()              - Euclidean distance
   │  ├─ neck_length()           - Ear to shoulder
   │  ├─ torso_length()          - Shoulder to hip
   │  ├─ full_leg_length()       - Hip to ankle
   │  ├─ shoulder_width()        - Left to right shoulder
   │  └─ hip_width()             - Left to right hip
   └─ Output: Dict with measurement values or None

3. utils_geometry.py
   ├─ Input: 2D tuples (x, y)
   ├─ Purpose: Shared geometry calculations
   ├─ Key functions:
   │  ├─ vector(p1, p2)         - Create direction vector
   │  └─ angle_between(v1, v2)  - Angle between vectors (degrees)
   └─ Output: Floats (vectors or angles)

4. posture_metrics.py
   ├─ Input: Dict of landmarks with pixel coordinates
   ├─ Purpose: Calculate posture-related angles
   ├─ Key functions:
   │  ├─ compute_forward_head_angle()     - CVA
   │  ├─ compute_chin_to_chest_angle()    - Neck flexion
   │  ├─ compute_torso_lean_angle()       - Forward/backward lean
   │  └─ compute_upper_back_angle()       - Thoracic kyphosis
   ├─ Dependencies: vector(), angle_between() from utils_geometry
   └─ Output: Dict with angle values or None

5. __init__.py
   ├─ Input: Normalized landmarks, image_size, person_height_cm
   ├─ Purpose: High-level orchestration of full pipeline
   ├─ Key functions:
   │  ├─ compute_all_measurements()       - Full pipeline
   │  ├─ compute_body_measurements_px()   - Segment lengths only
   │  ├─ compute_posture_angles()         - Angles only
   │  ├─ convert_measurements_px_to_cm()  - Unit conversion
   │  └─ compute_height_from_landmarks()  - Height calculation
   ├─ Dependencies: All other modules
   └─ Output: Dict with all measurements, angles, and metadata
"""

# ============================================================================
# DATA FLOW PIPELINE
# ============================================================================

"""
STEP-BY-STEP EXECUTION:

User Input:
    normalized_landmarks = [
        {"name": "nose", "x": 0.5, "y": 0.15, "z": 0.0},
        {"name": "left_shoulder", "x": 0.35, "y": 0.3, "z": 0.0},
        ...
    ]
    image_size = (1280, 720)
    person_height_cm = 170.0

        ↓↓↓ compute_all_measurements() called ↓↓↓

Step 1: COORDINATE CONVERSION
    Function: convert_normalized_to_pixel() [from normalized_to_px.py]
    Input:  List of dicts with normalized coords (0..1)
    Output: Dict with pixel coords
    
    Example:
        {"nose": (640.0, 108.0, 0.0)}  # 0.5 * 1280 = 640, 0.15 * 720 = 108

Step 2: HEIGHT CALCULATION
    Function: compute_height_from_landmarks() [from __init__.py]
    Input:  Dict of pixel landmarks
    Process: Distance from nose to ankle center
    Output: float (pixel_height)
    
    Example:
        pixel_height = 576.0 px

Step 3: SCALE FACTOR DERIVATION
    Function: Built into compute_all_measurements() [from __init__.py]
    Input:  pixel_height, person_height_cm
    Process: scale_factor = person_height_cm / pixel_height
    Output: float (cm_per_pixel)
    
    Example:
        scale_factor = 170.0 / 576.0 = 0.295139 cm/px

Step 4: SEGMENT LENGTH CALCULATION
    Function: compute_body_measurements_px() [from __init__.py]
        └─ calls functions from segment_lengths.py
    Input:  Dict of pixel landmarks
    Process: Multiple distance() calculations
    Output: Dict with all segment measurements in pixels
    
    Example:
        {
            'torso_length_px': 225.28,
            'full_leg_px': 252.0,
            'shoulder_width_px': 384.0,
            ...
        }

Step 5: UNIT CONVERSION (px → cm)
    Function: convert_measurements_px_to_cm() [from __init__.py]
    Input:  pixel_measurements dict, scale_factor
    Process: value_cm = value_px * scale_factor
    Output: Dict with all measurements in centimeters
    
    Example:
        {
            'torso_length_cm': 66.49,  # 225.28 * 0.295139
            'full_leg_cm': 74.38,
            'shoulder_width_cm': 113.33,
            ...
        }

Step 6: ANGLE CALCULATION
    Function: compute_posture_angles() [from __init__.py]
        └─ calls functions from posture_metrics.py
            └─ which use vector(), angle_between() from utils_geometry.py
    Input:  Dict of pixel landmarks
    Process: Vector creation and angle calculations
    Output: Dict with all posture angles in degrees
    
    Example:
        {
            'forward_head_angle_deg': 45.2,
            'torso_lean_angle_deg': 163.5,
            ...
        }

Final Output:
    {
        'pixel_height': 576.0,
        'scale_factor_cm_per_pixel': 0.295139,
        'pixel_measurements': {...},
        'cm_measurements': {...},
        'posture_angles': {...},
        'debug': {...},
    }
"""

# ============================================================================
# IMPORTS & CROSS-MODULE DEPENDENCIES
# ============================================================================

"""
IMPORT CHAIN:

__init__.py
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

posture_metrics.py
    from .utils_geometry import vector, angle_between

segment_lengths.py
    # No internal imports (pure functions)

normalized_to_px.py
    # No internal imports (pure functions)

utils_geometry.py
    # No internal imports (pure functions)

KEY PRINCIPLE:
    All imports are relative (from . import) and properly scoped.
    No circular dependencies.
    Pure functions (no side effects or state).
"""

# ============================================================================
# LANDMARK NAMING CONVENTION
# ============================================================================

"""
EXPECTED LANDMARK NAMES:
    These should match MediaPipe pose landmark names (case-insensitive).
    
    Core landmarks used:
        - nose
        - left_shoulder, right_shoulder
        - left_hip, right_hip
        - left_knee, right_knee
        - left_ankle, right_ankle
        - left_elbow, right_elbow
        - right_ear (for posture metrics)
    
    CASE HANDLING:
        The code handles both lowercase and UPPERCASE variants:
        
        Example from posture_metrics.py:
            ear = landmarks.get("right_ear") or landmarks.get("RIGHT_EAR")
        
        This ensures compatibility with different normalization outputs.

    MISSING LANDMARKS:
        All functions gracefully handle missing landmarks:
        - Return None if required landmarks are absent
        - Caller must check for None values
        - Example: if torso_length is None, skip that measurement
"""

# ============================================================================
# TYPE HINTS & SIGNATURES
# ============================================================================

"""
NORMALIZED LANDMARKS INPUT FORMATS:

Format 1: List of dicts (from normalization module output)
    List[Dict[str, float]]
    Example:
        [
            {"name": "nose", "x": 0.5, "y": 0.15, "z": 0.0},
            {"name": "left_shoulder", "x": 0.35, "y": 0.3, "z": 0.0},
            ...
        ]

Format 2: Dict of tuples (alternative format)
    Dict[str, Tuple[float, float, float]]
    Example:
        {
            "nose": (0.5, 0.15, 0.0),
            "left_shoulder": (0.35, 0.3, 0.0),
            ...
        }

INTERMEDIATE LANDMARK FORMAT (pixel space):

    Dict[str, Tuple[float, float, float]]
    Where Tuple is (x_px, y_px, z)
    Example:
        {
            "nose": (640.0, 108.0, 0.0),
            "left_shoulder": (448.0, 216.0, 0.0),
            ...
        }

MEASUREMENT OUTPUT:

    Dict[str, Optional[float]]
    Values are either:
        - float (successful measurement in pixels)
        - None (missing landmarks)
    
    Example:
        {
            'torso_length_px': 225.28,
            'full_leg_px': 252.0,
            'shoulder_width_px': None,  # If landmarks missing
            ...
        }
"""

# ============================================================================
# ERROR HANDLING & ROBUSTNESS
# ============================================================================

"""
GRACEFUL DEGRADATION:

1. Missing Landmarks:
   - Measurements return None instead of throwing errors
   - Caller should check for None before using values
   
   Example:
       torso_len = results['pixel_measurements']['torso_length_px']
       if torso_len is not None:
           cm_value = torso_len * scale_factor

2. Invalid image_size:
   - ValueError raised with clear message
   - image_size must be (width, height) tuple
   
   Example:
       if not image_size or len(image_size) != 2:
           raise ValueError("image_size must be a tuple (width, height)")

3. Zero/Negative scale_factor:
   - cm_measurements skipped (returns empty dict)
   - Avoids negative or infinite measurements
   
   Example:
       if scale_factor is None or scale_factor <= 0:
           return {}  # Return empty dict instead of bad measurements

4. Colinear points:
   - angle_between() handles zero-magnitude vectors
   - Returns 0.0 for invalid angles
   
   Example:
       if mag1 == 0 or mag2 == 0:
           return 0.0
"""

# ============================================================================
# INTEGRATION WITH EXTERNAL MODULES
# ============================================================================

"""
EXPECTED INPUTS FROM NORMALIZATION:

from normalization import DataNormalizer

normalizer = DataNormalizer()
normalized_landmarks = normalizer.normalize_landmarks(raw_landmarks)
# Returns list of dicts: [{"name": "...", "x": ..., "y": ..., "z": ...}, ...]

Then pass to measurements:
    from measurements import compute_all_measurements
    results = compute_all_measurements(normalized_landmarks, image_size, ...)

EXPECTED OUTPUTS TO STORAGE:

from calibration import storage

payload = {
    "version": "1.0",
    "timestamp": datetime.now().isoformat(),
    "raw_landmarks": {...},
    "normalized": normalized_landmarks,
    "measurements": {
        **results['pixel_measurements'],
        **results['cm_measurements'],
        **results['posture_angles'],
    },
    "camera_meta": {...},
}

storage.save_calibration_json(payload)
"""

# ============================================================================
# TESTING & VALIDATION
# ============================================================================

"""
RUN INTEGRATION TEST:

    python3 measurements/test_measurements_integration.py

EXPECTED OUTPUT:
    ✓ 14 landmarks converted to pixel space
    ✓ pixel_height computed: 576.00 px
    ✓ scale_factor computed: 0.295139 cm/px
    ✓ pixel_measurements: 7 values computed
    ✓ cm_measurements: 7 values computed
    ✓ posture_angles: 4 angles computed
    ✓ ALL TESTS PASSED

VALIDATION CHECKS:
    1. Height > 100 px (reasonable minimum)
    2. Scale factor > 0 (positive scaling)
    3. At least 1 measurement computed
    4. At least 1 angle computed
"""

# ============================================================================
# SUMMARY
# ============================================================================

"""
KEY FEATURES:
    ✓ All modules work together seamlessly
    ✓ Proper relative imports with no circular dependencies
    ✓ Type hints for clarity and IDE support
    ✓ Graceful handling of missing landmarks (returns None)
    ✓ Case-insensitive landmark name matching
    ✓ Flexible input formats (list or dict)
    ✓ Comprehensive integration test
    ✓ Well-documented with examples

QUICK START:
    from measurements import compute_all_measurements
    
    results = compute_all_measurements(
        normalized_landmarks,
        image_size=(1280, 720),
        person_height_cm=170.0
    )
    
    # Access results
    height = results['pixel_height']
    torso_px = results['pixel_measurements']['torso_length_px']
    torso_cm = results['cm_measurements']['torso_length_cm']
    head_angle = results['posture_angles']['forward_head_angle_deg']

PRODUCTION USE:
    1. Ensure normalized landmarks are properly formatted
    2. Pass valid image_size
    3. Optional: provide person_height_cm for cm conversions
    4. Check for None values in measurements/angles
    5. Save results via calibration.storage
"""

if __name__ == "__main__":
    print(__doc__)
