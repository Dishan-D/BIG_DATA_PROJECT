#!/usr/bin/env python3
"""
Test script to verify image transformations work correctly.
Creates test images showing before/after for each transformation.
"""

import cv2
import numpy as np
from processor import apply_gaussian_blur, apply_grayscale, apply_invert

def create_test_pattern():
    """Create a simple test image with colors and patterns."""
    img = np.zeros((512, 512, 3), dtype=np.uint8)
    
    # Red square
    img[50:200, 50:200] = [0, 0, 255]
    
    # Green square
    img[50:200, 312:462] = [0, 255, 0]
    
    # Blue square
    img[312:462, 50:200] = [255, 0, 0]
    
    # Yellow square
    img[312:462, 312:462] = [0, 255, 255]
    
    # White text area
    cv2.putText(img, "TEST", (200, 280), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
    
    return img

def test_transformations():
    """Test all transformations and save results."""
    print("Creating test image...")
    img = create_test_pattern()
    
    # Save original
    cv2.imwrite("test_original.jpg", img)
    print("✓ Saved: test_original.jpg")
    
    # Test blur
    print("\nTesting BLUR...")
    blurred = apply_gaussian_blur(img)
    cv2.imwrite("test_blur.jpg", blurred)
    print("✓ Saved: test_blur.jpg")
    
    if np.array_equal(img, blurred):
        print("❌ ERROR: Blur did NOT change the image!")
    else:
        print("✅ Blur successfully changed the image")
    
    # Test grayscale
    print("\nTesting GRAYSCALE...")
    gray = apply_grayscale(img)
    cv2.imwrite("test_grayscale.jpg", gray)
    print("✓ Saved: test_grayscale.jpg")
    
    if np.array_equal(img, gray):
        print("❌ ERROR: Grayscale did NOT change the image!")
    else:
        print("✅ Grayscale successfully changed the image")
    
    # Test invert
    print("\nTesting INVERT...")
    inverted = apply_invert(img)
    cv2.imwrite("test_invert.jpg", inverted)
    print("✓ Saved: test_invert.jpg")
    
    if np.array_equal(img, inverted):
        print("❌ ERROR: Invert did NOT change the image!")
    else:
        print("✅ Invert successfully changed the image")
    
    # Test combination
    print("\nTesting COMBINATION (Grayscale + Invert)...")
    combined = apply_invert(apply_grayscale(img))
    cv2.imwrite("test_combined.jpg", combined)
    print("✓ Saved: test_combined.jpg")
    
    print("\n" + "="*50)
    print("✅ Test complete! Check the output images:")
    print("   - test_original.jpg")
    print("   - test_blur.jpg (should be blurry)")
    print("   - test_grayscale.jpg (should be black & white)")
    print("   - test_invert.jpg (should be negative colors)")
    print("   - test_combined.jpg (should be negative B&W)")
    print("="*50)

if __name__ == "__main__":
    test_transformations()
