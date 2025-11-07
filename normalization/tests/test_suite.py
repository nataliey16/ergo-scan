#!/usr/bin/env python3
"""
ErgoScan Normalization - Comprehensive Test Suite

This module provides comprehensive testing for the ErgoScan normalization system:
- Data normalization and measurement processing 
- 3D landmark normalization with MediaPipe integration
- Real-time processing simulation
- Outlier detection and quality validation

Usage:
    python -m normalization.tests.test_suite
    python normalization/tests/test_suite.py

Author: ErgoScan Team
Version: 2.0.0 (3D Enhanced)
"""

import sys
import os
import time
from typing import List, Tuple

import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_normalizer import DataNormalizer, MeasurementPoint, BodyProfile


# =============================================================================
# Test Data Generation
# =============================================================================

def generate_sample_measurements(frames: int = 100) -> List[MeasurementPoint]:
    """Generate realistic sample measurements for testing"""
    measurements = []
    timestamp = time.time()
    
    # Define realistic measurement ranges (in pixels for camera-based measurements)
    measurement_ranges = {
        'height': (350, 450),
        'shoulder_width': (100, 140),
        'torso_length': (130, 170),
        'arm_length': (160, 200),
        'leg_length': (180, 220),
        'hip_width': (90, 120)
    }
    
    for frame_id in range(frames):
        frame_time = timestamp + frame_id * 0.1  # 10 FPS simulation
        
        for measurement_type, (min_val, max_val) in measurement_ranges.items():
            # Generate measurements with some realistic variation
            base_value = np.random.normal((min_val + max_val) / 2, (max_val - min_val) / 8)
            
            # Add temporal consistency (measurements should be similar across frames)
            if frame_id > 0:
                temporal_noise = np.random.normal(0, 2)  # Small frame-to-frame variation
                base_value += temporal_noise
            
            # Simulate realistic measurement quality
            confidence = np.random.uniform(0.7, 0.95)
            depth = np.random.uniform(1.5, 3.0)  # Realistic camera distance
            landmarks_quality = np.random.uniform(0.8, 0.95)
            
            measurements.append(MeasurementPoint(
                timestamp=frame_time,
                measurement_type=measurement_type,
                value=base_value,
                confidence=confidence,
                depth=depth,
                frame_id=frame_id,
                landmarks_quality=landmarks_quality
            ))
    
    return measurements


def create_dummy_mediapipe_landmarks() -> List[Tuple[float, float, float]]:
    """Create dummy MediaPipe landmarks for 3D normalization testing"""
    # MediaPipe 33-point pose landmarks with realistic 3D coordinates
    landmarks = np.array([
        (0.500, 0.100, 0.000),  # 0: nose
        (0.495, 0.095, 0.005),  # 1: left_eye_inner
        (0.490, 0.094, 0.010),  # 2: left_eye
        (0.485, 0.095, 0.000),  # 3: left_eye_outer
        (0.505, 0.095, 0.005),  # 4: right_eye_inner
        (0.510, 0.094, 0.010),  # 5: right_eye
        (0.515, 0.095, 0.000),  # 6: right_eye_outer
        (0.475, 0.105, -0.015), # 7: left_ear
        (0.525, 0.105, -0.015), # 8: right_ear
        (0.490, 0.120, 0.010),  # 9: mouth_left
        (0.510, 0.120, 0.010),  # 10: mouth_right
        (0.400, 0.250, 0.020),  # 11: left_shoulder
        (0.600, 0.250, 0.020),  # 12: right_shoulder
        (0.350, 0.350, 0.000),  # 13: left_elbow
        (0.650, 0.350, 0.000),  # 14: right_elbow
        (0.300, 0.450, -0.030), # 15: left_wrist
        (0.700, 0.450, -0.030), # 16: right_wrist
        (0.295, 0.470, -0.040), # 17: left_pinky
        (0.300, 0.465, -0.035), # 18: right_pinky
        (0.305, 0.460, -0.035), # 19: left_index
        (0.705, 0.470, -0.040), # 20: right_index
        (0.700, 0.465, -0.035), # 21: left_thumb
        (0.695, 0.460, -0.035), # 22: right_thumb
        (0.450, 0.750, 0.010),  # 23: left_hip
        (0.550, 0.750, 0.010),  # 24: right_hip
        (0.440, 0.850, 0.005),  # 25: left_knee
        (0.560, 0.850, 0.005),  # 26: right_knee
        (0.420, 1.050, 0.050),  # 27: left_ankle
        (0.580, 1.050, 0.050),  # 28: right_ankle
        (0.410, 1.070, 0.040),  # 29: left_heel
        (0.590, 1.070, 0.040),  # 30: right_heel
        (0.415, 1.100, 0.070),  # 31: left_foot_index
        (0.585, 1.100, 0.070),  # 32: right_foot_index
    ])
    
    return landmarks.tolist()


# =============================================================================
# Test Cases
# =============================================================================

class NormalizationTestSuite:
    """Comprehensive test suite for ErgoScan normalization system"""
    
    def __init__(self):
        self.normalizer = DataNormalizer()
        self.test_results = {}
        
    def run_all_tests(self):
        """Run all normalization tests"""
        print("ErgoScan Normalization - Comprehensive Test Suite")
        print("=" * 60)
        print("Testing 3D landmark normalization and data processing")
        print("=" * 60)
        
        # Run test modules
        self.test_data_normalization()
        self.test_landmark_normalization()
        self.test_real_time_processing()
        self.test_outlier_detection()
        self.test_rotation_correction()
        
        # Generate summary
        self.print_test_summary()
        
    def test_data_normalization(self):
        """Test basic data normalization with measurement data"""
        print("\n📊 TEST 1: Data Normalization & Measurement Processing")
        print("-" * 50)
        
        try:
            # Generate test data
            measurements = generate_sample_measurements(100)
            print(f"✅ Generated {len(measurements)} test measurements")
            
            # Process measurements
            body_profile, report = self.normalizer.process_measurements(measurements, "test_user")
            
            if body_profile:
                print(f"✅ Body profile created successfully")
                print(f"   Quality Score: {body_profile.calibration_quality:.2f}/10")
                print(f"   Measurements processed: {body_profile.measurement_count}")
                self.test_results['data_normalization'] = 'PASS'
            else:
                print("❌ Body profile creation failed")
                self.test_results['data_normalization'] = 'FAIL'
                
        except Exception as e:
            print(f"❌ Data normalization test failed: {e}")
            self.test_results['data_normalization'] = 'ERROR'
    
    def test_landmark_normalization(self):
        """Test 3D landmark normalization"""
        print("\n🎯 TEST 2: 3D Landmark Normalization")
        print("-" * 50)
        
        try:
            # Create test landmarks
            raw_landmarks = create_dummy_mediapipe_landmarks()
            print(f"✅ Created {len(raw_landmarks)} test landmarks")
            
            # Test different normalization configurations
            configs = [
                (None, 1.0, "Centroid-centered"),
                ("nose", 1.0, "Nose-centered"),
                ("chest", 1.0, "Chest-centered"),
                ("hip", 1.0, "Hip-centered")
            ]
            
            all_passed = True
            for center_point, target_height, config_name in configs:
                normalized = self.normalizer.normalize_landmarks(
                    landmarks=raw_landmarks,
                    center_point=center_point,
                    target_height=target_height
                )
                
                if normalized and len(normalized) == len(raw_landmarks):
                    coords = np.array(normalized)
                    height = np.max(coords[:, 1]) - np.min(coords[:, 1])
                    center = np.mean(coords, axis=0)
                    
                    # Validate normalization
                    height_ok = abs(height - target_height) < 0.2
                    center_ok = abs(center[0]) < 0.1 and abs(center[1]) < 0.1
                    
                    if height_ok and center_ok:
                        print(f"   ✅ {config_name}: Height={height:.3f}, Center=({center[0]:.3f},{center[1]:.3f},{center[2]:.3f})")
                    else:
                        print(f"   ⚠️  {config_name}: Height={height:.3f} (target: {target_height})")
                        all_passed = False
                else:
                    print(f"   ❌ {config_name}: Normalization failed")
                    all_passed = False
            
            self.test_results['landmark_normalization'] = 'PASS' if all_passed else 'PARTIAL'
            
        except Exception as e:
            print(f"❌ Landmark normalization test failed: {e}")
            self.test_results['landmark_normalization'] = 'ERROR'
    
    def test_rotation_correction(self):
        """Test rotation correction capability"""
        print("\n🔄 TEST 3: Rotation Correction")
        print("-" * 50)
        
        try:
            # Create tilted landmarks (rotated by 30 degrees)
            raw_landmarks = create_dummy_mediapipe_landmarks()
            angle = np.pi / 6  # 30 degrees
            cos_a, sin_a = np.cos(angle), np.sin(angle)
            
            tilted_landmarks = []
            for x, y, z in raw_landmarks:
                # Rotate in XY plane (Z-axis rotation)
                rotated_x = cos_a * (x - 0.5) - sin_a * (y - 0.5) + 0.5
                rotated_y = sin_a * (x - 0.5) + cos_a * (y - 0.5) + 0.5
                tilted_landmarks.append((rotated_x, rotated_y, z))
            
            # Normalize the tilted landmarks
            corrected = self.normalizer.normalize_landmarks(tilted_landmarks, target_height=1.0)
            
            if corrected and len(corrected) >= 13:
                coords = np.array(corrected)
                left_shoulder = coords[11]   # left_shoulder
                right_shoulder = coords[12]  # right_shoulder
                
                shoulder_angle = np.arctan2(
                    right_shoulder[1] - left_shoulder[1],
                    right_shoulder[0] - left_shoulder[0]
                )
                tilt_degrees = abs(np.degrees(shoulder_angle))
                
                print(f"   Original tilt: 30°")
                print(f"   Corrected tilt: {tilt_degrees:.1f}°")
                
                if tilt_degrees < 10:  # Should be nearly horizontal
                    print("   ✅ Rotation correction successful")
                    self.test_results['rotation_correction'] = 'PASS'
                else:
                    print("   ⚠️  Rotation correction needs improvement")
                    self.test_results['rotation_correction'] = 'PARTIAL'
            else:
                print("   ❌ Not enough landmarks for rotation test")
                self.test_results['rotation_correction'] = 'FAIL'
                
        except Exception as e:
            print(f"❌ Rotation correction test failed: {e}")
            self.test_results['rotation_correction'] = 'ERROR'
    
    def test_real_time_processing(self):
        """Test real-time processing simulation"""
        print("\n⚡ TEST 4: Real-time Processing Simulation")
        print("-" * 50)
        
        try:
            quality_scores = []
            
            # Simulate real-time measurement collection
            for frame in [10, 20, 30]:
                measurements = generate_sample_measurements(frame)
                body_profile, report = self.normalizer.process_measurements(measurements, f"rt_user_{frame}")
                
                if body_profile:
                    quality_scores.append(body_profile.calibration_quality)
                    print(f"   Frame {frame}: Quality = {body_profile.calibration_quality:.2f}/10")
            
            if quality_scores:
                avg_quality = np.mean(quality_scores)
                if avg_quality > 7.0:
                    print(f"✅ Real-time processing: Average quality = {avg_quality:.2f}/10")
                    self.test_results['real_time_processing'] = 'PASS'
                else:
                    print(f"⚠️  Real-time processing: Quality below threshold = {avg_quality:.2f}/10")
                    self.test_results['real_time_processing'] = 'PARTIAL'
            else:
                print("❌ Real-time processing: No valid profiles generated")
                self.test_results['real_time_processing'] = 'FAIL'
                
        except Exception as e:
            print(f"❌ Real-time processing test failed: {e}")
            self.test_results['real_time_processing'] = 'ERROR'
    
    def test_outlier_detection(self):
        """Test outlier detection capabilities"""
        print("\n🎯 TEST 5: Outlier Detection")
        print("-" * 50)
        
        try:
            # Generate measurements with known outliers
            measurements = generate_sample_measurements(50)
            
            # Add obvious outliers
            outlier_indices = [10, 20, 30]
            for idx in outlier_indices:
                measurements[idx * 6].value = 600.0  # Height outlier
                
            print(f"✅ Added {len(outlier_indices)} outliers to test data")
            
            # Process with outlier detection
            body_profile, report = self.normalizer.process_measurements(measurements, "outlier_test")
            
            if body_profile:
                steps = report.get('processing_steps', [])
                outlier_step = [step for step in steps if 'outlier' in step.lower()]
                
                if outlier_step:
                    print(f"✅ Outlier detection active: {outlier_step[0]}")
                    print(f"   Final quality score: {body_profile.calibration_quality:.2f}/10")
                    self.test_results['outlier_detection'] = 'PASS'
                else:
                    print("⚠️  Outlier detection step not found in processing")
                    self.test_results['outlier_detection'] = 'PARTIAL'
            else:
                print("❌ Outlier detection test: Profile creation failed")
                self.test_results['outlier_detection'] = 'FAIL'
                
        except Exception as e:
            print(f"❌ Outlier detection test failed: {e}")
            self.test_results['outlier_detection'] = 'ERROR'
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed = sum(1 for result in self.test_results.values() if result == 'PASS')
        partial = sum(1 for result in self.test_results.values() if result == 'PARTIAL')
        failed = sum(1 for result in self.test_results.values() if result in ['FAIL', 'ERROR'])
        
        for test_name, result in self.test_results.items():
            status_icon = {
                'PASS': '✅',
                'PARTIAL': '⚠️ ',
                'FAIL': '❌',
                'ERROR': '💥'
            }.get(result, '❓')
            
            print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result}")
        
        print("-" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed}")
        print(f"Partial: {partial}")
        print(f"Failed: {failed}")
        
        if failed == 0:
            if partial == 0:
                print("\n🎉 ALL TESTS PASSED! Normalization system is ready for production.")
            else:
                print(f"\n✅ Tests completed with {partial} partial passes. System is functional.")
        else:
            print(f"\n⚠️  {failed} tests failed. Review errors before deployment.")


# =============================================================================
# Main Test Runner
# =============================================================================

def main():
    """Main test runner"""
    try:
        test_suite = NormalizationTestSuite()
        test_suite.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()