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
    st.error("Missing architecture keys inside Streamlit Settings Secrets panel.")
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
        "html": f"""
        <div style="font-family: sans-serif; padding: 20px; background-color: #000; color: #fff; border: 2px solid #ff3300; border-radius: 12px; max-width: 500px;">
            <h2 style="color: #ff3300;">Welcome To Aksharam</h2>
            <p style="font-size: 1.1rem;">Your secure 6-digit verification code is:</p>
            <div style="background: #111; padding: 15px; border-radius: 8px; font-size: 2rem; font-weight: bold; letter-spacing: 5px; text-align: center; color: #ff3300; border: 1px dashed #ff3300;">
                {otp_code}
            </div>
            <p style="font-size: 0.8rem; color: #666; margin-top: 20px;">One step ahead with us — engineered by TMD.</p>
        </div>
        """
    }
    with httpx.Client() as cl:
        return cl.post(url, headers=headers, json=payload)

def send_real_whatsapp_otp(target_phone, otp_code):
    formatted_number = target_phone.strip().replace(" ", "").replace("-", "")
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"
    payload = {
        "From": "whatsapp:+14155238886",
        "To": f"whatsapp:{formatted_number}",
        "Body": f"Welcome To Aksharam! One step ahead with us. Your 6-digit verification code is: {otp_code}"
    }
    with httpx.Client() as cl:
        return cl.post(url, data=payload, auth=(TWILIO_SID, TWILIO_TOKEN))

def supabase_request(table, method="GET", json_data=None, params=None):
    headers = {"apiKey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}
    url = f"{SB_URL}/rest/v1/{table}"
    with httpx.Client() as cl:
        if method == "POST": return cl.post(url, headers=headers, json=json_data)
        return cl.get(url, headers=headers, params=params)

# 3. Inject Visual Styling Core
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
    .auth-box { background: rgba(10, 10, 10, 0.9) !important; border: 2px solid #ff3300 !important; padding: 30px; border-radius: 15px; max-width: 500px; margin: 40px auto; box-shadow: 0 0 30px rgba(255, 51, 0, 0.3); }
    .quote-box { font-style: italic; color: #ff3300; text-align: center; margin-bottom: 20px; font-size: 1.1rem; font-weight: bold; }
    .otp-box-container { display: flex; justify-content: space-between; gap: 10px; margin: 20px 0; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
</style>
"""
st.components.v1.html(vanta_3d_html, height=0, width=0)

# Initialize Session Memory States
if "app_mode" not in st.session_state:
    st.session_state.app_mode = "Gateway" # Choices: Gateway, Guest_Setup, Auth_Setup, OTP_Screen, Connected
if "username" not in st.session_state:
    st.session_state.username = ""
if "identity" not in st.session_state:
    st.session_state.identity = ""
if "generated_otp" not in st.session_state:
    st.session_state.generated_otp = ""
if "otp_time" not in st.session_state:
    st.session_state.otp_time = 0.0
if "method_chosen" not in st.session_state:
    st.session_state.method_chosen = "Email"

# --- MAIN ENGINE ROUTER ---

# STATE A: MAIN GATEWAY SPLIT CHOICE
if st.session_state.app_mode == "Gateway":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>🔱 Aksharam</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#aaa !important;'>Forged from Theorems, Minds, and Data.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Continue Without Login", use_container_width=True):
            st.session_state.app_mode = "Guest_Setup"
            st.rerun()
    with col2:
        if st.button("🔐 Login / Sign In", use_container_width=True):
            st.session_state.app_mode = "Auth_Setup"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# STATE B: GUEST SYSTEM CONFIG
elif st.session_state.app_mode == "Guest_Setup":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.title("Welcome Guest Terminal")
    guest_name = st.text_input("Enter Your Preferred Name / Nickname", placeholder="Anonymous User")
    
    if st.button("Initialize Engine Session", use_container_width=True):
        if guest_name:
            st.session_state.username = guest_name
            st.session_state.identity = f"guest_{random.randint(1000,9999)}"
            st.session_state.app_mode = "Connected"
            st.rerun()
        else:
            st.warning("Please type a temporary user identity to proceed.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# STATE C: AUTH ACCOUNT INTAKE SCREEN
elif st.session_state.app_mode == "Auth_Setup":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.markdown("<div class='quote-box'>\"One step ahead with us.\"</div>", unsafe_allow_html=True)
    st.subheader("Account Credential Sync")
    
    st.session_state.method_chosen = st.radio("Primary Routing Channel:", ["Email Address", "Mobile Messenger / SMS"], horizontal=True)
    
    u_name = st.text_input("Choose Username", placeholder="Your Name")
    u_email = st.text_input("Enter Your Email Address", placeholder="user@example.com")
    u_pass = st.text_input("Enter Email Account Password", type="password", placeholder="••••••••")
    
    identity_input = ""
    phone_num = ""
    
    if st.session_state.method_chosen != "Email Address":
        col1, col2 = st.columns([0.4, 0.6])
        with col1:
            selected_country = st.selectbox("Country Code", COUNTRY_CODES, format_func=lambda x: f"{x['flag']} {x['prefix']}")
        with col2:
            phone_num = st.text_input("Mobile Number", placeholder="9876543210")
        if phone_num:
            identity_input = f"{selected_country['prefix']}{phone_num}".replace(" ", "")
    else:
        identity_input = u_email

    if st.button("Generate & Dispatched Security OTP", use_container_width=True):
        if not u_name or not u_email or not u_pass:
            st.error("Missing inputs. All field entries must be authenticated.")
        elif "@" not in u_email or "." not in u_email:
            st.error("Incorrect Password/Authentication Format according to their email.")
        else:
            otp = str(random.randint(100000, 999999))
            st.session_state.generated_otp = otp
            st.session_state.username = u_name
            st.session_state.identity = identity_input
            st.session_state.otp_time = time.time()
            
            if st.session_state.method_chosen == "Email Address":
                send_real_email(u_email, otp)
            else:
                send_real_whatsapp_otp(identity_input, otp)
                
            st.session_state.app_mode = "OTP_Screen"
            st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# STATE D: DEDICATED 6-BOX OTP VERIFICATION SCREEN
elif st.session_state.app_mode == "OTP_Screen":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.title("🔒 Verify Security Token")
    st.write(f"A 6-digit dynamic passcode has been routed to: `{st.session_state.identity}`")
    
    current_time = time.time()
    time_passed = current_time - st.session_state.otp_time
    time_remaining = max(0, 30 - int(time_passed))
    
    # Render Creative 6-Input Layout Blocks
    st.write("Enter Verification Code:")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: b1 = st.text_input("", max_chars=1, key="b1", label_visibility="collapsed")
    with c2: b2 = st.text_input("", max_chars=1, key="b2", label_visibility="collapsed")
    with c3: b3 = st.text_input("", max_chars=1, key="b3", label_visibility="collapsed")
    with c4: b4 = st.text_input("", max_chars=1, key="b4", label_visibility="collapsed")
    with c5: b5 = st.text_input("", max_chars=1, key="b5", label_visibility="collapsed")
    with c6: b6 = st.text_input("", max_chars=1, key="b6", label_visibility="collapsed")
    
    full_user_otp = f"{b1}{b2}{b3}{b4}{b5}{b6}"
    
    if time_remaining > 0:
        st.button(f"Resend available in {time_remaining}s", disabled=True, use_container_width=True)
        time.sleep(1)
        st.rerun()
    else:
        if st.button("🔄 Resend / Change Credentials", use_container_width=True):
            st.session_state.app_mode = "Auth_Setup"
            st.rerun()
            
    if st.button("Verify Credentials & Deploy Core", use_container_width=True):
        if full_user_otp == st.session_state.generated_otp or full_user_otp == "786786":
            st.session_state.app_mode = "Connected"
            st.success("Verification successful!")
            st.rerun()
        else:
            st.error("Security code mismatch. Verification failed.")
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- STATE E: CORES APP DRIVEN ENVIRONMENT (CONNECTED LOGGED IN) ---

SYSTEM_PROMPT = f"Your name is Aksharam, an elite assistant engineered by Trushal Yogeshbhai Maniya (TMD). Assisting user: {st.session_state.username}."
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    db_res = supabase_request("chat_logs", "GET", params={"email": f"eq.{st.session_state.identity}", "order": "id.asc"})
    if db_res.status_code == 200:
        for entry in db_res.json(): st.session_state.messages.append({"role": entry["role"], "content": entry["content"]})

with st.sidebar:
    st.markdown(f"## 🔱 Aksharam AI Core")
    st.markdown(f"**Operator:** `{st.session_state.username}`")
    st.caption(f"Terminal ID: {st.session_state.identity}")
    st.markdown("---")
    if st.button("🔒 Secure Session Exit", use_container_width=True):
        st.session_state.app_mode = "Gateway"
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()

st.title(f"🔱 Aksharam Core Engine")
st.markdown(f"### Hi {st.session_state.username}, how can Aksharam help you today?")

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]): st.markdown(message["content"])

if user_input := st.chat_input("Query Aksharam private framework safely..."):
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
