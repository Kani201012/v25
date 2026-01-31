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

# Light admin CSS (kept compact)
st.markdown(
    """
    <style>
    /* Minimal light theme polish for Streamlit admin UI */
    .block-container { max-width: 1100px; }
    [data-testid="stSidebar"] { background: #fff; border-right: 1px solid #eef4f8; padding: 18px; width: 320px }
    .stExpander { background: #fff; border: 1px solid #eef4f8; border-radius: 12px; padding: 10px; box-shadow: 0 6px 18px rgba(16,24,40,0.04); }
    .stButton>button { border-radius: 10px; font-weight:700; }
    input, textarea, select { border-radius:8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar: controls & settings ---
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
            help="This changes the actual HTML structure of the generated asset.",
        )
        col1, col2 = st.columns(2)
        with col1:
            p_color = st.color_picker("Primary Color", "#0f172a")
        with col2:
            s_color = st.color_picker("Accent (CTA)", "#0ea5a6")

        border_rad = st.select_slider(
            "Corner Sharpness", options=["0px", "4px", "12px", "24px", "40px", "60px"], value="24px"
        )

    with st.expander("✍️ 2. Typography Studio", expanded=True):
        h_font = st.selectbox(
            "Heading Font", ["Montserrat", "Playfair Display", "Oswald", "Syncopate", "Space Grotesk"], index=0
        )
        b_font = st.selectbox("Body Text Font", ["Inter", "Roboto", "Open Sans", "Work Sans", "Lora"], index=0)
        h_weight = st.select_slider("Heading Weight", options=["300", "400", "700", "900"], value="900")
        ls = st.select_slider(
            "Letter Spacing (Tracking)", options=["-0.05em", "-0.02em", "0em", "0.05em", "0.1em"], value="-0.02em"
        )

    with st.expander("⚙️ 3. Technical Verification"):
        gsc_tag_input = st.text_input("GSC Meta Tag Content", placeholder="google-site-verification=...")
        canonical_check = st.checkbox("Force Canonical Mapping", value=True)

    st.divider()
    st.info("Technical Lead: Kiran Deb Mondal\nwww.kaydiemscriptlab.com")

# --- Main form for business data ---
st.title("🏗️ Kaydiem Titan Supreme Engine v25.0")
st.caption("Precision Engineering for Local SEO Dominance")

with st.form("business_form", clear_on_submit=False):
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
        map_iframe = st.text_area("Map Embed HTML Code", placeholder="Paste the <iframe> from Google Maps here.")

    with tabs[1]:
        st.subheader("AI-Search Content & Meta Layer")
        hero_h = st.text_input("Main Hero Headline", "Crafting Dream Weddings: New Delhi's Premier Luxury Decorators")
        seo_d = st.text_input("Meta Description (160 Chars)", "Verified 2026 AI-Ready Industrial Assets.")
        biz_key = st.text_input("Target SEO Keywords (comma separated)")
        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            biz_serv = st.text_area("Services Listing (One per line)", "Floral Decor\nThematic Lighting\nVenue Sourcing")
        with col_s2:
            st.markdown(
                '<div style="background:#f1fbfb;padding:8px;border-left:3px solid rgba(14,165,166,0.12);border-radius:8px">💡 Pro Tip: Every service listed here is wrapped in H3 Semantic Tags for Googlebot clarity.</div>',
                unsafe_allow_html=True,
            )

        about_txt = st.text_area("Our Authority Story (E-E-A-T Content)", height=250)

    with tabs[2]:
        st.header("📸 High-Ticket Asset Manager")
        custom_hero = st.text_input("Hero Background URL", "")
        custom_feat = st.text_input("Feature Section Image URL", "")
        custom_gall = st.text_input("About Section Image URL", "")

    with tabs[3]:
        st.header("🛒 Headless E-commerce Bridge")
        st.info("Publish your Google Sheet as CSV and paste link below.")
        sheet_url = st.text_input("Published CSV Link", "")
        st.warning("Ensure CSV columns: Name | Price | Description | Img1 | Img2 | Img3")

    with tabs[4]:
        st.header("🌟 Trust & Social Proof")
        testi_raw = st.text_area("Testimonials (Name | Quote)", "Aramco | Reliable Partner.\nNEOM | Best in class.")
        faq_raw = st.text_area("F.A.Q. (Question? ? Answer)", "Are you certified? ? Yes, we are ISO 2026 compliant.")

    with tabs[5]:
        st.header("⚖️ Authoritative Legal Hub")
        priv_body = st.text_area("Full Privacy Policy Content", height=200)
        terms_body = st.text_area("Full Terms & Conditions Content", height=200)

    submitted = st.form_submit_button("Save Settings")

# Sanitize & validate critical inputs
map_iframe_clean = clean_iframe(map_iframe)
about_txt_clean = clean_html(about_txt)
biz_serv_clean = [s.strip() for s in (biz_serv or "").splitlines() if s.strip()]
area_list = [a.strip() for a in (biz_areas or "").split(",") if a.strip()]

if prod_url:
    prod_url_valid = validate_url(prod_url)
    if not prod_url_valid:
        st.warning("Production URL looks invalid — please check schema (https://...).")
else:
    prod_url = ""

# Prepare builder context
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
    "biz_serv": biz_serv_clean,
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
    "map_iframe": map_iframe_clean,
}

# Build & Preview / Download
st.header("⚡ Live Technical Preview (v25.0)")
builder = SiteBuilder()
preview_html = builder.render_home(context, is_home=True)

if st.checkbox("Activate Full Live Site Preview"):
    st.components.v1.html(preview_html, height=800, scrolling=True)

if st.button("🚀 DEPLOY & DOWNLOAD THE WORLD'S BEST BUSINESS ASSET"):
    z_b = io.BytesIO()
    builder.build_zip(context, z_b)
    z_b.seek(0)
    filename = f"{(biz_name or 'site').lower().replace(' ', '_')}_final.zip"
    st.download_button("📥 DOWNLOAD PLATINUM ASSET", z_b, file_name=filename)

st.caption("Saved at: " + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ"))
