import cv2
import os
import time
import threading
import sys
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.common.config import CAMERA_IPS, get_rtsp_url

# Force TCP and set a socket timeout (in microseconds). 
# 5000000 = 5 seconds. This prevents infinite blocking on dead streams.
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;5000000"

def get_stream_url(ip, sub_stream=True):
    path = "/live/ch1" if sub_stream else "/live/ch0"
    return get_rtsp_url(ip, path)

class VideoCaptureThread:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.cap = cv2.VideoCapture(self.url)
        self.ret = False
        self.frame = None
        self.running = True
        
        if self.cap.isOpened():
            # Start the background thread
            self.thread = threading.Thread(target=self.update, args=())
            self.thread.daemon = True
            self.thread.start()

    def update(self):
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                self.ret = ret
                if ret:
                    self.frame = frame
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.1)

    def read(self):
        return self.ret, self.frame

    def release(self):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1.0)
        self.cap.release()

def main():
    print(f"Starting Live Viewer for cameras: {CAMERA_IPS}")
    
    viewers = []
    
    # Attempt to initialize both cameras
    for i, ip in enumerate(CAMERA_IPS):
        if not ip: continue
        
        url = get_stream_url(ip, sub_stream=True)
        print(f"Connecting to Camera {i+1} ({ip})...")
        
        viewer = VideoCaptureThread(f"Camera {i+1}", url)
        # Give it a moment to stabilize
        time.sleep(1.5)
        
        ret, _ = viewer.read()
        if ret:
            print(f"SUCCESS: Connected to {ip}")
            viewers.append(viewer)
        else:
            print(f"FAILED: Could not get frame from {ip}. Trying main stream...")
            viewer.release()
            
            url_main = get_stream_url(ip, sub_stream=False)
            viewer = VideoCaptureThread(f"Camera {i+1}", url_main)
            time.sleep(1.5)
            ret, _ = viewer.read()
            if ret:
                print(f"SUCCESS: Connected to {ip} (Main Stream)")
                viewers.append(viewer)
            else:
                viewer.release()
                print(f"ERROR: Complete failure connecting to {ip}")

    if not viewers:
        print("\nCould not connect to any camera. Please check your .env file and network.")
        return

    print("\nControls: 'q' to quit, 's' to save snapshot")
    
    try:
        while True:
            for viewer in viewers:
                ret, frame = viewer.read()
                if ret and frame is not None:
                    # Resize for display if needed
                    display_frame = cv2.resize(frame, (640, 360))
                    cv2.imshow(viewer.name, display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                for viewer in viewers:
                    ret, frame = viewer.read()
                    if ret:
                        fn = f"snapshot_{viewer.name}_{ts}.jpg"
                        cv2.imwrite(fn, frame)
                        print(f"Saved: {fn}")

    finally:
        for viewer in viewers:
            viewer.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
