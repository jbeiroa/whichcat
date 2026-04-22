import cv2
import os
import time
import threading
from datetime import datetime
from src.common.config import CAMERA_IPS, get_rtsp_url

def get_stream(ip, sub_stream=True):
    path = "/live/ch1" if sub_stream else "/live/ch0"
    return get_rtsp_url(ip, path)

class VideoCaptureThread:
    """
    Runs the video capture in a dedicated background thread.
    This prevents `cap.read()` from blocking the main thread (which causes the UI to hang/freeze).
    """
    def __init__(self, url):
        self.url = url
        self.cap = cv2.VideoCapture(self.url)
        self.ret = False
        self.frame = None
        self.running = True
        
        if self.cap.isOpened():
            self.ret, self.frame = self.cap.read()
            # Start the background thread
            self.thread = threading.Thread(target=self.update, args=())
            self.thread.daemon = True
            self.thread.start()

    def update(self):
        while self.running:
            if self.cap.isOpened():
                # This call can block if the network drops. 
                # Because it's in a thread, the UI won't freeze.
                ret, frame = self.cap.read()
                self.ret = ret
                if ret:
                    self.frame = frame
                else:
                    # If frame drops, sleep briefly to avoid pegging the CPU
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

    def isOpened(self):
        return self.cap.isOpened()

def main():
    # Force TCP and set a socket timeout (in microseconds). 
    # 5000000 = 5 seconds. This prevents infinite blocking on dead streams.
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;5000000"
    
    output_dir = "frames"
    os.makedirs(output_dir, exist_ok=True)

    use_substream = True
    video_thread = None
    connected_ip = None
    
    print("Initializing connection... (GUI should remain responsive)")
    
    for ip in CAMERA_IPS:
        if not ip: continue
        print(f"\nAttempting to connect to camera at {ip}...")
        url = get_stream(ip, use_substream)
        video_thread = VideoCaptureThread(url)
        
        time.sleep(1) # Allow thread to attempt first read
        
        if video_thread.isOpened() and video_thread.ret:
            connected_ip = ip
            print(f"-> Successfully connected to {ip} (sub-stream)")
            break
        else:
            video_thread.release()
            print(f"-> Failed to connect to {ip} on sub-stream. Trying main stream...")
            
            url = get_stream(ip, False)
            video_thread = VideoCaptureThread(url)
            time.sleep(1)
            
            if video_thread.isOpened() and video_thread.ret:
                connected_ip = ip
                use_substream = False
                print(f"-> Successfully connected to {ip} (main stream)")
                break
            else:
                video_thread.release()
                print(f"-> Failed to connect to {ip} entirely.")

    if not connected_ip or not video_thread or not video_thread.isOpened():
        print("\n*** ERROR: Could not connect to ANY camera. ***")
        print("Possible reasons:")
        print("1. The camera is currently handling its maximum number of streams (try power cycling it).")
        print("2. Your network is dropping the packets on the host side.")
        print("Exiting...")
        return

    print("\n=============================================")
    print("Stream connected successfully!")
    print("Controls:")
    print("  's' - Save frame")
    print("  'q' - Quit")
    print("  'c' - Toggle main/sub stream")
    print("=============================================\n")

    # Create window explicitly
    window_name = 'Gadnic Camera Live'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = video_thread.read()
            
            if not ret or frame is None:
                # If the thread hasn't fetched a new frame, wait a moment.
                # Since this is the main thread, the window will stay open but might look paused.
                time.sleep(0.05)
            else:
                # Show the latest frame fetched by the background thread
                cv2.imshow(window_name, frame)
            
            # waitKey allows the GUI to process events (mouse clicks, dragging, keyboard).
            # Because cap.read() is not running here, this runs constantly, keeping the UI smooth.
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                print("Quitting gracefully...")
                break
            elif key == ord('s'):
                if frame is not None:
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    fn = os.path.join(output_dir, f"frame_{ts}.jpg")
                    cv2.imwrite(fn, frame)
                    print(f"Saved: {fn}")
            elif key == ord('c'):
                print("Switching streams... please wait.")
                video_thread.release()
                use_substream = not use_substream
                url = get_stream(connected_ip, use_substream)
                video_thread = VideoCaptureThread(url)
                time.sleep(1) # Let the new thread stabilize

    except KeyboardInterrupt:
        print("\nCaught keyboard interrupt. Exiting...")
    finally:
        print("Cleaning up resources...")
        if video_thread:
            video_thread.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
