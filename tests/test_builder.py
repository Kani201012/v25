import pytest
from generator.site_builder import SiteBuilder

def test_render_contains_business_name():
    builder = SiteBuilder()
    ctx = {
        "biz_name": "Test Co",
        "hero_h": "Hello",
        "seo_d": "Desc",
        "biz_serv": ["One", "Two"],
        "about_txt": "<p>About</p>",
        "prod_url": "https://example.com/",
        "p_color": "#0f172a",
        "s_color": "#0ea5a6",
        "border_rad": "24px",
        "h_font": "Montserrat",
        "b_font": "Inter",
        "h_weight": "900",
        "ls": "0em",
        "gsc_tag_input": "",
        "map_iframe": "",
    }
    html = builder.render_home(ctx, is_home=True)
    assert "Test Co" in html
    assert "Hello" in html
