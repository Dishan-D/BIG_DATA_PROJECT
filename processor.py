# processor.py
import cv2
import numpy as np
import base64

def process_blur(b64_tile):
    """Apply a very strong Gaussian blur to the received image tile."""
    # Decode base64 → bytes → NumPy array
    img_data = base64.b64decode(b64_tile)
    np_arr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # 🔥 Apply a stronger Gaussian blur
    # (51x51 kernel gives very strong blur)
    blurred = cv2.GaussianBlur(img, (51, 51), 0)

    # Encode back to base64
    _, buf = cv2.imencode('.jpg', blurred)
    b64_blurred = base64.b64encode(buf).decode('utf-8')

    return b64_blurred
