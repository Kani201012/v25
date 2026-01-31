import streamlit as st
import io
import zipfile
from datetime import datetime
from generator.site_builder import SiteBuilder
from generator.sanitizer import clean_html, clean_iframe, validate_url

# --- 1. APP CONFIGURATION ---
st.set_page_config(
    page_title="Kaydiem Titan v25.0 | Sovereign Architect",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="expanded",
)

# Polished light admin CSS
st.markdown(
    """
    <style>
    :root{
        --bg: #f7fafc;
        --card: #ffffff;
        --muted: #64748b;
        --accent: #0f172a;
        --accent-2: #06b6d4;
        --radius: 12px;
    }
    body, .main { background: var(--bg) !important; color: var(--accent) !important; font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial; }
    .block-container { max-width: 1200px; padding-top: 26px; padding-bottom: 36px; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,var(--card), #fbfdff) !important;
        border-right: 1px solid #e6eef5; padding: 18px; width: 340px;
        box-shadow: 0 6px 24px rgba(16,24,40,0.04);
    }
    .stExpander { background: var(--card) !important; border: 1px solid #eef4f8 !important; border-radius: 12px !important; padding: 12px !important; }
    .stButton>button { border-radius: 10px; padding: 10px 16px; font-weight:700; }
    input, textarea, select { border-radius: 8px; border:1px solid #e6eef5 !important; padding:10px !important; }
    .preview-controls { display:flex; gap:8px; align-items:center; }
    .device-pill { background:#fff; padding:6px 10px; border-radius:999px; border:1px solid #eef4f8; cursor:pointer; }
    .device-pill.selected { box-shadow: 0 6px 18px rgba(6,182,212,0.08); border-color: rgba(6,182,212,0.12); }
    .stComponents iframe { border-radius: 12px; border: 1px solid #eef4f8; box-shadow: 0 10px 30px rgba(16,24,40,0.06); }
    .helper { background:#f1fbfb; border-left:3px solid rgba(6,182,212,0.12); padding:8px; border-radius:8px; color:#0f4660 }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar: design controls ---
with st.sidebar:
    st.image("https://www.gstatic.com/images/branding/product/2x/business_profile_96dp.png", width=56)
    st.title("Titan v25.0 Studio")
    st.caption("Fulfilling 1,000+ Assets Daily")
    st.divider()

    with st.expander("🎭 1. Architecture DNA", expanded=True):
        layout_dna = st.selectbox(
            "Select Site DNA",
            [
                "Industrial Titan",
                "Classic Royal",
                "Glass-Tech SaaS",
                "The Bento Grid",
                "Brutalist Bold",
                "Corporate Elite",
                "Minimalist Boutique",
                "Midnight Stealth",
                "Vivid Creative",
                "Clean Health",
            ],
            help="This changes the HTML structure of the generated asset.",
        )
        col1, col2 = st.columns(2)
        with col1:
            p_color = st.color_picker("Primary Color", "#0f172a")
        with col2:
            s_color = st.color_picker("Accent (CTA)", "#06b6d4")
        border_rad = st.select_slider(
            "Corner Sharpness", options=["0px", "4px", "12px", "24px", "40px", "60px"], value="24px"
        )

    with st.expander("✍️ 2. Typography Studio", expanded=True):
        h_font = st.selectbox("Heading Font", ["Montserrat", "Playfair Display", "Oswald", "Syncopate", "Space Grotesk"], index=0)
        b_font = st.selectbox("Body Text Font", ["Inter", "Roboto", "Open Sans", "Work Sans", "Lora"], index=0)
        h_weight = st.select_slider("Heading Weight", options=["300", "400", "700", "900"], value="900")
        ls = st.select_slider("Letter Spacing (Tracking)", options=["-0.05em", "-0.02em", "0em", "0.05em", "0.1em"], value="-0.02em")

    with st.expander("⚙️ 3. Technical Verification"):
        gsc_tag_input = st.text_input("GSC Meta Tag Content", placeholder="google-site-verification=...")
        canonical_check = st.checkbox("Force Canonical Mapping", value=True)

    st.divider()
    st.info("Technical Lead: Kiran Deb Mondal\nwww.kaydiemscriptlab.com")

# --- Main UI (live inputs, no blocking form) ---
st.title("🏗️ Kaydiem Titan Supreme Engine v25.0")
st.caption("Precision Engineering for Local SEO Dominance")

# Tabs for inputs
tabs = st.tabs(["📍 Identity", "🏗️ Content & SEO", "🖼️ Assets", "⚡ Live E-com", "🌟 Social Proof", "⚖️ Legal"])

with tabs[0]:
    st.subheader("Core Business Identity (NAP Compliance)")
    c1, c2 = st.columns(2)
    with c1:
        biz_name = st.text_input("Business Name", "Red Hippo (The Planners)")
        biz_phone = st.text_input("Verified Phone", "+91 84540 02711")
        biz_email = st.text_input("Business Email", "events@redhippoplanners.in")
    with c2:
        biz_cat = st.text_input("Primary Category", "Luxury Wedding Planner")
        biz_hours = st.text_input("Operating Hours", "Mon-Sun: 10:00 - 19:00")
        prod_url = st.text_input("Production URL", "https://kani201012.github.io/site/")

    biz_logo = st.text_input("Logo Image URL", help="Direct link to a PNG/SVG file.")
    biz_addr = st.text_area("Full Maps Physical Address")
    biz_areas = st.text_area("Service Areas (Comma separated)", "Vasant Kunj, Chhatarpur, South Delhi, Riyadh")
    map_iframe_raw = st.text_area("Map Embed HTML Code (paste Google Maps iframe only)", placeholder="Paste the <iframe> from Google Maps here.")

with tabs[1]:
    st.subheader("AI-Search Content & Meta Layer")
    hero_h = st.text_input("Main Hero Headline", "Crafting Dream Weddings: New Delhi's Premier Luxury Decorators")
    seo_d = st.text_input("Meta Description (160 Chars)", "Verified 2026 AI-Ready Industrial Assets.")
    biz_key = st.text_input("Target SEO Keywords", help="Separate by commas")
    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        biz_serv_text = st.text_area("Services Listing (One per line)", "Floral Decor\nThematic Lighting\nVenue Sourcing")
    with col_s2:
        st.markdown('<div class="helper">💡 Pro Tip: Every service listed here is wrapped in H3 Semantic Tags for Googlebot clarity.</div>', unsafe_allow_html=True)

    about_txt = st.text_area("Our Authority Story (E-E-A-T Content)", height=250)

with tabs[2]:
    st.header("📸 High-Ticket Asset Manager")
    custom_hero = st.text_input("Hero Background URL", "")
    custom_feat = st.text_input("Feature Section Image URL", "")
    custom_gall = st.text_input("About Section Image URL", "")

with tabs[3]:
    st.header("🛒 Headless E-commerce Bridge")
    st.info("Publish your Google Sheet as CSV and paste link below (CORS required for preview).")
    sheet_url = st.text_input("Published CSV Link (CSV or pipe-delimited)", "")
    st.warning("CSV columns accepted: Name | Price | Description | Img1 | Img2 | Img3 (delimiter auto-detected)")

with tabs[4]:
    st.header("🌟 Trust & Social Proof")
    testi_raw = st.text_area("Testimonials (Name | Quote)", "Aramco | Reliable Partner.\nNEOM | Best in class.")
    faq_raw = st.text_area("F.A.Q. (Question? ? Answer)", "Are you certified? ? Yes, we are ISO 2026 compliant.")

with tabs[5]:
    st.header("⚖️ Authoritative Legal Hub")
    priv_body = st.text_area("Full Privacy Policy Content", height=200)
    terms_body = st.text_area("Full Terms & Conditions Content", height=200)

# Sanitize values
map_iframe = clean_iframe(map_iframe_raw)
about_txt_clean = clean_html(about_txt)
service_list = [s.strip() for s in (biz_serv_text or "").splitlines() if s.strip()]
area_list = [a.strip() for a in (biz_areas or "").split(",") if a.strip()]

if prod_url and not validate_url(prod_url):
    st.warning("Production URL looks invalid — please ensure it starts with https://")

# Build context used for templates
context = {
    "biz_name": biz_name or "Business Name",
    "biz_phone": biz_phone or "",
    "biz_email": biz_email or "",
    "biz_cat": biz_cat or "",
    "biz_hours": biz_hours or "",
    "prod_url": prod_url or "",
    "biz_logo": biz_logo or "",
    "biz_addr": biz_addr or "",
    "area_list": area_list,
    "hero_h": hero_h or "",
    "seo_d": seo_d or "",
    "biz_key": biz_key or "",
    "biz_serv": service_list,
    "about_txt": about_txt_clean,
    "custom_hero": custom_hero or "",
    "custom_feat": custom_feat or "",
    "custom_gall": custom_gall or "",
    "sheet_url": sheet_url or "",
    "testi_raw": testi_raw or "",
    "faq_raw": faq_raw or "",
    "priv_body": priv_body or "",
    "terms_body": terms_body or "",
    "p_color": p_color,
    "s_color": s_color,
    "border_rad": border_rad,
    "h_font": h_font,
    "b_font": b_font,
    "h_weight": h_weight,
    "ls": ls,
    "layout_dna": layout_dna,
    "gsc_tag_input": gsc_tag_input,
    "map_iframe": map_iframe or "",
}

# --- Build preview and zip ---
builder = SiteBuilder()

# Device preview selector
st.markdown("### Preview")
cols = st.columns([1, 3, 1])
with cols[0]:
    device = st.radio("Device", ["Desktop", "Tablet", "Mobile"], horizontal=False)
with cols[1]:
    # render preview HTML live (Streamlit reruns on change so preview always reflects state)
    preview_html = builder.render_home(context, is_home=True)
    height_map = {"Desktop": 800, "Tablet": 700, "Mobile": 600}
    st.components.v1.html(preview_html, height=height_map.get(device, 800), scrolling=True)

# Export ZIP
if st.button("🚀 DEPLOY & DOWNLOAD THE WORLD'S BEST BUSINESS ASSET"):
    z_b = io.BytesIO()
    builder.build_zip(context, z_b)
    z_b.seek(0)
    filename = f"{(biz_name or 'site').lower().replace(' ', '_')}_final.zip"
    st.download_button("📥 DOWNLOAD PLATINUM ASSET", z_b, file_name=filename)

st.caption("Auto-saved at: " + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"))
