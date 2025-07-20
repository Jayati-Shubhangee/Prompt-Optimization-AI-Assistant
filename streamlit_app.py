import streamlit as st 
import requests
import base64
from PIL import Image
from io import BytesIO

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Promptimizer", layout="wide")

logo= Image.open("resources/pencil.png")


def image_to_base64(img_path):
    img = Image.open(img_path)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    return img_base64

cartoon_base64 = image_to_base64("resources/cartoon.png")

col1, col2 =st.columns([1,6])
with col1:
    st.image(logo, width=200)
with col2:
    st.markdown(
    """
    <div style="text-align: left;">
        <h1 style="color:#000000; font-size: 55px; margin-bottom: 10px;">
            Welcome to <span style='color:#EF5B0C;'>Promptimizer</span>
        </h1>
        <div style="color:#333333; font-size: 20px;">
            Effortlessly refine your prompts for precise results in seconds.
        </div>
    </div>
    """,
    unsafe_allow_html=True
    )

    # st.markdown(
    #      "<h1 style='color:#000000;font-size: 48px;'>Welcome to <span style='color:#EF5B0C;'>Promptimizer</span></h1>",                
    #     unsafe_allow_html=True
    # )

# ---- CUSTOM CSS ----
st.markdown("""
    <style>
    .reportview-container {
        background: #FFFAE5;
        padding: 0;
    }
    .prompt-box {
        background-color: white;
        padding: 5px 10px;
        border-radius: 12px;
        border: 3px solid #F97316;
        width: 250px;
        margin-left: 0;
        text-align: left;
    }
    .custom-button {
        background-color: #F97316;
        color: white;
        font-size: 18px;
        padding: 10px 30px;
        border-radius: 10px;
        border: none;
        cursor: pointer;
        transition: 0.3s;
    }
    .custom-button:hover {
        background-color: #e26300;
    }
    footer {
        text-align: center;
        padding: 10px;
        margin-top: 50px;
        font-size: 16px;
        color: #888;
    }
    </style>
""", unsafe_allow_html=True)

# ---- MAIN LAYOUT ----
left_col, right_col = st.columns([2, 1])

# ---- LEFT: Prompt Input ----
with left_col:
    st.markdown(
        '<div class="prompt-box"><h3 style="font-size:20px;">✨ Enter your prompt</h3></div>',
        unsafe_allow_html=True)

    prompt = st.text_area("", height=200, placeholder="e.g., write a short story about AI helping students...")
    submit_btn = st.button("🟠 Optimize Prompt")

    if submit_btn and prompt:
        with st.spinner("Optimizing your prompt..."):
            try:
                response = requests.post("http://127.0.0.1:8000/optimize", json={"prompt": prompt})
                if response.status_code == 200:
                    result = response.json()

                    st.markdown("---")
                    st.header("🔍 Prompt Quality Metrics")
                    st.slider("Clarity", 0, 10, int(result['quality_score'] * 0.85 / 10))
                    st.slider("Length", 0, 10, 8)
                    st.slider("Specificity", 0, 10, 7)

                    st.markdown("---")
                    if result["suggestions"]:
                        selected_suggestion = st.selectbox("💡 Suggestions to improve:", result["suggestions"])
                        st.info(f"💬 {selected_suggestion}")
                    else:
                        st.warning("No suggestions returned.")

                    if result["issues_detected"]:
                        st.markdown("---")
                        st.subheader("⚠️ Issues Detected")
                        for issue in result["issues_detected"]:
                            st.warning(f"- {issue}")

                    st.markdown("---")
                    st.subheader("🧠 Optimized Prompt Variants")
                    for i, variant in enumerate(result["variants"], start=1):
                        with st.expander(f"Version {i}"):
                            st.markdown(f"**Prompt:** {variant['optimized_prompt']}")
                            st.markdown(f"**Reason:** {variant['reason']}")
                else:
                    st.error(f"Error {response.status_code}: {response.json()['detail']}")
            except Exception as e:
                st.error(f"Exception occurred: {e}")

# ---- RIGHT: Quotes + Cartoon ----
with right_col:
    st.markdown("""
        <div style='text-align: right; margin-bottom: 10px;'>
            <div style='border: 2px solid black; border-radius: 25px; padding: 10px 20px; display: inline-block; font-weight: bold; font-family: Arial; background: #fff;'>
                ⟪ MASTERING THE ART OF PROMPT ENGINEERING 
            </div>
        </div>
        <div style='text-align: right;'>
            <div style='border: 2px solid black; border-radius: 25px; padding: 10px 20px; display: inline-block; font-weight: bold; font-family: Arial; background: #fff;'>
                ⟪ YOUR ULTIMATE GUIDE 
            </div>
        </div>
    """, unsafe_allow_html=True)
    
# Inject HTML to pin image to bottom right
st.markdown(
    f"""
    <style>
    .cartoon-float {{
        position: fixed;
        bottom: 10px;
        right: 10px;
        z-index: 9999;
    }}
    </style>
    <div class="cartoon-float">
        <img src="data:image/png;base64,{cartoon_base64}" height="310" width="270">
    </div>
    """,
    unsafe_allow_html=True
)
    # st.markdown("<br><br>", unsafe_allow_html=True)
    # cartoon = Image.open("resources/cartoon.png")
    # st.image(cartoon, width=200, use_container_width=False)

# ---- FOOTER ----
st.markdown("<footer>🚀 Made with ❤️ by Group 30</footer>", unsafe_allow_html=True)




