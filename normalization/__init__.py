"""
ErgoScan Data Normalization & Refinement Package
===============================================

This package provides comprehensive data normalization and refinement capabilities
for the ErgoScan body measurement system.

Modules:
    data_normalizer: Core normalization algorithms and data structures
    scan_processor: Integration with MediaPipe and real-time processing
    tests.test_normalization: Comprehensive test suite

Classes:
    MeasurementPoint: Individual measurement data point
    BodyProfile: Refined body profile with normalized measurements  
    DataNormalizer: Main processing pipeline
    ErgoScanProcessor: Real-time integration processor
"""

from .data_normalizer import DataNormalizer, MeasurementPoint, BodyProfile
from .scan_processor import ErgoScanProcessor, LiveScanningDemo

__version__ = "1.0.0"
__author__ = "ErgoScan Development Team"

__all__ = [
    'DataNormalizer',
    'MeasurementPoint', 
    'BodyProfile',
    'ErgoScanProcessor',
    'LiveScanningDemo'
]