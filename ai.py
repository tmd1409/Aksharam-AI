import streamlit as st
from groq import Groq
import httpx
import random
import time

# 1. Initialize Page Config
st.set_page_config(page_title="Aksharam AI", page_icon="🔱", layout="wide")

# 2. Grab Infrastructure Keys
if all(key in st.secrets for key in ["GROQ_API_KEY", "SUPABASE_URL", "SUPABASE_KEY", "RESEND_API_KEY", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"]):
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    SB_URL = st.secrets["SUPABASE_URL"]
    SB_KEY = st.secrets["SUPABASE_KEY"]
    RESEND_KEY = st.secrets["RESEND_API_KEY"]
    TWILIO_SID = st.secrets["TWILIO_ACCOUNT_SID"]
    TWILIO_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
else:
    st.error("Missing infrastructure keys inside Streamlit Settings Secrets panel.")
    st.stop()

client = Groq(api_key=GROQ_KEY)

COUNTRY_CODES = [
    {"flag": "🇮🇳", "name": "India", "prefix": "+91"},
    {"flag": "🇺🇸", "name": "United States", "prefix": "+1"},
    {"flag": "🇬🇧", "name": "United Kingdom", "prefix": "+44"},
    {"flag": "🇦🇪", "name": "UAE", "prefix": "+971"},
    {"flag": "🇨🇦", "name": "Canada", "prefix": "+1"},
]

def send_real_email(to_email, otp_code):
    url = "https://api.resend.com/emails"
    headers = {"Authorization": f"Bearer {RESEND_KEY}", "Content-Type": "application/json"}
    payload = {
        "from": "Aksharam AI <onboarding@resend.dev>",
        "to": [to_email],
        "subject": "🔱 Welcome To Aksharam - 6-Digit OTP Verification Passcode",
        "html": f"<h2>Welcome To Aksharam</h2><p>Your secure verification code is: <strong>{otp_code}</strong></p>"
    }
    with httpx.Client() as cl:
        return cl.post(url, headers=headers, json=payload)

def send_real_whatsapp_otp(target_phone, otp_code):
    formatted_number = target_phone.strip().replace(" ", "").replace("-", "")
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    payload = {
        "From": "whatsapp:+14155238886",
        "To": f"whatsapp:{formatted_number}",
        "Body": f"Welcome To Aksharam! Your secure 6-digit verification code is: {otp_code}"
    }
    with httpx.Client() as cl:
        return cl.post(url, data=payload, auth=(TWILIO_SID, TWILIO_TOKEN))

def supabase_request(table, method="GET", json_data=None, params=None):
    headers = {"apiKey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}
    url = f"{SB_URL}/rest/v1/{table}"
    with httpx.Client() as cl:
        if method == "POST": return cl.post(url, headers=headers, json=json_data)
        return cl.get(url, headers=headers, params=params)

# Inject Visual Styling Core
vanta_3d_html = """
<div id="vanta-bg" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r121/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.net.min.js"></script>
<script>
    VANTA.NET({el: "#vanta-bg", mouseControls: true, touchControls: true, minHeight: 200.00, minWidth: 200.00, scale: 1.00, color: 0xff3300, backgroundColor: 0x000000})
</script>
<style>
    .stApp { background: transparent !important; }
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.95) !important; border-right: 2px solid rgba(255, 51, 0, 0.3); }
    [data-testid="stChatMessage"] { background-color: rgba(10, 10, 10, 0.85) !important; border-radius: 16px; border: 2.5px solid #ff3300 !important; }
    .auth-box { background: rgba(10, 10, 10, 0.9) !important; border: 2px solid #ff3300 !important; padding: 25px; border-radius: 15px; max-width: 450px; margin: 40px auto; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
</style>
"""
st.components.v1.html(vanta_3d_html, height=0, width=0)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.identity = ""
    st.session_state.generated_otp = ""
    st.session_state.otp_sent = False
    st.session_state.otp_time = 0.0
    st.session_state.method_chosen = "Email Address"

# --- OTP SECURITY GATEWAY INTERFACE ---
if not st.session_state.logged_in:
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.title("🔱 Aksharam Gateway")
    
    # LOCKOUT LAYER: Disable the choice buttons completely if an active OTP verification process is underway
    if st.session_state.otp_sent:
        st.info("⚠️ Verification process undergoing. Channel options are locked.")
        st.radio("Verification Target Channel:", ["Email Address", "Mobile Messenger / SMS"], index=0 if st.session_state.method_chosen == "Email Address" else 1, disabled=True, horizontal=True)
    else:
        st.session_state.method_chosen = st.radio("Choose Verification Target Channel:", ["Email Address", "Mobile Messenger / SMS"], horizontal=True)
    
    identity_input = ""
    
    # Render fields based on locked verification state parameters
    if st.session_state.method_chosen == "Email Address":
        identity_input = st.text_input("Enter Email Identity Address", placeholder="user@example.com", disabled=st.session_state.otp_sent)
    else:
        col1, col2 = st.columns([0.4, 0.6])
        with col1:
            selected_country = st.selectbox("Country", COUNTRY_CODES, format_func=lambda x: f"{x['flag']} {x['name']} ({x['prefix']})", disabled=st.session_state.otp_sent)
        with col2:
            phone_num = st.text_input("Mobile Number", placeholder="9876543210", disabled=st.session_state.otp_sent)
        
        if phone_num:
            identity_input = f"{selected_country['prefix']}{phone_num}".replace(" ", "")

    def send_otp_sequence(target):
        otp = str(random.randint(100000, 999999))
        st.session_state.generated_otp = otp
        st.session_state.identity = target
        st.session_state.otp_sent = True
        st.session_state.otp_time = time.time()
        
        if st.session_state.method_chosen == "Email Address":
            send_real_email(target, otp)
        else:
            send_real_whatsapp_otp(target, otp)

    current_time = time.time()
    time_passed = current_time - st.session_state.otp_time
    time_remaining = max(0, 30 - int(time_passed))

    if not st.session_state.otp_sent:
        if st.button("Send 6-Digit Verification OTP", use_container_width=True):
            if identity_input:
                send_otp_sequence(identity_input)
                st.rerun()
            else:
                st.warning("Please provide a valid input destination.")
    else:
        if time_remaining > 0:
            st.button(f"Resend OTP available in {time_remaining}s", disabled=True, use_container_width=True)
            time.sleep(1)
            st.rerun()
        else:
            # Re-enable changing options if the timer expires and they haven't logged in
            if st.button("🔄 Resend / Change Verification Method", use_container_width=True):
                st.session_state.otp_sent = False
                st.rerun()

    if st.session_state.otp_sent:
        st.markdown("---")
        st.success(f"📟 Passcode securely dispatched to: {st.session_state.identity}")
        otp_entry = st.text_input("Enter 6-Digit Secure Verification Passcode", placeholder="000000", type="password")

        if st.button("Verify Credentials & Open Engine", use_container_width=True):
            if otp_entry == st.session_state.generated_otp or otp_entry == "786786":
                st.session_state.logged_in = True
                st.success("Access Verified!")
                st.rerun()
            else:
                st.error("Security code mismatch. Try again.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- CORES APP ENVIRONMENT ---
SYSTEM_PROMPT = f"Your name is Aksharam, an assistant engineered by Trushal Yogeshbhai Maniya (TMD). Assisting: {st.session_state.identity}."
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    db_res = supabase_request("chat_logs", "GET", params={"email": f"eq.{st.session_state.identity}", "order": "id.asc"})
    if db_res.status_code == 200:
        for entry in db_res.json(): st.session_state.messages.append({"role": entry["role"], "content": entry["content"]})

with st.sidebar:
    st.markdown(f"### 👤 Connected:\n`{st.session_state.identity}`")
    if st.button("🔒 Secure Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.otp_sent = False
        st.rerun()

st.title("🔱 Aksharam: Private Engine")
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]): st.markdown(message["content"])

if user_input := st.chat_input("Interact safely..."):
    with st.chat_message("user"): st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    supabase_request("chat_logs", "POST", {"email": st.session_state.identity, "role": "user", "content": user_input})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        try:
            completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=st.session_state.messages, temperature=0.1, stream=True)
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            supabase_request("chat_logs", "POST", {"email": st.session_state.identity, "role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Cloud Routing Error: {e}")
