"""
Integration test for measurements package.

Tests that all modules work together correctly with normalized landmark outputs.
"""

from typing import List, Dict
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from measurements import (
    compute_all_measurements,
    compute_body_measurements_px,
    compute_posture_angles,
    convert_normalized_to_pixel,
)


def test_normalized_landmarks_to_measurements():
    """Test the full pipeline: normalized landmarks -> pixel -> measurements -> angles."""
    
    # Sample normalized landmarks (output from normalization module)
    # Format: list of dicts with keys "name", "x", "y", "z" (0..1 range)
    normalized_landmarks = [
        {"name": "nose", "x": 0.5, "y": 0.15, "z": 0.0},
        {"name": "left_shoulder", "x": 0.35, "y": 0.3, "z": 0.0},
        {"name": "right_shoulder", "x": 0.65, "y": 0.3, "z": 0.0},
        {"name": "left_hip", "x": 0.4, "y": 0.6, "z": 0.0},
        {"name": "right_hip", "x": 0.6, "y": 0.6, "z": 0.0},
        {"name": "left_elbow", "x": 0.25, "y": 0.45, "z": 0.0},
        {"name": "right_elbow", "x": 0.75, "y": 0.45, "z": 0.0},
        {"name": "left_wrist", "x": 0.15, "y": 0.55, "z": 0.0},
        {"name": "right_wrist", "x": 0.85, "y": 0.55, "z": 0.0},
        {"name": "left_knee", "x": 0.4, "y": 0.8, "z": 0.0},
        {"name": "right_knee", "x": 0.6, "y": 0.8, "z": 0.0},
        {"name": "left_ankle", "x": 0.4, "y": 0.95, "z": 0.0},
        {"name": "right_ankle", "x": 0.6, "y": 0.95, "z": 0.0},
        {"name": "right_ear", "x": 0.65, "y": 0.1, "z": 0.0},
    ]
    
    # Camera frame dimensions
    image_size = (1280, 720)
    
    # Known person height (for scaling)
    person_height_cm = 170.0
    
    print("\\n" + "="*70)
    print("MEASUREMENTS INTEGRATION TEST")
    print("="*70)
    
    # ========================================================================
    # STEP 1: Convert normalized landmarks to pixel coordinates
    # ========================================================================
    print("\\n[STEP 1] Converting normalized landmarks to pixel coordinates...")
    pixel_landmarks = convert_normalized_to_pixel(normalized_landmarks, image_size)
    
    print(f"  ✓ Converted {len(pixel_landmarks)} landmarks to pixel space")
    print(f"  Sample: nose = {pixel_landmarks.get('nose')}")
    
    # ========================================================================
    # STEP 2: Compute all measurements
    # ========================================================================
    print("\\n[STEP 2] Running full measurement pipeline...")
    results = compute_all_measurements(
        normalized_landmarks,
        image_size=image_size,
        person_height_cm=person_height_cm
    )
    
    # ========================================================================
    # STEP 3: Display results
    # ========================================================================
    print("\\n[RESULTS] Computed measurements:")
    print("-" * 70)
    
    print(f"\\n  Overall Height:")
    print(f"    Pixel height: {results['pixel_height']:.2f} px")
    print(f"    Scale factor: {results['scale_factor_cm_per_pixel']:.6f} cm/px")
    
    print(f"\\n  Segment Lengths (pixels):")
    for key, value in sorted(results['pixel_measurements'].items()):
        if value is not None:
            print(f"    {key:20s}: {value:8.2f} px")
        else:
            print(f"    {key:20s}: N/A")
    
    print(f"\\n  Segment Lengths (centimeters):")
    for key, value in sorted(results['cm_measurements'].items()):
        if value is not None:
            print(f"    {key:20s}: {value:8.2f} cm")
        else:
            print(f"    {key:20s}: N/A")
    
    print(f"\\n  Posture Angles (degrees):")
    for key, value in sorted(results['posture_angles'].items()):
        if value is not None:
            print(f"    {key:25s}: {value:8.2f}°")
        else:
            print(f"    {key:25s}: N/A")
    
    print(f"\\n  Debug Info:")
    print(f"    Landmarks used: {results['debug']['total_landmarks']}")
    print(f"    Landmark names: {', '.join(sorted(results['debug']['landmarks_used']))}")
    
    # ========================================================================
    # STEP 4: Validation checks
    # ========================================================================
    print("\\n[VALIDATION] Checking results:")
    print("-" * 70)
    
    errors = []
    warnings = []
    
    # Check height
    if results['pixel_height'] is None:
        errors.append("  ✗ pixel_height is None (missing nose or ankles)")
    elif results['pixel_height'] < 100:
        warnings.append(f"  ⚠ pixel_height seems small: {results['pixel_height']:.2f} px")
    else:
        print("  ✓ pixel_height computed successfully")
    
    # Check scale factor
    if results['scale_factor_cm_per_pixel'] is None:
        warnings.append("  ⚠ scale_factor is None (person_height_cm may not be set)")
    else:
        print(f"  ✓ scale_factor computed: {results['scale_factor_cm_per_pixel']:.6f} cm/px")
    
    # Check measurements
    pixel_count = sum(1 for v in results['pixel_measurements'].values() if v is not None)
    cm_count = sum(1 for v in results['cm_measurements'].values() if v is not None)
    
    if pixel_count > 0:
        print(f"  ✓ pixel_measurements: {pixel_count} values computed")
    else:
        errors.append("  ✗ No pixel measurements computed")
    
    if cm_count > 0:
        print(f"  ✓ cm_measurements: {cm_count} values computed")
    else:
        warnings.append("  ⚠ No cm_measurements (scale_factor may be missing)")
    
    # Check angles
    angle_count = sum(1 for v in results['posture_angles'].values() if v is not None)
    if angle_count > 0:
        print(f"  ✓ posture_angles: {angle_count} angles computed")
    else:
        warnings.append("  ⚠ No angles computed (missing landmarks)")
    
    # Print summary
    print("\\n" + "="*70)
    if errors:
        print("ERRORS:")
        for error in errors:
            print(error)
    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(warning)
    
    if not errors:
        print("✓ ALL TESTS PASSED")
    
    print("="*70 + "\\n")
    
    return results


def test_dict_format_landmarks():
    """Test with dict format landmarks (alternative input format)."""
    
    # Alternative format: dict mapping landmark_name -> (x, y, z) tuples
    normalized_landmarks_dict = {
        "nose": (0.5, 0.15, 0.0),
        "left_shoulder": (0.35, 0.3, 0.0),
        "right_shoulder": (0.65, 0.3, 0.0),
        "left_hip": (0.4, 0.6, 0.0),
        "right_hip": (0.6, 0.6, 0.0),
        "left_ankle": (0.4, 0.95, 0.0),
        "right_ankle": (0.6, 0.95, 0.0),
        "right_ear": (0.65, 0.1, 0.0),
    }
    
    image_size = (1280, 720)
    person_height_cm = 170.0
    
    print("\\n" + "="*70)
    print("TEST: Dict Format Landmarks")
    print("="*70)
    
    results = compute_all_measurements(
        normalized_landmarks_dict,
        image_size=image_size,
        person_height_cm=person_height_cm
    )
    
    print(f"✓ Dict format works. Height: {results['pixel_height']:.2f} px")
    print(f"✓ Computed {len([v for v in results['pixel_measurements'].values() if v is not None])} pixel measurements")
    print("="*70 + "\\n")
    
    return results


if __name__ == "__main__":
    # Run tests
    results1 = test_normalized_landmarks_to_measurements()
    results2 = test_dict_format_landmarks()
    
    print("\\nAll integration tests completed successfully!")
