import os
import sys
import base64
import streamlit as st
import requests
from dotenv import load_dotenv

# ─── Project Root ──────────────────────────────────────────────────────────────
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ─── Load Environment ─────────────────────────────────────────────────────────
load_dotenv()  # ensure FASTAPI_URL is loaded

FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")
REGISTER_URL = f"{FASTAPI_URL}/auth/register"
LOGIN_URL = f"{FASTAPI_URL}/auth/login"

# ─── Streamlit Config ────────────────────────────────────────────────────────
st.set_page_config(page_title="🔐 AskMira Auth", layout="centered")

# ─── Session State ───────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

# ─── (Optional) Custom CSS ────────────────────────────────────────────────────
def add_custom_styles(image_path: str):
    with open(image_path, "rb") as img:
        b64 = base64.b64encode(img.read()).decode()
    css = f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background: url("data:image/png;base64,{b64}") no-repeat center/cover;
    }}
    .stButton > button {{
        width: 100%;
        background-color: #333;
        color: #fff;
    }}
    .stButton > button:hover {{
        background-color: #111;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# add_custom_styles("Images/YourBackground.png")  # uncomment & update path if you like

# ─── Authentication Pages ─────────────────────────────────────────────────────
def signup(username: str, email: str, password: str):
    payload = {"username": username, "email": email, "password": password}
    resp = requests.post(REGISTER_URL, json=payload)
    if resp.status_code in (200, 201):
        st.success("✅ Account created! Please log in.")
    else:
        detail = resp.json().get("detail", resp.text)
        st.error(f"Signup failed: {detail}")

def login(username: str, password: str):
    payload = {"username": username, "password": password}
    resp = requests.post(LOGIN_URL, json=payload)
    if resp.status_code == 200:
        data = resp.json()
        st.session_state["access_token"] = data["access_token"]
        st.session_state["logged_in"] = True
        st.experimental_rerun()
    else:
        detail = resp.json().get("detail", resp.text)
        st.error(f"Login failed: {detail}")

def auth_page():
    st.title("🔐 AskMira Login / Signup")
    mode = st.selectbox("I want to", ["Login", "Signup"])
    username = st.text_input("Username", key="auth_username")
    password = st.text_input("Password", type="password", key="auth_password")
    email = None
    if mode == "Signup":
        email = st.text_input("Email", key="auth_email")

    if st.button(mode):
        if mode == "Signup":
            if username and email and password:
                signup(username, email, password)
            else:
                st.error("Fill in all fields to sign up.")
        else:
            if username and password:
                login(username, password)
            else:
                st.error("Enter both username and password.")

# ─── Main ────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state["logged_in"]:
        auth_page()
    else:
        st.sidebar.markdown(f"👤 **{st.session_state.get('auth_username')}**")
        if st.sidebar.button("Logout"):
            st.session_state["logged_in"] = False
            st.session_state["access_token"] = None
            st.experimental_rerun()
        # Hand off to your main app once logged in
        import landing
        landing.run()

if __name__ == "__main__":
    main()
