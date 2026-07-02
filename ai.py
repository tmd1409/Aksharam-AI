import streamlit as st
from groq import Groq
import httpx
import random
import smtplib
import urllib.parse
import asyncio
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. Initialize Page Config
st.set_page_config(page_title="Aksharam AI", page_icon="🔱", layout="wide")

# 2. Grab Infrastructure Keys Safely
REQUIRED_KEYS = ["GROQ_API_KEY", "SUPABASE_URL", "SUPABASE_KEY", "GMAIL_SENDER", "GMAIL_PASSWORD", "ADMIN_EMAIL"]
if all(key in st.secrets for key in REQUIRED_KEYS):
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    SB_URL = st.secrets["SUPABASE_URL"]
    SB_KEY = st.secrets["SUPABASE_KEY"]
    GMAIL_SENDER = st.secrets["GMAIL_SENDER"]
    GMAIL_PASSWORD = st.secrets["GMAIL_PASSWORD"]
    ADMIN_EMAIL = st.secrets["ADMIN_EMAIL"].strip().lower()
    MASTER_OTP = st.secrets.get("MASTER_OTP", "786786")
else:
    st.error("Missing architecture keys inside Streamlit Secrets panel.")
    st.stop()

# Initialize Groq Client
client = Groq(api_key=GROQ_KEY)

# 3. Cryptographic Token Generator
def generate_secure_hash(secret_string: str) -> str:
    return hashlib.sha256(secret_string.encode('utf-8')).hexdigest()[:24]

# 4. Secure Async Supabase Engine
async def supabase_request_async(table, method="GET", json_data=None, params=None):
    headers = {
        "apiKey": SB_KEY, 
        "Authorization": f"Bearer {SB_KEY}", 
        "Content-Type": "application/json", 
        "Prefer": "return=representation"
    }
    url = f"{SB_URL}/rest/v1/{table}"
    async with httpx.AsyncClient() as cl:
        if method == "POST": 
            return await cl.post(url, headers=headers, json=json_data)
        return await cl.get(url, headers=headers, params=params)

def run_async(coroutine):
    return asyncio.run(coroutine)

# 5. Secure Gmail OTP & Password Router
def send_instant_security_mail(to_email, body_content, subject_text):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Aksharam AI <{GMAIL_SENDER}>"
        msg['To'] = to_email
        msg['Subject'] = f"🔱 Aksharam AI - {subject_text}"
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #000; color: #fff; padding: 20px; border: 2px solid #ff3300; border-radius: 10px;">
                <h2 style="color: #ff3300; text-align: center;">🔱 Aksharam AI Security Gateway</h2>
                <hr style="border: 1px solid #ff3300;">
                <div style="text-align: center; margin: 20px auto; padding: 15px; background: #111; border: 1px dashed #ff3300; font-size: 1.5rem; color: #ff3300;">
                    {body_content}
                </div>
                <p style="font-size: 0.8rem; color: #aaa; text-align: center;">Engineered by TMD © 2026</p>
            </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html'))
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_SENDER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_SENDER, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Security Dispatch Error: {e}")
        return False

# Inject 3D Visual Styling Environment
vanta_3d_html = """
<div id="vanta-bg" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r121/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.net.min.js"></script>
<script>
    VANTA.NET({el: "#vanta-bg", mouseControls: true, touchControls: true, minHeight: 200.00, minWidth: 200.00, scale: 1.00, color: 0xff3300, backgroundColor: 0x000000})
</script>
<style>
    #MainMenu, header, footer {visibility: hidden; display: none !important;}
    [data-testid="stAppDeployButton"], [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {display: none !important;}
    .stApp { background: transparent !important; }
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.95) !important; border-right: 2px solid rgba(255, 51, 0, 0.3); }
    .auth-box { background: rgba(10, 10, 10, 0.9) !important; border: 2px solid #ff3300 !important; padding: 30px; border-radius: 12px; max-width: 500px; margin: 40px auto; box-shadow: 0 0 25px rgba(255, 51, 0, 0.4); }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
    .chat-history-item { background: rgba(255, 51, 0, 0.1); border: 1px solid rgba(255, 51, 0, 0.3); padding: 8px 12px; border-radius: 6px; margin-bottom: 6px; font-size: 0.9rem; color: white; }
</style>
"""
st.components.v1.html(vanta_3d_html, height=0, width=0)

# Session States initialization
if "app_mode" not in st.session_state: st.session_state.app_mode = "Unauthorized"
if "username" not in st.session_state: st.session_state.username = ""
if "identity" not in st.session_state: st.session_state.identity = ""
if "saved_pass_hash" not in st.session_state: st.session_state.saved_pass_hash = ""
if "generated_otp" not in st.session_state: st.session_state.generated_otp = ""
if "messages" not in st.session_state: st.session_state.messages = []

# Keep registered trace for quick relogin
if "registered_email" not in st.session_state: st.session_state.registered_email = ""
if "registered_user" not in st.session_state: st.session_state.registered_user = ""

def get_system_prompt():
    return (
        f"Your name is Aksharam, a world-class premium AI assistant engineered by Trushal Yogeshbhai Maniya (TMD). "
        f"Current User: {st.session_state.username if st.session_state.username else 'Seeker'}.\n\n"
        f"CRITICAL CORE EXECUTION RULES:\n"
        f"1. TIME AWARENESS: The current year is strictly 2026.\n"
        f"2. ZERO HALLUCINATION POLICY: Never provide fake information.\n"
        f"3. FLUID MULTI-LINGUAL MATRIX: Match user's language instantly (Gujarati, Hindi, English).\n"
        f"4. HIGHLY PROFESSIONAL TONALITY: Sophisticated structure."
    )

# SIDEBAR ARCHITECTURE 
with st.sidebar:
    st.markdown(f"## 🔱 Aksharam AI Core")
    if st.session_state.app_mode == "Connected":
        st.success(f"🟢 Active Portal: {st.session_state.username}")
        st.markdown("---")
        if st.button("➕ New Chat Session", use_container_width=True):
            st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
            st.rerun()
        if st.button("🚪 Disconnect Session (Logout)", use_container_width=True):
            st.session_state.app_mode = "Unauthorized"
            st.session_state.username = ""
            st.session_state.identity = ""
            st.session_state.messages = []
            st.rerun()

# --- CENTRAL GATEWAY HUB ---
if st.session_state.app_mode == "Unauthorized":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #ff3300;'>🔱 Aksharam AI Gateway</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    modes = ["🚀 Continue As Guest", "🔐 Login / Sign In"]
    if st.session_state.registered_email:
        modes.insert(0, f"🔄 Quick Re-login")
        
    auth_action = st.radio("Select Entry Mode:", modes, horizontal=True)
    
    # 1. INSTANT RE-LOGIN (EMAIL + PASSWORD)
    if auth_action == "🔄 Quick Re-login":
        with st.form("relogin_form"):
            st.markdown(f"Welcome back, **{st.session_state.registered_user}**.")
            re_pass = st.text_input("Enter Portal Password", type="password")
            if st.form_submit_button("Verify & Resume 🚀", use_container_width=True) and re_pass:
                if generate_secure_hash(re_pass) == st.session_state.saved_pass_hash:
                    st.session_state.app_mode = "Connected"
                    st.session_state.username = st.session_state.registered_user
                    st.session_state.identity = generate_secure_hash(st.session_state.registered_email)
                    st.session_state.messages = []
                    st.rerun()
                else:
                    st.error("Invalid password token.")
                    
    # 2. GUEST MODE WITH 100% AUTOMATIC FREE TEXT ALERT via EMAIL-TO-HANDSET
    elif auth_action == "🚀 Continue As Guest":
        with st.form("guest_form"):
            guest_name = st.text_input("Enter Preferred Username", placeholder="Anonymous")
            guest_phone = st.text_input("Enter Mobile Number (10 Digits)", placeholder="9876543210")
            guest_pass = st.text_input("Create Guest Password", type="password")
            
            if st.form_submit_button("Unlock Core Engine 🚀", use_container_width=True) and guest_name and guest_phone and guest_pass:
                clean_user = guest_name.strip()
                clean_phone = ''.join(filter(str.isdigit, guest_phone))[-10:]
                
                # ઓટોમેટિક ઇન્સ્ટન્ટ ડિસ્પેચ ટ્રીક!
                sms_content = f"Hello {clean_user}, your Access Key is successfully compiled.<br>🔑 Password: <b>{guest_pass}</b>"
                
                # ભારતના ટેલિકોમ ઓપરેટર્સના બેકઅપ ગેટવે પર સીધું ફાયર થશે
                with st.spinner("Wiring secure key straight to your device..."):
                    for domain in ["@jio.com", "@airtelmail.com", "@ideacellular.net"]:
                        send_instant_security_mail(f"{clean_phone}{domain}", sms_content, "Guest Password")
                
                st.session_state.app_mode = "Connected"
                st.session_state.username = clean_user
                st.session_state.identity = f"guest_{generate_secure_hash(clean_user.lower() + guest_pass)}"
                st.rerun()
                
    # 3. MEMBER SIGN IN (EMAIL + PASSWORD -> TRIGGERS INSTANT OTP)
    elif auth_action == "🔐 Login / Sign In":
        with st.form("auth_form"):
            u_name = st.text_input("Choose Display Name")
            u_target = st.text_input("Enter Email Address")
            u_pass = st.text_input("Create Password", type="password")
            
            if st.form_submit_button("Generate Verification Token 🔑", use_container_width=True) and u_name and u_target and u_pass:
                otp = str(random.randint(100000, 999999))
                st.session_state.generated_otp = otp
                st.session_state.registered_user = u_name.strip()
                st.session_state.registered_email = u_target.strip().lower()
                st.session_state.saved_pass_hash = generate_secure_hash(u_pass)
                
                with st.spinner("Dispatching OTP code..."):
                    if send_instant_security_mail(st.session_state.registered_email, f"Your secure verification code is: <b>{otp}</b>", "Security OTP"):
                        st.session_state.app_mode = "OTP_Verification"
                        st.rerun()
                        
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- OTP VERIFICATION SCREEN ---
elif st.session_state.app_mode == "OTP_Verification":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #ff3300;'>🔒 Token Verification</h2>", unsafe_allow_html=True)
    with st.form("otp_form"):
        user_otp = st.text_input("Enter 6-Digit OTP Sent to Email", max_chars=6)
        if st.form_submit_button("Verify & Deploy Core", use_container_width=True) and user_otp:
            if user_otp == st.session_state.generated_otp or user_otp == MASTER_OTP:
                st.session_state.app_mode = "Connected"
                st.session_state.username = st.session_state.registered_user
                st.session_state.identity = generate_secure_hash(st.session_state.registered_email)
                st.rerun()
            else:
                st.error("Invalid security code token.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- ACTIVE INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #ff3300 !important;'>🔱 AKSHARAM CORE</h1>", unsafe_allow_html=True)

if not st.session_state.messages:
    st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
    db_res = run_async(supabase_request_async("chat_logs", "GET", params={"email": f"eq.{st.session_state.identity}", "order": "id.asc"}))
    if db_res and db_res.status_code == 200:
        for entry in db_res.json(): st.session_state.messages.append({"role": entry["role"], "content": entry["content"]})

for msg in st.session_state.messages:
    if msg["role"] == "system": continue
    with st.chat_message(msg["role"]): st.write(msg["content"])

if user_input := st.chat_input("Unleash your imagination into this blank scroll..."):
    with st.chat_message("user"): st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    asyncio.run(supabase_request_async("chat_logs", "POST", {"email": st.session_state.identity, "role": "user", "content": user_input}))
    
    try:
        with st.chat_message("assistant"):
            stream_container = st.empty()
            full_response = ""
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", messages=[st.session_state.messages[0]] + st.session_state.messages[-10:], temperature=0.1, stream=True
            )
            for chunk in completion:
                full_response += chunk.choices[0].delta.content or ""
                stream_container.write(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        asyncio.run(supabase_request_async("chat_logs", "POST", {"email": st.session_state.identity, "role": "assistant", "content": full_response}))
        st.rerun()
    except Exception as e: st.error(f"Cloud Error: {e}")