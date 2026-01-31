import os
import io
import zipfile
import csv
import json
import re
import requests
from urllib.parse import quote_plus
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .sanitizer import clean_html, clean_iframe, ensure_trailing_slash, sanitize_filename

# Determine templates path (repo templates/ folder)
TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), "templates")
if not os.path.isdir(TEMPLATES_PATH):
    TEMPLATES_PATH = os.path.join(os.getcwd(), "templates")

env = Environment(loader=FileSystemLoader(TEMPLATES_PATH), autoescape=select_autoescape(["html", "xml"]))

# Register a url encoding filter for templates (used for building WhatsApp links)
env.filters["url_encode"] = lambda value: quote_plus(str(value)) if value is not None else ""

class SiteBuilder:
    def __init__(self):
        self.env = env

    def render_home(self, context: dict, is_home: bool = False) -> str:
        ctx = self._sanitize_context(context)
        tpl = self.env.get_template("index.html.j2")
        return tpl.render(**ctx)

    def render_about(self, context: dict) -> str:
        ctx = self._sanitize_context(context)
        tpl = self.env.get_template("about.html.j2")
        return tpl.render(**ctx)

    def _sanitize_context(self, context: dict) -> dict:
        out = dict(context)

        # Clean text/html fields
        for k in ["about_txt", "seo_d", "hero_h", "biz_name", "biz_addr", "biz_email", "biz_cat", "priv_body", "terms_body"]:
            if out.get(k):
                out[k] = clean_html(str(out.get(k)))

        # sanitize iframe
        out["map_iframe"] = clean_iframe(out.get("map_iframe", ""))

        # ensure prod_url trailing slash for sitemap/robots
        out["prod_url"] = ensure_trailing_slash(out.get("prod_url", ""))

        # Clean service list entries
        out["biz_serv"] = [clean_html(s) for s in out.get("biz_serv", [])]

        # Default image fallbacks
        out.setdefault(
            "custom_hero",
            out.get("custom_hero")
            or "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&q=80&w=1600",
        )
        out.setdefault(
            "custom_feat",
            out.get("custom_feat")
            or "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?auto=format&fit=crop&q=80&w=800",
        )
        out.setdefault(
            "custom_gall",
            out.get("custom_gall")
            or "https://images.unsplash.com/photo-1532712938310-34cb3982ef74?auto=format&fit=crop&q=80&w=1600",
        )

        # Derive a cleaned phone used for WhatsApp links (digits and optional leading country code)
        biz_phone = (out.get("biz_phone") or "").strip()
        phone_digits = re.sub(r"[^\d+]", "", biz_phone)
        # For wa link, we remove the plus sign (wa.me expects number without plus)
        out["biz_phone_wa"] = phone_digits.lstrip("+")

        # Parse products server-side (if sheet_url provided)
        sheet_url = out.get("sheet_url") or ""
        out["products"] = []
        if sheet_url:
            try:
                products = self._fetch_products_from_sheet(sheet_url)
                out["products"] = products
            except Exception:
                out["products"] = []

        # Provide sanitized privacy/terms html for modal consumption
        out["privacy_html"] = out.get("priv_body", "")
        out["terms_html"] = out.get("terms_body", "")

        # layout flag ensures templates can switch layouts
        out["layout_dna"] = out.get("layout_dna", "Bento Fallback")

        return out

    def _fetch_products_from_sheet(self, sheet_url: str):
        """
        Fetch CSV from a Google Sheets link or any CSV/pipe-delimited link.
        Returns a list of product dicts with keys: name, price, desc, img.
        Tries to auto-convert google edit URLs to export=csv.
        """
        url = sheet_url.strip()
        # Convert common Google Sheets edit URL to export CSV
        if "docs.google.com/spreadsheets" in url:
            # If it's the /edit or /edit#gid=... form, convert
            url = re.sub(r"/edit.*$", "/export?format=csv", url)

        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        text = resp.text

        # Use csv.Sniffer to detect delimiter; if fails fallback to '|' or ','
        dialect = None
        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(text.splitlines()[0] if text else ",")
            delim = dialect.delimiter
        except Exception:
            # Heuristic: if pipe found in first few lines use pipe else comma
            first_chunk = "\n".join(text.splitlines()[:5])
            delim = "|" if "|" in first_chunk and first_chunk.count("|") >= 1 else ","

        reader = csv.reader(text.splitlines(), delimiter=delim)
        rows = [r for r in reader if any(cell.strip() for cell in r)]
        products = []
        # If header present, detect and skip
        start = 0
        if rows:
            header = [c.strip().lower() for c in rows[0]]
            if any(h in ("name", "service_name", "product", "title") for h in header):
                start = 1

        for r in rows[start:]:
            # Normalize row to at least 4 columns
            name = r[0].strip() if len(r) > 0 else ""
            price = r[1].strip() if len(r) > 1 else ""
            desc = r[2].strip() if len(r) > 2 else ""
            img = r[3].strip() if len(r) > 3 else ""
            # If image looks like a Google Drive link, try to normalize (best-effort)
            products.append({"name": name, "price": price, "desc": desc, "img": img})
        return products

    def build_zip(self, context: dict, output_io: io.BytesIO):
        ctx = self._sanitize_context(context)
        with zipfile.ZipFile(output_io, "w", zipfile.ZIP_DEFLATED) as zf:
            index = self.env.get_template("index.html.j2").render(**ctx)
            about = self.env.get_template("about.html.j2").render(**ctx)
            contact = self.env.get_template("about.html.j2").render(**ctx)

            zf.writestr("index.html", index)
            zf.writestr("about.html", about)
            zf.writestr("contact.html", contact)
            zf.writestr("privacy.html", self._wrap_basic("Privacy Policy", ctx.get("privacy_html", "")))
            zf.writestr("terms.html", self._wrap_basic("Terms & Conditions", ctx.get("terms_html", "")))
            zf.writestr("404.html", self._wrap_basic("404 - Not Found", "<h1>404</h1><p>Not Found</p>"))
            zf.writestr("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {ctx.get('prod_url', '')}sitemap.xml")
            zf.writestr(
                "sitemap.xml",
                f"<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'><url><loc>{ctx.get('prod_url','')}index.html</loc></url><url><loc>{ctx.get('prod_url','')}about.html</loc></url></urlset>",
            )

    def _wrap_basic(self, title: str, body_html: str) -> str:
        body_safe = clean_html(body_html or "")
        return f"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title></head><body><main><h1>{title}</h1><div>{body_safe}</div></main></body></html>"""
