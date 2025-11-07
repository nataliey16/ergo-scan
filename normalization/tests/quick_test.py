#!/usr/bin/env python3
"""
ErgoScan - Quick Landmark Normalization Test

A simple, fast test for validating 3D landmark normalization functionality.
For comprehensive testing, use normalization.tests.test_suite.

Usage:
    python normalization/tests/quick_test.py
    
Author: ErgoScan Team
Version: 2.0.0 (3D Enhanced)
"""

import sys
import os
from typing import List, Tuple

import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from data_normalizer import DataNormalizer
    print("✅ DataNormalizer imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def create_simple_pose() -> List[Tuple[float, float, float]]:
    """Create a simple standing pose for quick testing"""
    # MediaPipe 33-point pose with basic standing position
    landmarks = [(0.5, 0.5, 0.02)] * 33  # Initialize all landmarks
    
    # Set key landmarks in proper positions (x, y, z)
    landmarks[0] = (0.5, 0.1, 0.05)     # nose
    landmarks[11] = (0.4, 0.25, 0.02)   # left_shoulder  
    landmarks[12] = (0.6, 0.25, 0.02)   # right_shoulder
    landmarks[23] = (0.45, 0.75, 0.01)  # left_hip
    landmarks[24] = (0.55, 0.75, 0.01)  # right_hip
    landmarks[27] = (0.42, 1.0, 0.0)    # left_ankle
    landmarks[28] = (0.58, 1.0, 0.0)    # right_ankle
    
    return landmarks


def quick_test_normalize_landmarks():
    """Quick test of landmark normalization"""
    print("\n🧪 Quick Landmark Normalization Test")
    print("-" * 40)
    
    # Create normalizer
    normalizer = DataNormalizer()
    
    # Create simple pose
    raw_landmarks = create_simple_pose()
    print(f"✅ Created pose with {len(raw_landmarks)} landmarks")
    
    # Test normalization
    try:
        normalized = normalizer.normalize_landmarks(
            landmarks=raw_landmarks,
            target_height=1.0
        )
        
        if normalized:
            coords = np.array(normalized)
            height = np.max(coords[:, 1]) - np.min(coords[:, 1])
            center = np.mean(coords, axis=0)
            
            print(f"✅ Normalization successful")
            print(f"   Height: {height:.3f} (target: 1.0)")
            print(f"   Center: ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})")
            
            # Show key normalized landmarks
            key_landmarks = {
                'Nose': coords[0],
                'Shoulders': np.mean([coords[11], coords[12]], axis=0),
                'Hips': np.mean([coords[23], coords[24]], axis=0),
                'Ankles': np.mean([coords[27], coords[28]], axis=0)
            }
            
            for name, pos in key_landmarks.items():
                print(f"   {name:9}: ({pos[0]:6.3f}, {pos[1]:6.3f}, {pos[2]:6.3f})")
            
            # Validate results
            height_ok = abs(height - 1.0) < 0.2
            center_ok = abs(center[0]) < 0.1 and abs(center[1]) < 0.1
            
            if height_ok and center_ok:
                print("✅ Validation passed")
                return True
            else:
                print("⚠️  Validation needs review")
                return False
        else:
            print("❌ Normalization returned empty result")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def quick_test_rotation():
    """Quick test of rotation correction"""
    print("\n🔄 Quick Rotation Correction Test")
    print("-" * 40)
    
    normalizer = DataNormalizer()
    raw_landmarks = create_simple_pose()
    
    # Create tilted pose (30 degree rotation)
    angle = np.pi / 6
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    
    tilted_landmarks = []
    for x, y, z in raw_landmarks:
        rotated_x = cos_a * (x - 0.5) - sin_a * (y - 0.5) + 0.5
        rotated_y = sin_a * (x - 0.5) + cos_a * (y - 0.5) + 0.5
        tilted_landmarks.append((rotated_x, rotated_y, z))
    
    try:
        corrected = normalizer.normalize_landmarks(tilted_landmarks)
        
        if corrected and len(corrected) >= 13:
            coords = np.array(corrected)
            left_shoulder = coords[11]
            right_shoulder = coords[12]
            
            shoulder_angle = np.arctan2(
                right_shoulder[1] - left_shoulder[1],
                right_shoulder[0] - left_shoulder[0]
            )
            tilt_degrees = abs(np.degrees(shoulder_angle))
            
            print(f"   Original tilt: 30.0°")
            print(f"   Corrected tilt: {tilt_degrees:.1f}°")
            
            if tilt_degrees < 10:
                print("✅ Rotation correction successful")
                return True
            else:
                print("⚠️  Rotation correction needs improvement")
                return False
        else:
            print("❌ Insufficient landmarks for rotation test")
            return False
            
    except Exception as e:
        print(f"❌ Rotation test failed: {e}")
        return False


def main():
    """Main quick test function"""
    print("ErgoScan - Quick Landmark Normalization Test")
    print("=" * 50)
    
    test1 = quick_test_normalize_landmarks()
    test2 = quick_test_rotation()
    
    print("\n" + "=" * 50)
    if test1 and test2:
        print("🎉 All quick tests passed!")
        print("\nFor comprehensive testing, run:")
        print("  python normalization/tests/test_suite.py")
    else:
        print("⚠️  Some tests failed. Check errors above.")
        print("\nFor detailed diagnostics, run:")
        print("  python normalization/tests/test_suite.py")


if __name__ == "__main__":
    main()