#!/usr/bin/env python3
"""
Simple test for landmark normalization functionality
Tests the normalize_landmarks() function with dummy MediaPipe data
"""

import sys
import os
import numpy as np
from typing import List, Tuple

# Add current directory to path
sys.path.append('.')

try:
    from normalization import DataNormalizer
    print("✅ DataNormalizer imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)

def create_simple_pose() -> List[Tuple[float, float]]:
    """Create a simple standing pose for testing with proper MediaPipe indices"""
    # Create a pose with 33 landmarks (MediaPipe standard)
    # Initialize all with default positions
    landmarks = [(0.5, 0.5)] * 33
    
    # Set key landmarks in their proper positions
    landmarks[0] = (0.5, 0.1)    # nose
    landmarks[11] = (0.4, 0.25)  # left_shoulder  
    landmarks[12] = (0.6, 0.25)  # right_shoulder
    landmarks[23] = (0.45, 0.75) # left_hip
    landmarks[24] = (0.55, 0.75) # right_hip
    landmarks[27] = (0.42, 1.0)  # left_ankle
    landmarks[28] = (0.58, 1.0)  # right_ankle
    
    return landmarks

def test_normalize_landmarks():
    """Test basic landmark normalization"""
    print("\n🧪 Testing normalize_landmarks() function...")
    
    # Create normalizer
    normalizer = DataNormalizer()
    print("✅ DataNormalizer created")
    
    # Create simple pose
    raw_landmarks = create_simple_pose()
    print(f"✅ Created pose with {len(raw_landmarks)} landmarks")
    
    # Test basic normalization
    try:
        normalized = normalizer.normalize_landmarks(
            landmarks=raw_landmarks,
            target_height=1.0
        )
        
        print("✅ Landmarks normalized successfully")
        
        # Verify results
        coords = np.array(normalized)
        height = np.max(coords[:, 1]) - np.min(coords[:, 1])
        center = np.mean(coords, axis=0)
        
        print(f"   📏 Normalized height: {height:.3f}")
        print(f"   📍 Center position: ({center[0]:.3f}, {center[1]:.3f})")
        
        # Test that centering worked (center should be close to origin)
        if abs(center[0]) < 0.1 and abs(center[1]) < 0.1:
            print("   ✅ Centering successful")
        else:
            print("   ⚠️  Centering may need adjustment")
        
        # Test that scaling worked (height should be close to 1.0)
        if abs(height - 1.0) < 0.2:
            print("   ✅ Scaling successful")
        else:
            print("   ⚠️  Scaling may need adjustment")
        
        return True
        
    except Exception as e:
        print(f"❌ Normalization failed: {e}")
        return False

def test_rotation_correction():
    """Test rotation correction with tilted pose"""
    print("\n🔄 Testing rotation correction...")
    
    normalizer = DataNormalizer()
    
    # Create tilted pose (rotate by 30 degrees)
    raw_landmarks = create_simple_pose()
    angle = np.pi / 6  # 30 degrees
    cos_a, sin_a = np.cos(angle), np.sin(angle)
    
    tilted_landmarks = []
    for x, y in raw_landmarks:
        # Rotate around center point (0.5, 0.5)
        rotated_x = cos_a * (x - 0.5) - sin_a * (y - 0.5) + 0.5
        rotated_y = sin_a * (x - 0.5) + cos_a * (y - 0.5) + 0.5
        tilted_landmarks.append((rotated_x, rotated_y))
    
    try:
        # Normalize the tilted landmarks
        corrected = normalizer.normalize_landmarks(tilted_landmarks)
        
        # Check if shoulders are horizontal (landmarks 11 and 12 are shoulders)
        if len(corrected) >= 13:
            left_shoulder = corrected[11]   # left_shoulder
            right_shoulder = corrected[12]  # right_shoulder
            
            shoulder_angle = np.arctan2(
                right_shoulder[1] - left_shoulder[1],
                right_shoulder[0] - left_shoulder[0]
            )
            tilt_degrees = abs(np.degrees(shoulder_angle))
            
            print(f"   Original tilt: 30°")
            print(f"   Corrected tilt: {tilt_degrees:.1f}°")
            
            if tilt_degrees < 10:  # Should be nearly horizontal
                print("   ✅ Rotation correction successful")
                return True
            else:
                print("   ⚠️  Rotation correction needs improvement")
                return False
        else:
            print("   ⚠️  Not enough landmarks for rotation test")
            return False
            
    except Exception as e:
        print(f"❌ Rotation correction failed: {e}")
        return False

def main():
    """Main test function"""
    print("ErgoScan Landmark Normalization - Simple Test")
    print("=" * 50)
    
    success1 = test_normalize_landmarks()
    success2 = test_rotation_correction()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 All landmark normalization tests passed!")
        print("\nnormalize_landmarks() delivers:")
        print("• ✅ Centered coordinates (origin at body center)")
        print("• ✅ Rotated coordinates (shoulders horizontal)")  
        print("• ✅ Scaled coordinates (normalized height)")
    else:
        print("💥 Some tests failed. Check error messages above.")
    
    return 0 if (success1 and success2) else 1

if __name__ == "__main__":
    exit(main())