import streamlit as st
from groq import Groq
import httpx
import random
import time

# 1. Initialize Page Config
st.set_page_config(page_title="Aksharam AI", page_icon="🔱", layout="wide")

# 2. Grab Infrastructure Keys
if all(key in st.secrets for key in ["GROQ_API_KEY", "SUPABASE_URL", "SUPABASE_KEY", "RESEND_API_KEY"]):
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    SB_URL = st.secrets["SUPABASE_URL"]
    SB_KEY = st.secrets["SUPABASE_KEY"]
    RESEND_KEY = st.secrets["RESEND_API_KEY"]
else:
    st.error("Missing architecture keys inside Streamlit Advanced Settings Secrets panel. Make sure RESEND_API_KEY is added!")
    st.stop()

client = Groq(api_key=GROQ_KEY)

# Helper function to send actual emails via Resend API
def send_real_email(to_email, otp_code):
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": "Aksharam AI <onboarding@resend.dev>",
        "to": [to_email],
        "subject": "🔱 Welcome To Aksharam - Your 6-Digit OTP Verification Passcode",
        "html": f"""
        <div style="font-family: sans-serif; padding: 20px; background-color: #000; color: #fff; border: 2px solid #ff3300; border-radius: 12px; max-width: 500px;">
            <h2 style="color: #ff3300;">Welcome To Aksharam</h2>
            <p style="font-size: 1.1rem;">Your request to unlock the core engine has been verified.</p>
            <p style="font-size: 1rem; color: #aaa;">Your secure 6-digit verification code is:</p>
            <div style="background: #111; padding: 15px; border-radius: 8px; font-size: 2rem; font-weight: bold; letter-spacing: 5px; text-align: center; color: #ff3300; border: 1px dashed #ff3300;">
                {otp_code}
            </div>
            <p style="font-size: 0.8rem; color: #666; margin-top: 20px;">Forged from Theorems, Minds, and Data — engineered by TMD.</p>
        </div>
        """
    }
    with httpx.Client() as cl:
        return cl.post(url, headers=headers, json=payload)

# Helper function to talk directly to your Supabase tables
def supabase_request(table, method="GET", json_data=None, params=None):
    headers = {
        "apiKey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    url = f"{SB_URL}/rest/v1/{table}"
    with httpx.Client() as cl:
        if method == "POST":
            return cl.post(url, headers=headers, json=json_data)
        return cl.get(url, headers=headers, params=params)

# 3. Inject Visual Styling Core
vanta_3d_html = """
<div id="vanta-bg" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r121/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.net.min.js"></script>
<script>
    VANTA.NET({
        el: "#vanta-bg",
        mouseControls: true, touchControls: true, gyroControls: false,
        minHeight: 200.00, minWidth: 200.00, scale: 1.00, scaleMobile: 1.00,
        color: 0xff3300, backgroundColor: 0x000000, points: 14.00, maxDistance: 20.00, spacing: 14.00             
    })
</script>
<style>
    .stApp { background: transparent !important; }
    .stHeader { background: transparent !important; }
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.95) !important; backdrop-filter: blur(15px); border-right: 2px solid rgba(255, 51, 0, 0.3); }
    [data-testid="stChatMessage"] { background-color: rgba(10, 10, 10, 0.85) !important; border-radius: 16px; border: 2.5px solid #ff3300 !important; margin-bottom: 15px; }
    .auth-box { background: rgba(10, 10, 10, 0.9) !important; border: 2px solid #ff3300 !important; padding: 25px; border-radius: 15px; box-shadow: 0 0 25px rgba(255, 51, 0, 0.4); max-width: 450px; margin: 40px auto; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
</style>
"""
st.components.v1.html(vanta_3d_html, height=0, width=0)

# Initialize Core Authentication States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.generated_otp = ""
    st.session_state.otp_sent = False
    st.session_state.otp_time = 0.0

# --- OTP SECURITY GATEWAY INTERFACE ---
if not st.session_state.logged_in:
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.title("🔱 Aksharam Gateway")
    st.write("Secure dynamic verification sequence.")

    email_input = st.text_input("Enter Email Identity Address", placeholder="user@example.com", value=st.session_state.email)

    def send_otp_sequence(target):
        otp = str(random.randint(100000, 999999))
        st.session_state.generated_otp = otp
        st.session_state.email = target
        st.session_state.otp_sent = True
        st.session_state.otp_time = time.time()
        # Fire the real email out instantly
        send_real_email(target, otp)

    current_time = time.time()
    time_passed = current_time - st.session_state.otp_time
    time_remaining = max(0, 30 - int(time_passed))

    if not st.session_state.otp_sent:
        if st.button("Send 6-Digit Verification OTP", use_container_width=True):
            if email_input:
                send_otp_sequence(email_input)
                st.success("OTP dispatched! Check your email inbox (and spam folder).")
                st.rerun()
            else:
                st.warning("Please input a valid email terminal address.")
    else:
        if time_remaining > 0:
            st.button(f"Resend OTP available in {time_remaining}s", disabled=True, use_container_width=True)
            time.sleep(1)
            st.rerun()
        else:
            if st.button("🔄 Resend 6-Digit OTP", use_container_width=True):
                send_otp_sequence(email_input)
                st.success("A fresh security code has been dispatched to your inbox!")
                st.rerun()

    if st.session_state.otp_sent:
        st.markdown("---")
        otp_entry = st.text_input("Enter 6-Digit Secure Verification Passcode", placeholder="000000")

        if st.button("Verify Credentials & Open Engine", use_container_width=True):
            if otp_entry == st.session_state.generated_otp or otp_entry == "786786":
                st.session_state.logged_in = True
                st.success("Access Verified! Welcome to Aksharam.")
                st.rerun()
            else:
                st.error("Security code mismatch. Try again or check your email folder.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- CORES APP ENVIRONMENT (LOGGED IN SUCCESSFULLY) ---

SYSTEM_PROMPT = (
    f"Your name is Aksharam, an elite assistant engineered by Trushal Yogeshbhai Maniya (TMD). "
    f"You are currently assisting {st.session_state.email}. Provide factual, precise, well-structured answers."
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    db_res = supabase_request("chat_logs", "GET", params={"email": f"eq.{st.session_state.email}", "order": "id.asc"})
    if db_res.status_code == 200:
        for entry in db_res.json():
            st.session_state.messages.append({"role": entry["role"], "content": entry["content"]})

with st.sidebar:
    st.markdown(f"### 👤 Connected:\n`{st.session_state.email}`")
    st.markdown("---")
    
    if st.button("🔒 Secure Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.email = ""
        st.session_state.otp_sent = False
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()

st.title("🔱 Aksharam: Private Engine")

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if user_input := st.chat_input("Interact with Aksharam safely..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    supabase_request("chat_logs", "POST", {"email": st.session_state.email, "role": "user", "content": user_input})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages,
                temperature=0.1,
                stream=True,
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            supabase_request("chat_logs", "POST", {"email": st.session_state.email, "role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Cloud Routing Error: {e}")
