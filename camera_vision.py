import cv2
import base64
import logging
import tempfile
import os
from typing import Optional

logger = logging.getLogger(__name__)

class CameraVision:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.camera = None
        self._initialize_camera()
    
    def _initialize_camera(self):
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                self.camera = None
            else:
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            self.camera = None
    
    def capture_image(self) -> Optional[str]:
        if not self.camera or not self.camera.isOpened():
            return None
        
        try:
            # Flush buffer
            for _ in range(3):
                self.camera.read()
            
            ret, frame = self.camera.read()
            if not ret or frame is None:
                return None
            
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_path = temp_file.name
            temp_file.close()
            
            cv2.imwrite(temp_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            return temp_path
            
        except Exception:
            return None
    
    def is_available(self) -> bool:
        return self.camera is not None and self.camera.isOpened()
    
    def release(self):
        if self.camera:
            self.camera.release()
