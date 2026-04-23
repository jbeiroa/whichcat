import cv2
import sys
import time
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.common.config import CAMERA_IPS, get_credentials_for_ip, get_rtsp_url

# Force TCP and set a timeout (in microseconds)
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp|stimeout;5000000"

def test_url(url):
    print(f"Testing: {url}")
    cap = cv2.VideoCapture(url)
    if cap.isOpened():
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        # Try to read a frame multiple times
        for _ in range(3):
            ret, frame = cap.read()
            if ret:
                print(f"SUCCESS: {url} ({int(width)}x{int(height)})")
                cap.release()
                return True, int(width), int(height)
            time.sleep(0.5)
        print(f"Opened but failed to read frame: {url}")
    cap.release()
    return False, 0, 0

ips = CAMERA_IPS

# Common RTSP paths for iCSee/XMEYE cameras
paths = [
    "/live/ch0",
    "/live/ch1",
    "/",
    "/stream1",
    "/stream2",
    "/cam/realmonitor?channel=1&subtype=0",
    "/cam/realmonitor?channel=1&subtype=1",
    "/mpeg4",
    "/h264",
    "/h265",
    "/ch0.h264",
    "/11", # Common for some generic Chinese cameras (channel 1, stream 1)
    "/12", # channel 1, stream 2
]

found_any = False
for ip in ips:
    if not ip: continue
    user, password = get_credentials_for_ip(ip)
    usernames = [user, "admin", "monites"]
    
    found_for_ip = False
    for u in usernames:
        for p in paths:
            url = f"rtsp://{u}:{password}@{ip}:554{p}"
            success, w, h = test_url(url)
            if success:
                print(f"\n*** FOUND WORKING URL for {ip}: {url} [{w}x{h}] ***\n")
                found_for_ip = True
                found_any = True
                break
        if found_for_ip: break
    if not found_for_ip:
        print(f"FAILED to find working URL for {ip}")

if not found_any:
    print("\nCould not find a working RTSP URL. Please check your credentials in the .env file.")
