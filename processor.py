# processor.py
import cv2
import numpy as np
import base64
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_blur(b64_tile):
    """
    Apply a very strong Gaussian blur to the received image tile.
    
    Args:
        b64_tile: Base64 encoded image data
        
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
        
        # 🔥 Apply a stronger Gaussian blur (51x51 kernel)
        try:
            blurred = cv2.GaussianBlur(img, (51, 51), 0)
        except Exception as e:
            raise Exception(f"Gaussian blur failed: {e}")
        
        # Encode back to JPEG
        try:
            success, buf = cv2.imencode('.jpg', blurred)
            if not success:
                raise Exception("cv2.imencode failed to encode image")
        except Exception as e:
            raise Exception(f"Image encoding failed: {e}")
        
        # Convert to base64
        try:
            b64_blurred = base64.b64encode(buf).decode('utf-8')
        except Exception as e:
            raise Exception(f"Base64 encoding failed: {e}")
        
        if not b64_blurred:
            raise ValueError("Result is empty after encoding")
        
        logger.debug(f"✓ Successfully processed tile (output size: {len(b64_blurred)} chars)")
        return b64_blurred
        
    except ValueError as ve:
        logger.error(f"❌ Validation error in process_blur: {ve}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error in process_blur: {e}")
        logger.debug(f"Input data length: {len(b64_tile) if b64_tile else 0}")
        raise
