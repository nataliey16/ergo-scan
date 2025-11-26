# Measurements Package Documentation

## Overview

The `measurements` package takes **normalized landmark outputs** from the normalization module and computes:
1. **Body segment lengths** (in pixels and centimeters)
2. **Posture angles** (forward head angle, torso lean, etc.)

All modules work together seamlessly with proper imports and type hints.

---

## Module Structure

### 1. **`normalized_to_px.py`** – Coordinate Conversion
Converts normalized landmarks (0..1 range) to pixel coordinates.

**Key Functions:**
- `normalized_to_pixels(landmarks, image_size)` – Converts normalized → pixel
- `convert_normalized_to_pixel(landmarks, image_size)` – Alias with required image_size

**Input Format (List of dicts):**
```python
[
    {"name": "nose", "x": 0.5, "y": 0.15, "z": 0.0},
    {"name": "left_shoulder", "x": 0.35, "y": 0.3, "z": 0.0},
    ...
]
```

**Input Format (Dict):**
```python
{
    "nose": (0.5, 0.15, 0.0),
    "left_shoulder": (0.35, 0.3, 0.0),
    ...
}
```

**Output:**
```python
{
    "nose": (640.0, 108.0, 0.0),  # pixel coordinates
    "left_shoulder": (448.0, 216.0, 0.0),
    ...
}
```

---

### 2. **`segment_lengths.py`** – Body Measurements
Computes distances between landmarks (segment lengths).

**Key Functions:**
- `distance(p1, p2)` – Euclidean distance between 2D points
- `torso_length(landmarks)` – Shoulder to hip distance
- `full_leg_length(landmarks)` – Hip to ankle distance
- `shoulder_width(landmarks)` – Left to right shoulder distance
- `hip_width(landmarks)` – Left to right hip distance
- `neck_length(landmarks)` – Ear to shoulder distance

**Input:** Dict mapping landmark names → (x, y, z) tuples
**Output:** Float distances in pixels (or None if landmarks missing)

**Example:**
```python
measurements_px = compute_body_measurements_px(pixel_landmarks)
# Returns:
{
    'neck_length_px': 144.0,
    'torso_length_px': 225.28,
    'full_leg_px': 252.0,
    'shoulder_width_px': 384.0,
    'hip_width_px': 256.0,
    ...
}
```

---

### 3. **`posture_metrics.py`** – Angle Calculations
Computes ergonomic posture angles using vector math.

**Key Functions:**
- `compute_forward_head_angle(landmarks)` – CVA (Craniovertebral Angle)
- `compute_chin_to_chest_angle(landmarks)` – Neck flexion
- `compute_torso_lean_angle(landmarks)` – Forward/backward lean
- `compute_upper_back_angle(landmarks)` – Thoracic kyphosis

**Input:** Dict mapping landmark names → (x, y, z) tuples
**Output:** Float angles in degrees (or None if landmarks missing)

**Example:**
```python
angles = compute_posture_angles(pixel_landmarks)
# Returns:
{
    'forward_head_angle_deg': 45.2,
    'chin_to_chest_angle_deg': 29.4,
    'torso_lean_angle_deg': 163.5,
    'upper_back_angle_deg': 163.5,
}
```

---

### 4. **`utils_geometry.py`** – Geometry Utilities
Shared geometry functions used by other modules.

**Key Functions:**
- `vector(p1, p2)` – Create vector from p1 → p2
- `angle_between(v1, v2)` – Angle between two 2D vectors in degrees

**Input/Output:** 2D tuples (x, y)

---

### 5. **`__init__.py`** – Integration & High-Level API
Combines all modules into a unified interface.

**Key Functions:**
- `compute_all_measurements(normalized_landmarks, image_size, person_height_cm)` – Full pipeline
- `compute_body_measurements_px(landmarks_px)` – Segment lengths only
- `compute_posture_angles(landmarks_px)` – Angles only
- `convert_measurements_px_to_cm(measurements_px, scale_factor)` – Unit conversion

---

## Full Pipeline Example

```python
from measurements import compute_all_measurements

# 1. Get normalized landmarks from normalization module
normalized_landmarks = [
    {"name": "nose", "x": 0.5, "y": 0.15, "z": 0.0},
    {"name": "left_shoulder", "x": 0.35, "y": 0.3, "z": 0.0},
    {"name": "right_shoulder", "x": 0.65, "y": 0.3, "z": 0.0},
    ...
]

# 2. Run full measurement pipeline
results = compute_all_measurements(
    normalized_landmarks,
    image_size=(1280, 720),
    person_height_cm=170.0
)

# 3. Access results
print(f"Height: {results['pixel_height']} px")
print(f"Scale: {results['scale_factor_cm_per_pixel']} cm/px")
print(f"Torso (px): {results['pixel_measurements']['torso_length_px']} px")
print(f"Torso (cm): {results['cm_measurements']['torso_length_cm']} cm")
print(f"Head angle: {results['posture_angles']['forward_head_angle_deg']}°")
```

---

## Landmark Naming Convention

The modules expect MediaPipe-style landmark names:

**Key landmarks used:**
- `nose` – Face reference point
- `left_shoulder`, `right_shoulder` – Shoulder joints
- `left_hip`, `right_hip` – Hip joints
- `left_knee`, `right_knee` – Knee joints
- `left_ankle`, `right_ankle` – Ankle joints
- `left_elbow`, `right_elbow` – Elbow joints
- `right_ear` – Ear reference (side-view angles)

Names are **case-insensitive** (checks both lowercase and uppercase).

---

## Key Design Features

### 1. **Robustness**
- Handles missing landmarks gracefully (returns `None` for missing measurements)
- Supports both list and dict input formats
- Case-insensitive landmark name matching

### 2. **Modularity**
- Each file handles one responsibility (conversion, lengths, angles, utilities)
- Proper relative imports ensure modules work together
- Type hints for clarity

### 3. **Scalability**
- Easy to add new measurements (add function to `segment_lengths.py`)
- Easy to add new angles (add function to `posture_metrics.py`)
- Central `compute_all_measurements()` function orchestrates everything

### 4. **Data Flow**
```
Normalized Landmarks (list/dict)
         ↓
   Pixel Conversion (normalized_to_px.py)
         ↓
   Pixel Landmarks (dict)
         ↓
   ┌─────┴──────┐
   ↓            ↓
Lengths      Angles
(segment_    (posture_
 lengths.py) metrics.py)
   ↓            ↓
   └─────┬──────┘
         ↓
    cm Conversion
         ↓
    Final Results
```

---

## Output Structure

```python
{
    'pixel_height': 576.0,                           # Overall height in pixels
    'scale_factor_cm_per_pixel': 0.295139,           # Cm per pixel
    'pixel_measurements': {                          # All lengths in pixels
        'neck_length_px': 144.0,
        'torso_length_px': 225.28,
        'full_leg_px': 252.0,
        'shoulder_width_px': 384.0,
        'hip_width_px': 256.0,
        'upper_leg_px': 144.0,
        'lower_leg_px': 108.0,
    },
    'cm_measurements': {                             # All lengths in cm
        'neck_length_cm': 42.50,
        'torso_length_cm': 66.49,
        'full_leg_cm': 74.38,
        'shoulder_width_cm': 113.33,
        'hip_width_cm': 75.56,
        'upper_leg_cm': 42.50,
        'lower_leg_cm': 31.88,
    },
    'posture_angles': {                              # All angles in degrees
        'forward_head_angle_deg': 45.2,
        'chin_to_chest_angle_deg': 29.4,
        'torso_lean_angle_deg': 163.5,
        'upper_back_angle_deg': 163.5,
    },
    'debug': {
        'landmarks_used': 14,
        'total_landmarks': ['nose', 'left_shoulder', ...],
    },
}
```

---

## Integration with Calibration Flow

```python
# In your calibration.py or main flow:
from normalization import DataNormalizer
from measurements import compute_all_measurements
import calibration.storage as storage

# 1. Get raw landmarks from MediaPipe
raw_landmarks = mp_pose.process(frame).pose_landmarks

# 2. Normalize them
normalizer = DataNormalizer()
normalized = normalizer.normalize_landmarks(raw_landmarks)

# 3. Convert to measurements
meas_results = compute_all_measurements(
    normalized,
    image_size=(frame.width, frame.height),
    person_height_cm=170.0
)

# 4. Build and save calibration JSON
payload = {
    "version": "1.0",
    "timestamp": datetime.now().isoformat(),
    "raw_landmarks": {...},
    "normalized": normalized,
    "measurements": {
        **meas_results['pixel_measurements'],
        **meas_results['cm_measurements'],
        **meas_results['posture_angles'],
    },
    "camera_meta": {...},
}

storage.save_calibration_json(payload)
```

---

## Testing

Run the integration test:

```bash
python3 measurements/test_measurements_integration.py
```

Expected output shows successful computation of:
- ✓ 14 landmarks converted to pixels
- ✓ 7 segment length measurements
- ✓ 4 posture angle measurements
- ✓ cm conversions with proper scaling

---

## Troubleshooting

### Missing measurements (None values)
**Cause:** Required landmarks not present in input
**Solution:** Ensure all landmarks are in the normalized output, or use fallback values

### Incorrect angles (0° or 180°)
**Cause:** Landmarks are colinear or missing
**Solution:** Check that shoulder, hip, and other reference points are present

### Very large/small scale factors
**Cause:** Incorrect `person_height_cm` or unrealistic `pixel_height`
**Solution:** Validate frame height calculation and person height input

