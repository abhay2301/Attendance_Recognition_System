import cv2
import threading
import time
from queue import Queue
import numpy as np

class CameraStream:
    def __init__(self, camera_id=0):
        self.camera_id = camera_id
        self.cap = None
        self.frame = None
        self.latest_frame = None
        self.is_running = False
        self.thread = None
        self.frame_queue = Queue(maxsize=1)
        self.lock = threading.Lock()
        
    def start(self):
        """Start camera stream"""
        if self.is_running:
            return True
            
        try:
            self.cap = cv2.VideoCapture(self.camera_id, cv2.CAP_DSHOW)  # Use DirectShow backend for better performance on Windows
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            if not self.cap.isOpened():
                print(f"Error: Could not open camera {self.camera_id}")
                return False
            
            self.is_running = True
            self.thread = threading.Thread(target=self._update_frame, daemon=True)
            self.thread.start()
            print(f"Camera {self.camera_id} started successfully")
            return True
            
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False
    
    def _update_frame(self):
        """Update frame in background thread"""
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        self.frame = frame.copy()
                        self.latest_frame = frame.copy()
                        
                        # Update queue if needed
                        if self.frame_queue.full():
                            self.frame_queue.get_nowait()
                        self.frame_queue.put(frame.copy())
                else:
                    print("Warning: Failed to read frame from camera")
                    time.sleep(0.1)
            except Exception as e:
                print(f"Error in camera thread: {e}")
                time.sleep(0.1)
    
    def get_frame(self):
        """Get latest frame"""
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()
        return None
    
    def get_latest_frame(self):
        """Get frame from queue (non-blocking)"""
        try:
            return self.frame_queue.get_nowait()
        except:
            return None
    
    def stop(self):
        """Stop camera stream"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()
        print(f"Camera {self.camera_id} stopped")
    
    def is_opened(self):
        """Check if camera is opened"""
        return self.is_running and self.cap is not None
    
    def list_cameras(self, max_to_check=5):
        """List available cameras"""
        available_cameras = []
        for i in range(max_to_check):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        return available_cameras
    
    def capture_photo(self):
        """Capture a single photo"""
        frame = self.get_frame()
        if frame is not None:
            # Save to temporary file
            filename = f"capture_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            return frame, filename
        return None, None

# Global camera instances
cameras = {}

def get_camera(camera_id=0):
    """Get or create camera instance"""
    if camera_id not in cameras:
        cameras[camera_id] = CameraStream(camera_id)
    return cameras[camera_id]

def release_all_cameras():
    """Release all camera resources"""
    for cam in cameras.values():
        cam.stop()
    cameras.clear()