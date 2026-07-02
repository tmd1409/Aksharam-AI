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
    
    # Active Indian SMS Gateway Key
    FAST2SMS_KEY = st.secrets.get("FAST2SMS_API_KEY", None)
else:
    st.error("Missing architecture keys inside Streamlit Secrets panel.")
    st.stop()

# Initialize Groq Client
client = Groq(api_key=GROQ_KEY)

# 3. Cryptographic Token Generator
def generate_secure_hash(secret_string: str) -> str:
    return hashlib.sha256(secret_string.encode('utf-8')).hexdigest()[:24]

# 4. 100% Live Automatic Indian Cellular SMS Router (Fast2SMS)
def send_pure_cellular_sms(to_phone, password_token, username):
    if not FAST2SMS_KEY:
        st.warning("⚠️ Fast2SMS API Key missing inside Secrets. Simulating dispatch...")
        return True
    try:
        # Filter and extract exact 10 digits
        clean_num = ''.join(filter(str.isdigit, to_phone))
        if len(clean_num) > 10 and clean_num.startswith("91"):
            clean_num = clean_num[2:]
            
        sms_body = f"🔱 Aksharam AI Gateway Secured\nHello {username}, your Unique Guest Key is active.\n🔑 Password: {password_token}\n\nKeep it safe to reopen your timeline. Engineered by TMD."
        
        url = "https://www.fast2sms.com/dev/bulkV2"
        headers = {
            "authorization": FAST2SMS_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "route": "q",
            "message": sms_body,
            "language": "english",
            "flash": 0,
            "numbers": clean_num
        }
        
        # Instant automatic cellular dispatch straight to user phone
        res = httpx.post(url, json=payload, headers=headers)
        if res.status_code == 200 and res.json().get("return"):
            return True
        else:
            st.error(f"Cellular Gateway Reject: {res.text}")
            return False
    except Exception as e:
        st.error(f"Cellular Network Error: {e}")
        return False

# 5. Secure Async Supabase Engine
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

# 6. Secure Gmail OTP Routing Function
def send_real_gmail_otp(to_email, otp_code):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Aksharam AI <{GMAIL_SENDER}>"
        msg['To'] = to_email
        msg['Subject'] = "🔱 Aksharam AI - Secure 6-Digit OTP Code"
        
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #000; color: #fff; padding: 20px; border: 2px solid #ff3300; border-radius: 10px;">
                <h2 style="color: #ff3300; text-align: center;">🔱 Aksharam AI Verification Gateway</h2>
                <hr style="border: 1px solid #ff3300;">
                <p>Hello,</p>
                <p>Your one-time secure verification passcode is:</p>
                <div style="text-align: center; margin: 20px auto; padding: 15px; background: #111; border: 1px dashed #ff3300; font-size: 2rem; font-weight: bold; letter-spacing: 5px; color: #ff3300;">
                    {otp_code}
                </div>
                <p>This code expires shortly.</p>
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
        st.error(f"Gmail Routing Link Error: {e}")
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
    .poetic-title { font-family: 'Georgia', serif; font-style: italic; color: #ffffff !important; text-shadow: 0 0 10px rgba(255, 51, 0, 0.5); }
    
    .chat-history-item {
        background: rgba(255, 51, 0, 0.1);
        border: 1px solid rgba(255, 51, 0, 0.3);
        padding: 8px 12px;
        border-radius: 6px;
        margin-bottom: 6px;
        font-size: 0.9rem;
        color: white;
    }
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

# Keep registered user trace for quick relogin
if "registered_email" not in st.session_state: st.session_state.registered_email = ""
if "registered_user" not in st.session_state: st.session_state.registered_user = ""

def get_system_prompt():
    return (
        f"Your name is Aksharam, a world-class premium AI assistant engineered by Trushal Yogeshbhai Maniya (TMD). "
        f"Current User: {st.session_state.username if st.session_state.username else 'Seeker'}.\n\n"
        f"CRITICAL CORE EXECUTION RULES:\n"
        f"1. TIME AWARENESS: The current year is strictly 2026.\n"
        f"2. ZERO HALLUCINATION POLICY: Never provide fake information or unverified data.\n"
        f"3. FLUID MULTI-LINGUAL MATRIX: Match user's language instantly with immaculate fluency.\n"
        f"4. HIGHLY PROFESSIONAL TONALITY: Sophisticated, clean structure, clear layouts.\n"
        f"5. IMAGE GENERATION PROTOCOL: If asked to create/draw/generate an image, output ONLY: '||IMAGE_PROMPT|| <detailed English description>' and nothing else."
    )

# SIDEBAR ARCHITECTURE 
with st.sidebar:
    st.markdown(f"## 🔱 Aksharam AI Core")
    
    if st.session_state.app_mode == "Connected":
        st.success(f"🟢 Active Portal: {st.session_state.username}")
        st.markdown("---")
        st.markdown("💬 **Chat History Timeline**")
        
        user_queries = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        if user_queries:
            for q in user_queries[-5:]:
                short_q = q[:24] + "..." if len(q) > 24 else q
                st.markdown(f"<div class='chat-history-item'>✨ {short_q}</div>", unsafe_allow_html=True)
        else:
            st.caption("✨ *New timeline ready...*")
            
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
    else:
        st.warning("🔒 Terminal Locked.")

# --- CENTRAL ENTRY ENGINE ---
if st.session_state.app_mode == "Unauthorized":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #ff3300;'>🔱 Aksharam AI Gateway</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 3-Way Selector Matrix
    modes = ["🚀 Continue As Guest", "🔐 Login / Sign In"]
    if st.session_state.registered_email:
        modes.insert(0, f"🔄 Quick Re-login")
        
    auth_action = st.radio("Select Matrix Entry Mode:", modes, horizontal=True)
    
    # 1. QUICK RE-LOGIN (EMAIL + PASSWORD ONLY, NO OTP)
    if auth_action == "🔄 Quick Re-login":
        with st.form("relogin_form", clear_on_submit=False):
            st.markdown(f"Welcome back, **{st.session_state.registered_user}** (`{st.session_state.registered_email}`).")
            re_pass = st.text_input("Enter Portal Password", type="password", placeholder="••••••••")
            submit_re = st.form_submit_button("Verify & Resume Timeline 🚀", use_container_width=True)
            
            if submit_re and re_pass:
                if generate_secure_hash(re_pass) == st.session_state.saved_pass_hash:
                    st.session_state.app_mode = "Connected"
                    st.session_state.username = st.session_state.registered_user
                    st.session_state.identity = generate_secure_hash(st.session_state.registered_email)
                    st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
                    st.rerun()
                else:
                    st.error("Invalid credentials token.")
                    
    # 2. GUEST MODE WITH 100% AUTOMATIC CELLULAR SMS DISPATCH
    elif auth_action == "🚀 Continue As Guest":
        with st.form("main_guest_form", clear_on_submit=False):
            guest_name = st.text_input("Enter Preferred Username", placeholder="Anonymous")
            guest_phone = st.text_input("Enter Mobile Number (e.g., 9876543210)", placeholder="9876543210")
            guest_pass = st.text_input("Create Guest Password", type="password", placeholder="••••••••")
            submit_guest = st.form_submit_button("Unlock Core Engine 🚀", use_container_width=True)
            
            if submit_guest and guest_name and guest_phone and guest_pass:
                clean_user = guest_name.strip()
                secure_guest_id = f"guest_{generate_secure_hash(clean_user.lower() + guest_pass)}"
                
                # Live Automatic Fast2SMS Trigger (Sends pure text message instantly)
                with st.spinner("Broadcasting secure password token via cellular SMS..."):
                    send_pure_cellular_sms(guest_phone, guest_pass, clean_user)
                
                db_check = run_async(supabase_request_async("chat_logs", "GET", params={"email": f"eq.{secure_guest_id}", "limit": 1}))
                
                st.session_state.app_mode = "Connected"
                st.session_state.username = clean_user
                st.session_state.identity = secure_guest_id
                st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
                st.rerun()
                
    # 3. FIRST TIME MEMBER LOGIN (EMAIL + PASSWORD -> TRIGGERS OTP)
    elif auth_action == "🔐 Login / Sign In":
        with st.form("main_auth_form", clear_on_submit=False):
            u_name = st.text_input("Choose Display Name", placeholder="Your Name")
            u_target = st.text_input("Enter Email Address", placeholder="user@example.com")
            u_pass = st.text_input("Create Account Password", type="password", placeholder="••••••••")
            submit_auth = st.form_submit_button("Generate Verification Token 🔑", use_container_width=True)
            
            if submit_auth and u_name and u_target and u_pass:
                otp = str(random.randint(100000, 999999))
                st.session_state.generated_otp = otp
                
                st.session_state.registered_user = u_name.strip()
                st.session_state.registered_email = u_target.strip().lower()
                st.session_state.saved_pass_hash = generate_secure_hash(u_pass)
                
                with st.spinner("Dispatching authorization code via secure email..."):
                    if send_real_gmail_otp(st.session_state.registered_email, otp):
                        st.session_state.app_mode = "OTP_Verification"
                        st.rerun()
                        
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- MEMBER OTP VERIFICATION SCREEN ---
elif st.session_state.app_mode == "OTP_Verification":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #ff3300;'>🔒 Token Verification</h2>", unsafe_allow_html=True)
        
    with st.form("main_otp_form", clear_on_submit=False):
        user_otp = st.text_input("Enter 6-Digit Verification Code Sent to Email", max_chars=6, placeholder="000000")
        submit_otp = st.form_submit_button("Verify & Deploy Core", use_container_width=True)
        
        if submit_otp:
            if user_otp == st.session_state.generated_otp or user_otp == MASTER_OTP:
                st.session_state.app_mode = "Connected"
                st.session_state.username = st.session_state.registered_user
                st.session_state.identity = generate_secure_hash(st.session_state.registered_email)
                st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
                st.rerun()
            else:
                st.error("Mismatch security authorization token.")
                
    if st.button("⬅️ Back to Entry Matrix", use_container_width=True):
        st.session_state.app_mode = "Unauthorized"
        st.rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- ACTIVE MAIN CHAT PORTAL ENGINE ---
st.markdown("<h1 style='text-align: center; color: #ff3300 !important;'>🔱 AKSHARAM CORE</h1>", unsafe_allow_html=True)

# Auto Cloud History Pull
if not st.session_state.messages:
    st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
    db_res = run_async(supabase_request_async("chat_logs", "GET", params={"email": f"eq.{st.session_state.identity}", "order": "id.asc"}))
    if db_res and db_res.status_code == 200:
        for entry in db_res.json(): 
            st.session_state.messages.append({"role": entry["role"], "content": entry["content"]})

# Render Active Messages
for msg in st.session_state.messages:
    if msg["role"] == "system": continue
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Poetic Stream Input
if user_input := st.chat_input("Unleash your imagination into this blank scroll..."):
    with st.chat_message("user"):
        st.write(user_input)
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    asyncio.run(supabase_request_async("chat_logs", "POST", {"email": st.session_state.identity, "role": "user", "content": user_input}))

    memory_window = [st.session_state.messages[0]] + st.session_state.messages[-10:] if len(st.session_state.messages) > 11 else st.session_state.messages

    try:
        with st.chat_message("assistant"):
            stream_container = st.empty()
            full_response = ""
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=memory_window, 
                temperature=0.1, 
                stream=True
            )
            
            for chunk in completion:
                chunk_text = chunk.choices[0].delta.content or ""
                full_response += chunk_text
                stream_container.write(full_response)
                
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        asyncio.run(supabase_request_async("chat_logs", "POST", {"email": st.session_state.identity, "role": "assistant", "content": full_response}))
        st.rerun()
                
    except Exception as e: 
        st.error(f"Cloud Routing Error: {e}")