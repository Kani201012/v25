import os
import io
import requests
from PIL import Image

# Simple helper: download remote image and optionally resize/save as webp.
# This module is optional; used for improving export (not mandatory).

def fetch_image_to_bytes(url: str, max_size=(1600, 1600)):
    """
    Download image and return bytes. If large, resize to max_size.
    Returns bytes or None if failed.
    """
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content)).convert("RGB")
        img.thumbnail(max_size)
        out = io.BytesIO()
        img.save(out, format="WEBP", quality=80)
        out.seek(0)
        return out.read()
    except Exception:
        return None
