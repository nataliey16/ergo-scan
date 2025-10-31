# ErgoScan Data Normalization & Refinement Package

This package provides comprehensive data normalization and refinement capabilities for the ErgoScan body measurement system.

## Overview

The normalization package implements Step 3 of the ErgoScan project: cleaning, normalizing, and validating measurement data to ensure consistent accuracy across different scanning conditions.

## Features

- **Outlier Detection**: Z-score and IQR-based outlier removal
- **Temporal Smoothing**: Weighted averaging across multiple frames
- **Quality Scoring**: Comprehensive quality assessment (0-10 scale)
- **Confidence Weighting**: Measurements weighted by detection confidence
- **Depth Correction**: Adjustments based on estimated depth
- **Calibration Scaling**: Integration with existing calibration data
- **Real-time Processing**: Handles continuous measurement streams
- **Landmark Normalization**: MediaPipe landmark centering, rotation, and scaling

## Package Structure

```
normalization/
├── __init__.py               # Package initialization and exports
├── data_normalizer.py        # Core normalization algorithms
├── scan_processor.py         # MediaPipe integration and real-time processing
├── requirements.txt          # Package dependencies
├── README.md                # This file
└── tests/
    ├── __init__.py          # Test package initialization  
    └── test_normalization.py # Comprehensive test suite
```

## Classes

### MeasurementPoint
Data structure for individual measurement points containing:
- Timestamp and frame information
- Measurement type and value
- Confidence and quality metrics
- Depth information

### BodyProfile  
Refined body profile with normalized measurements:
- All 6 body measurement types
- Quality scores and metadata
- Scale factors and calibration data

### DataNormalizer
Main processing pipeline with methods for:
- Outlier detection and removal
- Temporal smoothing and averaging
- Depth correction and calibration scaling
- Quality assessment and validation
- **MediaPipe landmark normalization** (centering, rotation, scaling)

### ErgoScanProcessor
Real-time integration processor that:
- Connects with MediaPipe pose detection
- Manages measurement collection sessions
- Provides live processing capabilities

## Usage

### Basic Usage

```python
from normalization import DataNormalizer, MeasurementPoint, BodyProfile

# Initialize normalizer
normalizer = DataNormalizer()

# Process measurements
body_profile, report = normalizer.process_measurements(measurements, "user_id")

# Check quality
print(f"Quality Score: {body_profile.calibration_quality:.2f}/10")
```

### Real-time Integration

```python
from normalization import ErgoScanProcessor

# Initialize processor
processor = ErgoScanProcessor()

# Start scanning session
processor.start_scanning_session()

# Process frames (in your camera loop)
processed_frame, measurements = processor.process_frame(frame)

# End session and get refined profile
body_profile, report = processor.end_scanning_session("user_id")
```

## Installation

1. Install dependencies:
   ```bash
   pip install -r normalization/requirements.txt
   ```

2. For MediaPipe support (optional):
   ```bash
   pip install mediapipe>=0.10.0
   ```

## Testing

Run the comprehensive test suite:

```python
python normalization/tests/test_normalization.py
```

The test suite includes:
- Basic data normalization testing
- Real-time processing simulation
- Outlier detection validation
- Performance benchmarking

## Integration with ErgoScan

The normalization package is designed to integrate seamlessly with:

- **mainScreen.py**: Main GUI interface
- **calibration_instructions.py**: Calibration system
- **MediaPipe pose detection**: Real-time landmark processing
- **Profile management**: Enhanced measurement accuracy

### Example Integration

```python
# In your main scanning logic
from normalization import ErgoScanProcessor

class ErgoScanMain:
    def __init__(self):
        self.processor = ErgoScanProcessor()
    
    def start_scan(self, user_id):
        self.processor.start_scanning_session()
        # Your existing camera loop here
        # Call processor.process_frame(frame) for each frame
        
    def finish_scan(self, user_id):
        body_profile, report = self.processor.end_scanning_session(user_id)
        
        # Use the refined measurements
        if body_profile.calibration_quality >= 7.0:
            # High quality measurements - proceed with confidence
            self.save_user_profile(body_profile)
        else:
            # Lower quality - may need re-scan
            self.handle_low_quality_scan(body_profile, report)
```

## Quality Metrics

The system provides comprehensive quality assessment:

- **Sample Score**: Based on number of measurements collected
- **Consistency Score**: Based on measurement variability (CV)
- **Detection Score**: Based on confidence and landmark quality
- **Completeness Score**: Based on measurement type coverage

Quality scores range from 0-10, with recommendations:
- **9-10**: Excellent quality, high confidence
- **7-8**: Good quality, reliable measurements  
- **5-6**: Acceptable quality, consider re-scan for critical applications
- **0-4**: Poor quality, re-scan recommended

## Performance

- **Processing Speed**: Sub-millisecond processing times
- **Memory Usage**: Efficient sliding window buffer management
- **Real-time Capability**: Suitable for live camera feeds at 30+ FPS
- **Scalability**: Handles measurement sessions of any length

## Configuration

The normalizer can be configured through parameters:

```python
normalizer = DataNormalizer(
    calibration_file="custom_calibration.json",  # Custom calibration
    outlier_threshold=2.5,  # Z-score threshold for outliers
    min_confidence=0.5,     # Minimum detection confidence
    min_samples=5           # Minimum samples for processing
)
```

## Error Handling

The package includes comprehensive error handling:
- Graceful degradation when dependencies unavailable
- Validation of input data and parameters  
- Detailed error reporting and logging
- Recovery mechanisms for processing failures

## Future Enhancements

Planned improvements include:
- Advanced depth estimation integration (Depth Anything)
- Machine learning-based outlier detection
- Adaptive quality thresholds
- Enhanced temporal smoothing algorithms
- Support for additional measurement types

## Support

For questions or issues with the normalization package:
1. Check the test suite for usage examples
2. Review the comprehensive docstrings in the source code
3. Examine the processing reports for debugging information