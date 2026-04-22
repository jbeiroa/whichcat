import os
from dotenv import load_dotenv

load_dotenv()

CAMERA_IPS = [ip.strip() for ip in os.getenv("CAMERA_IPS", "").split(",") if ip.strip()]
_users = [u.strip() for u in os.getenv("CAMERA_USER", "admin").split(",") if u.strip()]
_passwords = [p.strip() for p in os.getenv("CAMERA_PASSWORD", "").split(",") if p.strip()]

def get_credentials_for_ip(ip):
    """Returns (user, password) for a given camera IP."""
    try:
        idx = CAMERA_IPS.index(ip)
        user = _users[idx] if idx < len(_users) else _users[-1]
        password = _passwords[idx] if idx < len(_passwords) else _passwords[-1]
        return user, password
    except (ValueError, IndexError):
        # Fallback to first credentials if IP not found or lists are empty
        user = _users[0] if _users else "admin"
        password = _passwords[0] if _passwords else ""
        return user, password

def get_rtsp_url(ip, path="/live/ch0"):
    user, password = get_credentials_for_ip(ip)
    return f"rtsp://{user}:{password}@{ip}:554{path}"
