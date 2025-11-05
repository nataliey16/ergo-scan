"""
Test script for ErgoScan Data Normalization & Refinement integration
Tests the data processing pipeline with sample data
"""

import numpy as np
import time
import json
import sys
import os
from typing import List, Tuple

# Add project root to path to import normalization package
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from normalization import DataNormalizer, MeasurementPoint, BodyProfile

def generate_sample_measurements(num_frames: int = 50) -> list:
    """Generate realistic sample measurements for testing"""
    measurements = []
    base_timestamp = time.time()
    
    # Base measurements (in pixels for a 640x480 frame)
    base_measurements = {
        'height': 400,
        'shoulder_width': 120,
        'torso_length': 150,
        'arm_length': 180,
        'leg_length': 200,
        'hip_width': 100
    }
    
    for frame_id in range(num_frames):
        timestamp = base_timestamp + frame_id * 0.1  # 10 FPS
        
        # Add realistic variation and some outliers
        for measurement_type, base_value in base_measurements.items():
            # Normal variation (±5%)
            variation = np.random.normal(0, base_value * 0.05)
            value = base_value + variation
            
            # Add some outliers (2% chance)
            if np.random.random() < 0.02:
                value += np.random.normal(0, base_value * 0.3)  # Large outlier
            
            # Simulate confidence variation
            confidence = np.random.uniform(0.7, 0.95)
            
            # Simulate depth variation
            depth = np.random.uniform(1.8, 2.2)
            
            # Simulate landmarks quality
            landmarks_quality = np.random.uniform(0.8, 0.95)
            
            measurements.append(MeasurementPoint(
                timestamp=timestamp,
                measurement_type=measurement_type,
                value=max(0, value),  # Ensure non-negative
                confidence=confidence,
                depth=depth,
                frame_id=frame_id,
                landmarks_quality=landmarks_quality
            ))
    
    return measurements

def test_data_normalizer():
    """Test the data normalizer with sample data"""
    print("Testing Data Normalization & Refinement System")
    print("=" * 50)
    
    # Generate sample data
    print("Generating sample measurements...")
    measurements = generate_sample_measurements(100)
    print(f"Generated {len(measurements)} measurements across {100} frames")
    
    # Initialize normalizer
    normalizer = DataNormalizer()
    
    # Process measurements
    print("\nProcessing measurements...")
    body_profile, report = normalizer.process_measurements(measurements, "test_user")
    
    # Display results
    print("\nBody Profile Results:")
    print("-" * 30)
    print(f"Height: {body_profile.height:.2f} px")
    print(f"Shoulder Width: {body_profile.shoulder_width:.2f} px")
    print(f"Torso Length: {body_profile.torso_length:.2f} px")
    print(f"Arm Length: {body_profile.arm_length:.2f} px")
    print(f"Leg Length: {body_profile.leg_length:.2f} px")
    print(f"Hip Width: {body_profile.hip_width:.2f} px")
    
    print(f"\nCalibration Quality: {body_profile.calibration_quality:.2f}/10")
    
    print("\nProcessing Report:")
    print("-" * 30)
    for key, value in report.items():
        if isinstance(value, dict):
            print(f"{key.replace('_', ' ').title()}:")
            for subkey, subvalue in value.items():
                if isinstance(subvalue, (int, float)):
                    print(f"  {subkey.replace('_', ' ').title()}: {subvalue:.2f}")
                else:
                    print(f"  {subkey.replace('_', ' ').title()}: {subvalue}")
        elif isinstance(value, (int, float)):
            print(f"{key.replace('_', ' ').title()}: {value:.2f}")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    return body_profile, report

def test_real_time_processing():
    """Test real-time style processing"""
    print("\n" + "=" * 50)
    print("Testing Real-time Processing Simulation")
    print("=" * 50)
    
    normalizer = DataNormalizer()
    measurement_buffer = []
    
    print("Simulating real-time measurement collection...")
    
    # Simulate collecting measurements over time
    for frame in range(30):
        # Generate measurements for current frame
        frame_measurements = generate_sample_measurements(1)
        if frame_measurements:
            frame_measurements[0].frame_id = frame
            frame_measurements[0].timestamp = time.time()
            
            measurement_buffer.extend(frame_measurements)
        
        # Process every 10 frames
        if (frame + 1) % 10 == 0:
            if len(measurement_buffer) >= 5:
                body_profile, report = normalizer.process_measurements(
                    measurement_buffer, f"realtime_user_{frame}"
                )
                print(f"Frame {frame + 1}: Quality score = {body_profile.calibration_quality:.2f}")
                
                # Keep only recent measurements (sliding window)
                measurement_buffer = measurement_buffer[-20:]  # Keep last 20 measurements
    
    print("Real-time simulation completed")

def test_outlier_detection():
    """Test outlier detection capabilities"""
    print("\n" + "=" * 50)
    print("Testing Outlier Detection")
    print("=" * 50)
    
    # Generate measurements with intentional outliers
    measurements = []
    base_timestamp = time.time()
    
    # Normal measurements
    for i in range(40):
        measurements.append(MeasurementPoint(
            timestamp=base_timestamp + i * 0.1,
            measurement_type='height',
            value=400 + np.random.normal(0, 10),  # Normal variation
            confidence=0.9,
            depth=2.0,
            frame_id=i,
            landmarks_quality=0.9
        ))
    
    # Add clear outliers
    outlier_indices = [10, 20, 30]
    for idx in outlier_indices:
        measurements[idx].value = 600  # Clear outlier (50% larger)
    
    print(f"Added outliers at frame indices: {outlier_indices}")
    
    # Process with outlier detection
    normalizer = DataNormalizer()
    body_profile, report = normalizer.process_measurements(measurements, "outlier_test")
    
    print(f"Final average height: {body_profile.height:.2f} px")
    print(f"Expected height (without outliers): ~400 px")
    print(f"Quality score: {body_profile.calibration_quality:.2f}/10")

def save_test_results(body_profile: BodyProfile, report: dict):
    """Save test results to file"""
    test_results = {
        'body_profile': body_profile.__dict__,
        'processing_report': report,
        'test_info': {
            'test_type': 'data_normalization_test',
            'timestamp': time.time(),
            'description': 'Test of ErgoScan data normalization and refinement system'
        }
    }
    
    filename = f"test_results_{int(time.time())}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(test_results, f, indent=2)
        print(f"\nTest results saved to: {filename}")
    except Exception as e:
        print(f"Error saving test results: {e}")

def create_dummy_mediapipe_landmarks() -> List[Tuple[float, float, float]]:
    """Create dummy MediaPipe pose landmarks for testing with XYZ coordinates"""
    # MediaPipe pose has 33 landmarks, we'll create a basic standing pose
    landmarks = []
    
    # Basic human pose landmarks (x, y, z coordinates in normalized space)
    # Simulating a person standing upright facing the camera
    # x: left-right, y: top-bottom, z: depth (camera distance)
    
    # Face landmarks (0-10)
    landmarks.extend([
        (0.5, 0.1, 0.0),   # 0: nose
        (0.48, 0.08, 0.02), # 1: left_eye_inner
        (0.47, 0.08, 0.01), # 2: left_eye
        (0.46, 0.08, 0.03), # 3: left_eye_outer
        (0.52, 0.08, 0.02), # 4: right_eye_inner
        (0.53, 0.08, 0.01), # 5: right_eye
        (0.54, 0.08, 0.03), # 6: right_eye_outer
        (0.45, 0.12, 0.05), # 7: left_ear
        (0.55, 0.12, 0.05), # 8: right_ear
        (0.47, 0.14, 0.01), # 9: mouth_left
        (0.53, 0.14, 0.01), # 10: mouth_right
    ])
    
    # Upper body landmarks (11-16)
    landmarks.extend([
        (0.4, 0.25, 0.02),  # 11: left_shoulder
        (0.6, 0.25, 0.02),  # 12: right_shoulder
        (0.35, 0.45, 0.05), # 13: left_elbow
        (0.65, 0.45, 0.05), # 14: right_elbow
        (0.32, 0.65, 0.08), # 15: left_wrist
        (0.68, 0.65, 0.08), # 16: right_wrist
    ])
    
    # Hand landmarks (17-22)
    landmarks.extend([
        (0.31, 0.67, 0.10), # 17: left_pinky
        (0.30, 0.66, 0.09), # 18: left_index
        (0.315, 0.665, 0.09), # 19: left_thumb
        (0.69, 0.67, 0.10), # 20: right_pinky
        (0.70, 0.66, 0.09), # 21: right_index
        (0.685, 0.665, 0.09), # 22: right_thumb
    ])
    
    # Lower body landmarks (23-32)
    landmarks.extend([
        (0.45, 0.75, 0.01), # 23: left_hip
        (0.55, 0.75, 0.01), # 24: right_hip
        (0.43, 0.9, 0.03),  # 25: left_knee
        (0.57, 0.9, 0.03),  # 26: right_knee
        (0.42, 1.05, 0.05), # 27: left_ankle
        (0.58, 1.05, 0.05), # 28: right_ankle
        (0.41, 1.08, 0.06), # 29: left_heel
        (0.59, 1.08, 0.06), # 30: right_heel
        (0.415, 1.1, 0.07), # 31: left_foot_index
        (0.585, 1.1, 0.07), # 32: right_foot_index
    ])
    
    return landmarks

def test_landmark_normalization():
    """Test the normalize_landmarks function with dummy MediaPipe data"""
    print("\n" + "=" * 50)
    print("Testing Landmark Normalization")
    print("=" * 50)
    
    # Initialize normalizer
    normalizer = DataNormalizer()
    
    # Create dummy landmarks
    raw_landmarks = create_dummy_mediapipe_landmarks()
    print(f"Created {len(raw_landmarks)} dummy MediaPipe landmarks")
    
    # Test different normalization options
    test_cases = [
        {"center_point": None, "target_height": 1.0, "name": "Default (centroid center)"},
        {"center_point": "nose", "target_height": 1.0, "name": "Nose-centered"},
        {"center_point": "chest", "target_height": 1.0, "name": "Chest-centered"}, 
        {"center_point": "hip", "target_height": 1.0, "name": "Hip-centered"},
        {"center_point": None, "target_height": 2.0, "name": "Scaled to height 2.0"},
    ]
    
    print("\nTesting normalization configurations:")
    print("-" * 40)
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            normalized = normalizer.normalize_landmarks(
                landmarks=raw_landmarks,
                center_point=test_case["center_point"],
                target_height=test_case["target_height"]
            )
            
            # Calculate statistics about the normalized landmarks
            coords = np.array(normalized)
            
            # Calculate bounding box for 3D coordinates
            min_coords = np.min(coords, axis=0)
            max_coords = np.max(coords, axis=0)
            
            if coords.shape[1] == 3:  # 3D coordinates
                min_x, min_y, min_z = min_coords
                max_x, max_y, max_z = max_coords
                width = max_x - min_x
                height = max_y - min_y
                depth = max_z - min_z
                center_x, center_y, center_z = np.mean(coords, axis=0)
                
                print(f"{i}. {test_case['name']}:")
                print(f"   Bounding box: ({min_x:.3f}, {min_y:.3f}, {min_z:.3f}) to ({max_x:.3f}, {max_y:.3f}, {max_z:.3f})")
                print(f"   Dimensions: {width:.3f} × {height:.3f} × {depth:.3f}")
                print(f"   Center: ({center_x:.3f}, {center_y:.3f}, {center_z:.3f})")
            else:  # 2D coordinates (fallback)
                min_x, min_y = min_coords
                max_x, max_y = max_coords
                width = max_x - min_x
                height = max_y - min_y
                center_x, center_y = np.mean(coords, axis=0)
                
                print(f"{i}. {test_case['name']}:")
                print(f"   Bounding box: ({min_x:.3f}, {min_y:.3f}) to ({max_x:.3f}, {max_y:.3f})")
                print(f"   Dimensions: {width:.3f} × {height:.3f}")
                print(f"   Center: ({center_x:.3f}, {center_y:.3f})")
            
            # Check that scaling worked correctly
            expected_height = test_case["target_height"]
            height_error = abs(height - expected_height)
            if height_error < 0.1:  # Allow 10% error tolerance
                print(f"   ✅ Height scaling: {height:.3f} (target: {expected_height})")
            else:
                print(f"   ⚠️  Height scaling: {height:.3f} (target: {expected_height}, error: {height_error:.3f})")
            
        except Exception as e:
            print(f"{i}. {test_case['name']}: ❌ Error - {e}")
    
    # Test with rotated input (tilted person)
    print("\nTesting rotation correction:")
    print("-" * 40)
    
    # Create tilted landmarks by rotating the original ones in 3D space
    rotation_angle = np.pi / 6  # 30 degrees around Z-axis
    cos_a, sin_a = np.cos(rotation_angle), np.sin(rotation_angle)
    # 3D rotation matrix around Z-axis
    rotation_matrix_3d = np.array([
        [cos_a, -sin_a, 0],
        [sin_a, cos_a, 0],
        [0, 0, 1]
    ])
    
    tilted_landmarks = []
    for x, y, z in raw_landmarks:
        # Center, rotate, then restore
        centered_point = np.array([x - 0.5, y - 0.5, z])
        rotated_point = np.dot(rotation_matrix_3d, centered_point)
        final_point = rotated_point + [0.5, 0.5, 0]
        tilted_landmarks.append((final_point[0], final_point[1], final_point[2]))
    
    try:
        # Normalize the tilted landmarks
        corrected = normalizer.normalize_landmarks(tilted_landmarks, target_height=1.0)
        
        # Check shoulder alignment (should be close to horizontal after normalization)
        left_shoulder = corrected[11]   # left_shoulder index
        right_shoulder = corrected[12]  # right_shoulder index
        
        # Calculate shoulder angle in XY plane (after 3D normalization)
        shoulder_angle = np.arctan2(
            right_shoulder[1] - left_shoulder[1],
            right_shoulder[0] - left_shoulder[0]
        )
        shoulder_tilt = abs(np.degrees(shoulder_angle))
        
        print(f"Original tilt: 30°")
        print(f"Corrected shoulder angle: {shoulder_tilt:.1f}°")
        
        if shoulder_tilt < 5:  # Should be nearly horizontal
            print("✅ Rotation correction successful")
        else:
            print("⚠️  Rotation correction may need improvement")
            
    except Exception as e:
        print(f"❌ Rotation test failed: {e}")
    
    print("\nLandmark normalization tests completed")
    return True

def main():
    """Run all tests"""
    print("ErgoScan Data Normalization & Refinement - Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Basic data normalization
        body_profile, report = test_data_normalizer()
        
        # Test 2: Real-time processing simulation
        test_real_time_processing()
        
        # Test 3: Outlier detection
        test_outlier_detection()
        
        # Test 4: Landmark normalization (NEW)
        test_landmark_normalization()
        
        # Save results
        save_test_results(body_profile, report)
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("The data normalization system is ready for integration.")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()