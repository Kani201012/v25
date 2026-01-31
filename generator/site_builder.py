import os
import io
import zipfile
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .sanitizer import clean_html, clean_iframe, sanitize_filename, ensure_trailing_slash

TEMPLATES_PATH = os.path.join(os.path.dirname(__file__), "templates")

# If templates are kept at repository root templates/ path
# Fallback to top-level templates directory
if not os.path.isdir(TEMPLATES_PATH):
    TEMPLATES_PATH = os.path.join(os.getcwd(), "templates")

env = Environment(loader=FileSystemLoader(TEMPLATES_PATH), autoescape=select_autoescape(["html", "xml"]))


class SiteBuilder:
    def __init__(self):
        self.env = env

    def render_home(self, context: dict, is_home: bool = False) -> str:
        """
        Renders the index.html using the index template and sanitized context.
        """
        ctx = self._sanitize_context(context)
        tpl = self.env.get_template("index.html.j2")
        return tpl.render(**ctx)

    def render_about(self, context: dict) -> str:
        ctx = self._sanitize_context(context)
        tpl = self.env.get_template("about.html.j2")
        return tpl.render(**ctx)

    def _sanitize_context(self, context: dict) -> dict:
        out = dict(context)
        # sanitize known string fields
        for k in ["about_txt", "seo_d", "hero_h", "biz_name", "biz_addr", "biz_email", "biz_cat"]:
            if out.get(k):
                out[k] = clean_html(str(out.get(k)))
        # sanitize iframe field
        out["map_iframe"] = clean_iframe(out.get("map_iframe", ""))
        # ensure prod_url trailing slash for sitemap/robots
        out["prod_url"] = ensure_trailing_slash(out.get("prod_url", ""))
        # ensure service list items sanitized
        out["biz_serv"] = [clean_html(s) for s in out.get("biz_serv", [])]
        return out

    def build_zip(self, context: dict, output_io: io.BytesIO):
        """
        Create a ZIP with generated site files.
        Writes into provided BytesIO.
        """
        ctx = self._sanitize_context(context)

        with zipfile.ZipFile(output_io, "w", zipfile.ZIP_DEFLATED) as zf:
            index = self.env.get_template("index.html.j2").render(**ctx)
            about = self.env.get_template("about.html.j2").render(**ctx)
            # contact uses simple about content fallback
            contact = self.env.get_template("about.html.j2").render(**ctx)

            zf.writestr("index.html", index)
            zf.writestr("about.html", about)
            zf.writestr("contact.html", contact)
            zf.writestr("privacy.html", self._wrap_basic("Privacy Policy", ctx.get("priv_body", "")))
            zf.writestr("terms.html", self._wrap_basic("Terms & Conditions", ctx.get("terms_body", "")))
            zf.writestr("404.html", self._wrap_basic("404 - Not Found", "<h1>404</h1><p>Not Found</p>"))
            zf.writestr("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {ctx.get('prod_url', '')}sitemap.xml")
            zf.writestr(
                "sitemap.xml",
                f"<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'><url><loc>{ctx.get('prod_url','')}index.html</loc></url><url><loc>{ctx.get('prod_url','')}about.html</loc></url></urlset>",
            )

    def _wrap_basic(self, title: str, body_html: str) -> str:
        body_safe = clean_html(body_html or "")
        return f"""<!doctype html><html><head><meta charset="utf-8"><title>{title}</title></head><body><main><h1>{title}</h1><div>{body_safe}</div></main></body></html>"""
