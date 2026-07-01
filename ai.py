import streamlit as st
from groq import Groq
import httpx

# 1. Initialize Page Config
st.set_page_config(page_title="Aksharam AI", page_icon="🔱", layout="wide")

# 2. Extract Secrets Network Stack
try:
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    SB_URL = st.secrets["SUPABASE_URL"]
    SB_KEY = st.secrets["SUPABASE_KEY"]
    TWILIO_SID = st.secrets["TWILIO_ACCOUNT_SID"]
    TWILIO_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
    TWILIO_SERVICE = st.secrets["TWILIO_VERIFY_SERVICE_SID"]
except Exception:
    st.error("Missing architecture keys inside Streamlit Advanced Settings Secrets panel.")
    st.stop()

client = Groq(api_key=GROQ_KEY)

# Helper function to query Twilio Verify API directly over HTTPS
def twilio_verify_request(endpoint, payload):
    url = f"https://verify.twilio.com/v2/Services/{TWILIO_SERVICE}/{endpoint}"
    auth = (TWILIO_SID, TWILIO_TOKEN)
    with httpx.Client() as cl:
        return cl.post(url, auth=auth, data=payload)

# Helper function to sync cloud chat data with Supabase Tables
def supabase_db_request(table, method="GET", json_data=None, params=None):
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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_identity = ""

# --- SECURITY GATEWAY INTERFACE (TWILIO ROUTER) ---
if not st.session_state.logged_in:
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.title("🔱 Aksharam Gateway")
    
    delivery_channel = st.radio("Choose OTP Transmission Channel:", ["Text Message (SMS)", "Email Inbox"])
    
    if delivery_channel == "Text Message (SMS)":
        user_input_target = st.text_input("Mobile Phone Number (Include country code, e.g., +919876543210)", placeholder="+91")
        channel_type = "sms"
    else:
        user_input_target = st.text_input("Email Address", placeholder="name@example.com")
        channel_type = "email"
        
    if st.button("Transmit 6-Digit OTP Token", use_container_width=True):
        if user_input_target:
            response = twilio_verify_request("Verifications", {"To": user_input_target, "Channel": channel_type})
            if response.status_code in [200, 201]:
                st.success(f"Security key successfully sent to {user_input_target}!")
                st.session_state.user_identity = user_input_target
            else:
                st.error(f"Routing transmission error: {response.text}")
        else:
            st.warning("Please specify a valid connection destination.")

    st.markdown("---")
    otp_code = st.text_input("Enter 6-Digit OTP Passcode", placeholder="123456", type="password")

    if st.button("Verify Keys & Launch Engine", use_container_width=True):
        if st.session_state.get("user_identity") and otp_code:
            check_response = twilio_verify_request("VerificationCheck", {"To": st.session_state.user_identity, "Code": otp_code})
            
            if check_response.status_code == 200 and check_response.json().get("status") == "approved":
                st.session_state.logged_in = True
                st.success("Tunnel Verified! Syncing persistent profile...")
                st.rerun()
            else:
                st.error("Invalid or expired 6-Digit verification code.")
        else:
            st.error("Please request an OTP passcode terminal first.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- MAIN SECURE WORKING ENVIRONMENT ---

SYSTEM_PROMPT = (
    "Your name is Aksharam, an elite assistant engineered by Trushal Yogeshbhai Maniya (TMD). "
    "Provide factual, structured answers with clean layouts."
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    db_res = supabase_db_request("chat_logs", "GET", params={"email": f"eq.{st.session_state.user_identity}", "order": "id.asc"})
    if db_res.status_code == 200:
        for entry in db_res.json():
            st.session_state.messages.append({"role": entry["role"], "content": entry["content"]})

with st.sidebar:
    st.markdown(f"### 👤 Connected: \n`{st.session_state.user_identity}`")
    st.markdown("---")
    if st.button("🔒 Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_identity = ""
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
    
    supabase_db_request("chat_logs", "POST", {"email": st.session_state.user_identity, "role": "user", "content": user_input})

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
            supabase_db_request("chat_logs", "POST", {"email": st.session_state.user_identity, "role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Cloud Routing Error: {e}")
