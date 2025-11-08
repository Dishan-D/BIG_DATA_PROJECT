# processor.py
import cv2
import numpy as np
import base64
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== INDIVIDUAL TRANSFORMATIONS ====================

def apply_gaussian_blur(img):
    """Apply Gaussian blur."""
    return cv2.GaussianBlur(img, (31, 31), 0)


def apply_grayscale(img):
    """Convert to grayscale."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def apply_invert(img):
    """Invert colors (negative)."""
    return cv2.bitwise_not(img)


# ==================== MAIN PROCESSING FUNCTION ====================

def process_image(b64_tile, transformations):
    """
    Apply multiple transformations to an image tile.
    
    Args:
        b64_tile: Base64 encoded image data
        transformations: List of transformation names to apply
        
    Returns:
        Base64 encoded processed image
        
    Raises:
        ValueError: If tile data is invalid
        Exception: For other processing errors
    """
    try:
        if not b64_tile:
            raise ValueError("Empty tile data received")
        
        # Decode base64 → bytes
        try:
            img_data = base64.b64decode(b64_tile)
        except Exception as e:
            raise ValueError(f"Failed to decode base64 data: {e}")
        
        if len(img_data) == 0:
            raise ValueError("Decoded image data is empty")
        
        # bytes → NumPy array
        np_arr = np.frombuffer(img_data, np.uint8)
        
        if len(np_arr) == 0:
            raise ValueError("NumPy array is empty")
        
        # Decode image
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode image - cv2.imdecode returned None")
        
        if img.size == 0:
            raise ValueError("Decoded image has zero size")
        
        logger.debug(f"Processing image tile: shape={img.shape}, dtype={img.dtype}")
        logger.info(f"🎨 Applying transformations: {transformations}")
        
        # Apply transformations in sequence
        processed = img.copy()
        
        if not transformations or len(transformations) == 0:
            logger.warning(f"⚠️ No transformations specified! Returning original image.")
            # Return original image if no transformations
        else:
            for transform in transformations:
                try:
                    logger.info(f"  → Applying: {transform}")
                    if transform == 'blur':
                        processed = apply_gaussian_blur(processed)
                        logger.info(f"  ✓ Blur applied")
                    elif transform == 'grayscale':
                        processed = apply_grayscale(processed)
                        logger.info(f"  ✓ Grayscale applied")
                    elif transform == 'invert':
                        processed = apply_invert(processed)
                        logger.info(f"  ✓ Invert applied")
                    else:
                        logger.warning(f"Unknown transformation: {transform}")
                        
                except Exception as e:
                    logger.error(f"Failed to apply {transform}: {e}")
                    # Continue with other transformations
        
        # Encode back to JPEG
        try:
            success, buf = cv2.imencode('.jpg', processed)
            if not success:
                raise Exception("cv2.imencode failed to encode image")
        except Exception as e:
            raise Exception(f"Image encoding failed: {e}")
        
        # Convert to base64
        try:
            b64_processed = base64.b64encode(buf).decode('utf-8')
        except Exception as e:
            raise Exception(f"Base64 encoding failed: {e}")
        
        if not b64_processed:
            raise ValueError("Result is empty after encoding")
        
        logger.debug(f"✓ Successfully processed tile with {len(transformations)} transformations")
        return b64_processed
        
    except ValueError as ve:
        logger.error(f"❌ Validation error in process_image: {ve}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in process_image: {e}")
        logger.debug(f"Input data length: {len(b64_tile) if b64_tile else 0}")
        raise


# ==================== BACKWARD COMPATIBILITY ====================

def process_blur(b64_tile):
    """Legacy function for backward compatibility."""
    return process_image(b64_tile, ['blur'])
