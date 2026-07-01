import streamlit as st
from groq import Groq
import httpx

# 1. Initialize Page Config
st.set_page_config(page_title="Aksharam AI", page_icon="🔱", layout="wide")

# 2. Get Secure Infrastructure Secrets
if all(key in st.secrets for key in ["GROQ_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]):
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    SB_URL = st.secrets["SUPABASE_URL"]
    SB_KEY = st.secrets["SUPABASE_KEY"]
else:
    st.error("Missing architecture keys inside Streamlit Advanced Settings Secrets panel.")
    st.stop()

client = Groq(api_key=GROQ_KEY)

# Helper function to run direct REST calls to Supabase Auth Engine
def supabase_auth_request(endpoint, json_data):
    headers = {
        "apiKey": SB_KEY, 
        "Content-Type": "application/json"
    }
    url = f"{SB_URL}/auth/v1/{endpoint}"
    with httpx.Client() as cl:
        return cl.post(url, headers=headers, json=json_data)

# Helper function to read/write persistent data to Supabase Tables
def supabase_db_request(table, method="GET", json_data=None, params=None):
    headers = {
        "apiKey": SB_KEY,
        "Authorization": f"Bearer {st.session_state.get('auth_token', SB_KEY)}",
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

# Initialize Session Memory States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.email = ""
    st.session_state.auth_token = ""

# --- SECURITY GATEWAY INTERFACE (OTP LOGIC) ---
if not st.session_state.logged_in:
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.title("🔱 Aksharam Gateway")
    st.write("Enter your email to receive your secure 6-digit OTP code.")

    email_input = st.text_input("Email Address", placeholder="name@example.com")
    
    if st.button("Send Magic 6-Digit OTP", use_container_width=True):
        if email_input:
            # Native Supabase endpoint to trigger OTP/MagicLink generation
            res = supabase_auth_request("otp", {"email": email_input, "options": {"shouldCreateUser": True}})
            if res.status_code in [200, 201]:
                st.success(f"OTP successfully sent to {email_input}! Check your inbox or spam folder.")
                st.session_state.email = email_input
            else:
                st.error(f"Error sending OTP: {res.text}")
        else:
            st.warning("Please specify a valid email terminal.")

    st.markdown("---")
    otp_code = st.text_input("Enter 6-Digit OTP Verification Passcode", placeholder="123456")

    if st.button("Verify Keys & Launch Engine", use_container_width=True):
        if st.session_state.get("email") and otp_code:
            # FIX: Sending specific 'email' type ensures Supabase handles it as a 6-digit numeric token
            verify_res = supabase_auth_request("verify", {
                "email": st.session_state.email,
                "token": otp_code,
                "type": "email"
            })

            if verify_res.status_code == 200:
                auth_data = verify_res.json()
                st.session_state.logged_in = True
                st.session_state.auth_token = auth_data.get("access_token")
                st.success("Tunnel Verified! Syncing persistent profile...")
                st.rerun()
            else:
                st.error("Invalid or expired 6-Digit OTP token. Click 'Send Magic 6-Digit OTP' again.")
        else:
            st.error("Please request an OTP token first before validation.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- MAIN SECURE WORKING ENVIRONMENT ---

SYSTEM_PROMPT = (
    "Your name is Aksharam, an elite assistant engineered by Trushal Yogeshbhai Maniya (TMD). "
    "Provide factual, structured answers with clean layouts."
)

# Pull Chat Logs permanently from Supabase Cloud
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    db_res = supabase_db_request("chat_logs", "GET", params={"email": f"eq.{st.session_state.email}", "order": "id.asc"})
    if db_res.status_code == 200:
        for entry in db_res.json():
            st.session_state.messages.append({"role": entry["role"], "content": entry["content"]})

with st.sidebar:
    st.markdown(f"### 👤 Connected: \n`{st.session_state.email}`")
    st.markdown("---")
    
    if st.button("🔒 Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.email = ""
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()

st.title("🔱 Aksharam: Persistent Cloud Platform")

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if user_input := st.chat_input("Interact with Aksharam..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Sync User Input into Supabase
    supabase_db_request("chat_logs", "POST", {"email": st.session_state.email, "role": "user", "content": user_input})

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
            # Sync AI Answer into Supabase
            supabase_db_request("chat_logs", "POST", {"email": st.session_state.email, "role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Cloud Routing Error: {e}")
