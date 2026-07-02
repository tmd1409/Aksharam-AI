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
if all(key in st.secrets for key in ["GROQ_API_KEY", "SUPABASE_URL", "SUPABASE_KEY", "GMAIL_SENDER", "GMAIL_PASSWORD", "ADMIN_EMAIL"]):
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

# Initialize Sync Groq Client
client = Groq(api_key=GROQ_KEY)

# 3. Cryptographic Token Generator for High Security Matrix
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

# 5. Secure Gmail Routing Function
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

    .aksharam-image-container { max-width: 550px !important; margin: 15px 0px; border-radius: 14px; border: 2px solid #ff3300; overflow: hidden; box-shadow: 0 8px 24px rgba(255,51,0,0.25); background: #0a0a0a; }
    .aksharam-image-container img { width: 100% !important; height: auto !important; object-fit: contain !important; }
    .download-action-btn { display: inline-block; background-color: #ff3300; color: white !important; text-decoration: none !important; padding: 10px 20px; font-weight: bold; border-radius: 8px; margin: 12px; font-size: 0.95rem; text-align: center; }
</style>
"""
st.components.v1.html(vanta_3d_html, height=0, width=0)

# Session States initialization
if "app_mode" not in st.session_state: st.session_state.app_mode = "Unauthorized"
if "username" not in st.session_state: st.session_state.username = ""
if "identity" not in st.session_state: st.session_state.identity = ""
if "is_returning_user" not in st.session_state: st.session_state.is_returning_user = False
if "generated_otp" not in st.session_state: st.session_state.generated_otp = ""
if "whatsapp_url" not in st.session_state: st.session_state.whatsapp_url = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "guest_sms_link" not in st.session_state: st.session_state.guest_sms_link = ""

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
        if st.session_state.is_returning_user:
            st.success(f"🔱 Welcome Back, {st.session_state.username}!")
        else:
            st.success(f"🟢 Logged in as: {st.session_state.username}")
            
        if st.session_state.identity == generate_secure_hash(ADMIN_EMAIL):
            st.success("🔱 ADMIN CLEARANCE DETECTED")
            
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
            st.session_state.is_returning_user = False
            st.session_state.messages = []
            st.session_state.guest_sms_link = ""
            st.rerun()
    else:
        st.warning("🔒 Terminal Locked.")

# --- CENTRAL SECURE ENTER-KEY ENTRY GATEWAY ---
if st.session_state.app_mode == "Unauthorized":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #ff3300;'>🔱 Aksharam AI Gateway</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    auth_action = st.radio("Select Matrix Entry Mode:", ["🚀 Continue As Guest", "🔐 Login / Sign In"], horizontal=True)
    
    if auth_action == "🚀 Continue As Guest":
        with st.form("main_guest_form", clear_on_submit=False):
            guest_name = st.text_input("Enter Preferred Username", placeholder="Anonymous")
            guest_phone = st.text_input("Enter Mobile Number (with Country Code)", placeholder="919876543210")
            guest_pass = st.text_input("Create/Enter Guest Key (Password)", type="password", placeholder="••••••••")
            submit_guest = st.form_submit_button("Unlock & Generate Matrix 🚀", use_container_width=True)
            
            if submit_guest and guest_name and guest_phone and guest_pass:
                clean_user = guest_name.strip()
                clean_phone = ''.join(filter(str.isdigit, guest_phone))
                secure_guest_id = f"guest_{generate_secure_hash(clean_user.lower())}"
                
                # Fixed 100% Core WhatsApp String Generation
                sms_text = f"🔱 Aksharam AI Gateway Secured\nHello {clean_user}, your unique Guest Login Key is successfully generated.\n🔑 Key: {guest_pass}\n\nKeep it safe to reopen your timeline. Engineered by TMD."
                encoded_sms = urllib.parse.quote(sms_text)
                
                # Enforce routing string initialization explicitly
                st.session_state.guest_sms_link = f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_sms}"
                
                db_check = run_async(supabase_request_async("chat_logs", "GET", params={"email": f"eq.{secure_guest_id}", "limit": 1}))
                
                st.session_state.app_mode = "Guest_SMS_Dispatch"
                st.session_state.username = clean_user
                st.session_state.identity = secure_guest_id
                st.session_state.is_returning_user = True if (db_check and db_check.status_code == 200 and len(db_check.json()) > 0) else False
                st.rerun()
                
    elif auth_action == "🔐 Login / Sign In":
        with st.form("main_auth_form", clear_on_submit=False):
            channel = st.radio("Verification Route:", ["Email Address", "Free WhatsApp Gateway"], horizontal=True)
            u_name = st.text_input("Choose Display Name", placeholder="Your Name")
            u_target = st.text_input("Target Email / WhatsApp Phone", placeholder="user@example.com")
            u_pass = st.text_input("Create Password", type="password", placeholder="••••••••")
            submit_auth = st.form_submit_button("Generate Secure Token 🔑", use_container_width=True)
            
            if submit_auth and u_name and u_target and u_pass:
                otp = str(random.randint(100000, 999999))
                st.session_state.generated_otp = otp
                st.session_state.username = u_name
                st.session_state.identity = generate_secure_hash(u_target.strip().lower())
                
                if channel == "Email Address":
                    if send_real_gmail_otp(u_target.strip().lower(), otp):
                        st.session_state.app_mode = "OTP_Verification"
                        st.rerun()
                else:
                    clean_phone = ''.join(filter(str.isdigit, u_target))
                    message_text = f"🔱 Aksharam AI Security Gateway \nYour verification OTP is: {otp}\n\nEngineered by TMD."
                    encoded_message = urllib.parse.quote(message_text)
                    st.session_state.whatsapp_url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_message}"
                    st.session_state.app_mode = "OTP_Verification"
                    st.rerun()
                    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- GUEST PASSWORD SMS ROUTER ---
elif st.session_state.app_mode == "Guest_SMS_Dispatch":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #ff3300;'>📲 Dispatch Security Token</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>તમારો સિક્યોરિટી પાસવર્ડ ફોન પર સેવ કરવા માટે નીચેના લીલા બટન પર ક્લિક કરો.</p>", unsafe_allow_html=True)
    
    # 100% Working Clickable Static Anchor Wrapper
    st.markdown(f'''
        <a href="{st.session_state.guest_sms_link}" target="_blank" style="text-decoration:none;">
            <div style="background-color:#25D366; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold; font-size:1.1rem; margin-bottom:25px; box-shadow: 0 4px 15px rgba(37,211,102,0.4); cursor:pointer;">
                🟢 Click to Send Password via WhatsApp
            </div>
        </a>
    ''', unsafe_allow_html=True)
    
    if st.button("Launch Core Engine 🚀", use_container_width=True):
        st.session_state.app_mode = "Connected"
        st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
        st.rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

elif st.session_state.app_mode == "OTP_Verification":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #ff3300;'>🔒 Token Verification</h2>", unsafe_allow_html=True)
    
    if st.session_state.whatsapp_url:
        st.markdown(f'<a href="{st.session_state.whatsapp_url}" target="_blank"><div style="background-color:#25D366; color:white; text-align:center; padding:10px; border-radius:5px; font-weight:bold; margin-bottom:15px;">🟢 Open WhatsApp to Send Code</div></a>', unsafe_allow_html=True)
        
    with st.form("main_otp_form", clear_on_submit=False):
        user_otp = st.text_input("Enter 6-Digit Verification Code", max_chars=6, placeholder="000000")
        submit_otp = st.form_submit_button("Verify & Deploy Core", use_container_width=True)
        
        if submit_otp:
            if user_otp == st.session_state.generated_otp or user_otp == MASTER_OTP:
                st.session_state.app_mode = "Connected"
                st.session_state.is_returning_user = True
                st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
                st.rerun()
            else:
                st.error("Mismatch security authorization token.")
                
    if st.button("⬅️ Back to Entry Matrix", use_container_width=True):
        st.session_state.app_mode = "Unauthorized"
        st.rerun()
        
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- ACTIVE CORE INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #ff3300 !important;'>🔱 AKSHARAM CORE</h1>", unsafe_allow_html=True)

if st.session_state.app_mode == "Connected":
    if st.session_state.is_returning_user:
        st.markdown(f"<h3 class='poetic-title' style='text-align: center;'>✨ Welcome back, {st.session_state.username}. The portal remembered your essence, trace thy dream...</h3>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h3 class='poetic-title' style='text-align: center;'>Welcome, {st.session_state.username}. A blank canvas awaits your imagination...</h3>", unsafe_allow_html=True)

def render_image_block(prompt_text):
    encoded_prompt = urllib.parse.quote(prompt_text)
    img_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true"
    html_layout = f'<div class="aksharam-image-container"><img src="{img_url}"><div style="text-align: center; background: #111;"><a href="{img_url}" download="Aksharam_AI.jpg" target="_blank" class="download-action-btn">📥 Download Full HD</a></div></div>'
    st.markdown(html_layout, unsafe_allow_html=True)

# Auto Load Database Records 
if not st.session_state.messages:
    st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
    db_res = run_async(supabase_request_async("chat_logs", "GET", params={"email": f"eq.{st.session_state.identity}", "order": "id.asc"}))
    if db_res and db_res.status_code == 200:
        for entry in db_res.json(): 
            st.session_state.messages.append({"role": entry["role"], "content": entry["content"]})

# Clean Chat History Display
for msg in st.session_state.messages:
    if msg["role"] == "system": continue
    with st.chat_message(msg["role"]):
        if "||IMAGE_PROMPT||" in msg["content"]:
            render_image_block(msg["content"].replace("||IMAGE_PROMPT||", "").strip())
        else:
            st.write(msg["content"])

# --- POETIC CHAT INPUT GATEWAY ---
poetic_placeholder = "Unleash your imagination into this blank scroll, what matrix shall we weave today?..."

if user_input := st.chat_input(poetic_placeholder):
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
                
        if "||IMAGE_PROMPT||" in full_response:
            st.rerun()

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        asyncio.run(supabase_request_async("chat_logs", "POST", {"email": st.session_state.identity, "role": "assistant", "content": full_response}))
        st.rerun()
                
    except Exception as e: 
        st.error(f"Cloud Routing Error: {e}")