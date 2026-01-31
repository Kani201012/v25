import re
import bleach
from urllib.parse import urlparse

# Allowed tags and attributes for content fields
ALLOWED_TAGS = ["a", "b", "i", "u", "em", "strong", "p", "br", "ul", "ol", "li", "h2", "h3", "img"]
ALLOWED_ATTRS = {"a": ["href", "title", "rel", "target"], "img": ["src", "alt", "width", "height"]}


def clean_html(value: str) -> str:
    if not value:
        return ""
    # Trim and clean
    return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)


def clean_iframe(value: str) -> str:
    """
    Very small whitelist: only allow Google Maps iframe embeds.
    If input does not look like a safe iframe, return an empty string.
    """
    if not value:
        return ""
    v = value.strip()
    # Quick check for iframe
    if "<iframe" not in v:
        return ""
    # Extract src
    m = re.search(r'src=["\']([^"\']+)["\']', v)
    if not m:
        return ""
    src = m.group(1)
    # Allow only google maps origins
    parsed = urlparse(src)
    host = parsed.netloc.lower()
    allowed_hosts = ["www.google.com", "maps.google.com", "www.google.co", "www.google.co.in", "google.com", "www.google.co.uk"]
    if "google" not in host and "google" not in parsed.path:
        return ""
    # Rebuild a minimal iframe with safe attributes
    safe = f'<iframe src="{src}" width="600" height="450" style="border:0;" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>'
    return safe


def validate_url(value: str) -> bool:
    try:
        parsed = urlparse(value)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def ensure_trailing_slash(value: str) -> str:
    if not value:
        return ""
    return value if value.endswith("/") else value + "/"


def sanitize_filename(name: str) -> str:
    # remove unsafe characters
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)[:120]
