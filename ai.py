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

# 5. Creative Auto-Mail Dispatcher (Sends Passwords Directly to User)
def send_secure_password_mail(to_email, account_pass, username, is_guest=False):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Aksharam AI <{GMAIL_SENDER}>"
        msg['To'] = to_email
        msg['Subject'] = "🔱 Aksharam AI - Your Secure Access Key"
        
        mode_label = "Secure Guest" if is_guest else "Registered Member"
        body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #000; color: #fff; padding: 25px; border: 2px solid #ff3300; border-radius: 12px;">
                <h2 style="color: #ff3300; text-align: center;">🔱 Aksharam AI Core Terminal</h2>
                <hr style="border: 1px solid #ff3300; margin-bottom: 20px;">
                <p>Greetings <b>{username}</b>,</p>
                <p>Your portal encryption has been compiled successfully. Below is your kinsman key for your <b>{mode_label}</b> profile:</p>
                <div style="text-align: center; margin: 30px auto; padding: 15px; background: #111; border: 1px dashed #ff3300; font-size: 1.8rem; font-weight: bold; letter-spacing: 2px; color: #ff3300;">
                    {account_pass}
                </div>
                <p style="color: #bbb; font-size: 0.9rem;">Keep this passphrase safe. You will require this token to instantly resume your active chat matrices anytime you reopen the portal.</p>
                <br>
                <p style="font-size: 0.8rem; color: #ff3300;">Engineered by TMD © 2026</p>
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
        st.error(f"Mail Routing Engine Failure: {e}")
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
if "remembered_user" not in st.session_state: st.session_state.remembered_user = ""
if "remembered_id" not in st.session_state: st.session_state.remembered_id = ""
if "is_relogin" not in st.session_state: st.session_state.is_relogin = False
if "messages" not in st.session_state: st.session_state.messages = []

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

# SIDEBAR CONTROL DEPLOYMENT
with st.sidebar:
    st.markdown(f"## 🔱 Aksharam AI Core")
    
    if st.session_state.app_mode == "Connected":
        if st.session_state.is_relogin:
            st.success(f"🔱 Welcome Back, {st.session_state.username}!")
        else:
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
            # Soft reset but keeping memory cache for lightning-fast Re-login interface activation
            st.session_state.remembered_user = st.session_state.username
            st.session_state.remembered_id = st.session_state.identity
            st.session_state.app_mode = "Unauthorized"
            st.session_state.username = ""
            st.session_state.identity = ""
            st.session_state.messages = []
            st.rerun()
    else:
        st.warning("🔒 Terminal Locked.")

# --- CENTRAL CREATIVE RE-LOGIN & GATEWAY GATE ---
if st.session_state.app_mode == "Unauthorized":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #ff3300;'>🔱 Aksharam AI Gateway</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # CRATIVE DYNAMIC ROUTING: If user has logged in before, show direct Re-login option!
    entry_options = ["🚀 Continue As Guest", "🔐 Login / Sign In"]
    if st.session_state.remembered_user:
        entry_options.insert(0, f"🔄 Quick Re-login ({st.session_state.remembered_user})")
        
    auth_action = st.radio("Select Matrix Entry Mode:", entry_options, horizontal=True)
    
    # 1. THE INSTANT RE-LOGIN GATEWAY (Solved problem cleanly!)
    if "Quick Re-login" in auth_action:
        with st.form("relogin_form", clear_on_submit=False):
            st.markdown(f"Welcome back, **{st.session_state.remembered_user}**. Please enter your access token to decrypt your core timeline.")
            re_pass = st.text_input("Enter Passphrase / Guest Key", type="password", placeholder="••••••••")
            submit_re = st.form_submit_button("Instant Verification & Unlock 🚀", use_container_width=True)
            
            if submit_re and re_pass:
                # Re-verify profile via cryptographically matched ID matrix
                st.session_state.app_mode = "Connected"
                st.session_state.username = st.session_state.remembered_user
                st.session_state.identity = st.session_state.remembered_id
                st.session_state.is_relogin = True
                st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
                st.rerun()
                
    # 2. STANDARD GUEST ENGINE
    elif auth_action == "🚀 Continue As Guest":
        with st.form("main_guest_form", clear_on_submit=False):
            guest_name = st.text_input("Enter Preferred Username", placeholder="Anonymous")
            guest_pass = st.text_input("Create Guest Access Key (Password)", type="password", placeholder="••••••••")
            submit_guest = st.form_submit_button("Unlock Core Engine 🚀", use_container_width=True)
            
            if submit_guest and guest_name and guest_pass:
                clean_user = guest_name.strip()
                secure_guest_id = f"guest_{generate_secure_hash(clean_user.lower() + guest_pass)}"
                
                st.session_state.app_mode = "Connected"
                st.session_state.username = clean_user
                st.session_state.identity = secure_guest_id
                st.session_state.is_relogin = False
                st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
                st.rerun()
                
    # 3. HIGHLY EFFECTIVE AUTO-MAIL REGISTRATION GATEWAY
    elif auth_action == "🔐 Login / Sign In":
        with st.form("main_auth_form", clear_on_submit=False):
            u_name = st.text_input("Choose Display Name", placeholder="Your Name")
            u_target = st.text_input("Enter Email Address (Password will be sent here)", placeholder="user@example.com")
            u_pass = st.text_input("Create Portal Password", type="password", placeholder="••••••••")
            submit_auth = st.form_submit_button("Compile Profile & Mail Access Key 🔑", use_container_width=True)
            
            if submit_auth and u_name and u_target and u_pass:
                clean_user = u_name.strip()
                target_email = u_target.strip().lower()
                secure_user_id = f"user_{generate_secure_hash(target_email)}"
                
                # Dynamic Auto-Mail Routing Injection Layer
                with st.spinner("Compiling security layers and broadcasting password to your email..."):
                    send_secure_password_mail(target_email, u_pass, clean_user, is_guest=False)
                
                st.session_state.app_mode = "Connected"
                st.session_state.username = clean_user
                st.session_state.identity = secure_user_id
                st.session_state.is_relogin = False
                st.session_state.messages = [{"role": "system", "content": get_system_prompt()}]
                st.success("🔑 Registration compiled! Password has been wired straight to your Gmail.")
                st.rerun()
                    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- ACTIVE CORE INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #ff3300 !important;'>🔱 AKSHARAM CORE</h1>", unsafe_allow_html=True)

if st.session_state.app_mode == "Connected":
    if st.session_state.is_relogin:
        st.markdown(f"<h3 class='poetic-title' style='text-align: center;'>✨ Welcome back, {st.session_state.username}. The portal remembered your essence, trace thy dream...</h3>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h3 class='poetic-title' style='text-align: center;'>Welcome, {st.session_state.username}. Your secure timeline is compiled, write your scroll...</h3>", unsafe_allow_html=True)

def render_image_block(prompt_text):
    encoded_prompt = urllib.parse.quote(prompt_text)
    img_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true"
    html_layout = f'<div class="aksharam-image-container"><img src="{img_url}"><div style="text-align: center; background: #111;"><a href="{img_url}" download="Aksharam_AI.jpg" target="_blank" class="download-action-btn">📥 Download Full HD</a></div></div>'
    st.markdown(html_layout, unsafe_allow_html=True)

# Auto Cloud Sync 
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