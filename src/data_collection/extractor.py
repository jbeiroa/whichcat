import cv2
import os
import time
import threading
import numpy as np
from datetime import datetime
from ultralytics import YOLO
from src.common.config import get_rtsp_url, CAMERA_IPS
from src.common.logging import get_logger

logger = get_logger(__name__)

# Force TCP for RTSP
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;5000000"

class RTSPExtractor:
    def __init__(self, output_dir="data/raw/unlabeled", model_name="yolov8s.pt", cooldown=0.5, padding=30):
        self.output_dir = output_dir
        self.cooldown = cooldown
        self.padding = padding
        self.model = YOLO(model_name)
        self.running = False
        self.threads = []
        self.last_saved = {}
        
        # CLAHE for night vision enhancement
        self.clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))

        os.makedirs(self.output_dir, exist_ok=True)

    def enhance_frame(self, frame):
        """Enhance contrast, especially useful for night vision."""
        # Convert to LAB color space
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L-channel
        cl = self.clahe.apply(l)
        
        # Merge back and convert to BGR
        limg = cv2.merge((cl, a, b))
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        return enhanced

    def _process_camera(self, ip):
        # Use path="/live/ch0" for the high-definition main stream
        url = get_rtsp_url(ip, path="/live/ch0")
        logger.info(f"Starting extraction for {ip} from {url}")
        
        cap = cv2.VideoCapture(url)
        if not cap.isOpened():
            logger.error(f"Could not open stream for {ip}")
            return

        self.last_saved[ip] = 0
        
        while self.running:
            ret, frame = cap.read()
            if not ret or frame is None:
                logger.warning(f"Failed to read frame from {ip}. Retrying...")
                cap.release()
                time.sleep(5)
                cap = cv2.VideoCapture(url)
                continue

            current_time = time.time()
            if current_time - self.last_saved.get(ip, 0) < self.cooldown:
                continue

            # Enhance frame for better detection in low light
            enhanced = self.enhance_frame(frame)

            # Run inference with a lower confidence threshold for small/blurry cats
            results = self.model(enhanced, classes=[15], conf=0.25, verbose=False)
            
            if len(results) > 0 and len(results[0].boxes) > 0:
                self.last_saved[ip] = current_time
                
                boxes = results[0].boxes.xyxy.cpu().numpy()
                h, w, _ = frame.shape
                
                for i, box in enumerate(boxes):
                    x1, y1, x2, y2 = box.astype(int)
                    
                    # Add extra padding for small crops
                    x1 = max(0, x1 - self.padding)
                    y1 = max(0, y1 - self.padding)
                    x2 = min(w, x2 + self.padding)
                    y2 = min(h, y2 + self.padding)
                    
                    crop = frame[y1:y2, x1:x2]
                    
                    if crop.size == 0:
                        continue

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    filename = f"cat_crop_{ip.replace('.', '_')}_{timestamp}_{i}.jpg"
                    filepath = os.path.join(self.output_dir, filename)
                    
                    cv2.imwrite(filepath, crop)
                    logger.info(f"Detected potential cat (conf: {results[0].boxes.conf[i]:.2f}) on {ip}. Saved crop.")

        cap.release()

    def start(self, ips=None):
        if ips is None:
            ips = CAMERA_IPS
            
        self.running = True
        for ip in ips:
            if not ip: continue
            t = threading.Thread(target=self._process_camera, args=(ip,))
            t.daemon = True
            t.start()
            self.threads.append(t)
            
    def stop(self):
        self.running = False
        for t in self.threads:
            t.join(timeout=2.0)
        logger.info("Extraction stopped.")

if __name__ == "__main__":
    import signal
    import sys
    extractor = RTSPExtractor()
    def signal_handler(sig, frame):
        extractor.stop()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    extractor.start()
    while True:
        time.sleep(1)
