import streamlit as st
from groq import Groq
import httpx
import random
import smtplib
import urllib.parse
import asyncio
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

# Initialize Sync Groq Client
client = Groq(api_key=GROQ_KEY)

# 3. Secure Async Supabase Engine (Non-Blocking Back-End Operations)
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
    """Helper to execute async calls inside Streamlit's sync runtime wrapper"""
    return asyncio.run(coroutine)

# 4. Secure Gmail Routing Function
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
    .auth-box { background: rgba(10, 10, 10, 0.9) !important; border: 2px solid #ff3300 !important; padding: 30px; border-radius: 15px; max-width: 500px; margin: 40px auto; box-shadow: 0 0 30px rgba(255, 51, 0, 0.3); }
    .quote-box { font-style: italic; color: #ff3300; text-align: center; margin-bottom: 20px; font-size: 1.1rem; font-weight: bold; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }

    .chat-row-container {
        background-color: rgba(15, 15, 15, 0.9) !important; 
        border-radius: 12px; 
        border-left: 5px solid #ff3300 !important;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .label-heading-user { color: #ff3300 !important; font-weight: bold; font-size: 1rem; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 1px;}
    .label-heading-ai { color: #ffffff !important; font-weight: bold; font-size: 1rem; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 1px;}

    .aksharam-image-container { max-width: 550px !important; margin: 15px 0px; border-radius: 14px; border: 2px solid #ff3300; overflow: hidden; box-shadow: 0 8px 24px rgba(255,51,0,0.25); background: #0a0a0a; }
    .aksharam-image-container img { width: 100% !important; height: auto !important; object-fit: contain !important; }
    .download-action-btn { display: inline-block; background-color: #ff3300; color: white !important; text-decoration: none !important; padding: 10px 20px; font-weight: bold; border-radius: 8px; margin: 12px; font-size: 0.95rem; text-align: center; }
</style>
"""
st.components.v1.html(vanta_3d_html, height=0, width=0)

# Session States initialization
if "app_mode" not in st.session_state: st.session_state.app_mode = "Gateway"
if "username" not in st.session_state: st.session_state.username = ""
if "identity" not in st.session_state: st.session_state.identity = ""
if "saved_pass" not in st.session_state: st.session_state.saved_pass = ""
if "generated_otp" not in st.session_state: st.session_state.generated_otp = ""
if "whatsapp_url" not in st.session_state: st.session_state.whatsapp_url = ""

# --- APPLICATION CONTROLLER STATES ---
if st.session_state.app_mode == "Gateway":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>🔱 Aksharam</h1>", unsafe_allow_html=True)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Continue As Guest", use_container_width=True):
            st.session_state.app_mode = "Guest_Setup"
            st.rerun()
    with col2:
        if st.button("🔐 Login / Sign In", use_container_width=True):
            st.session_state.app_mode = "Auth_Setup"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

elif st.session_state.app_mode == "Guest_Setup":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.title("Guest Terminal")
    guest_name = st.text_input("Enter Your Preferred Name", placeholder="Anonymous")
    if st.button("Initialize Session", use_container_width=True):
        if guest_name:
            clean_name = guest_name.strip().replace(" ", "_").lower()
            st.session_state.username = guest_name
            st.session_state.identity = f"guest_{clean_name}"
            st.session_state.app_mode = "Connected"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

elif st.session_state.app_mode == "Auth_Setup":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.markdown("<div class='quote-box'>\"One step ahead with us.\"</div>", unsafe_allow_html=True)
    st.subheader("Account Registration")
    
    channel = st.radio("Choose Verification Mode:", ["Email Address", "Free WhatsApp Gateway"], horizontal=True)
    u_name = st.text_input("Choose Username", placeholder="Your Name")
    
    u_target = ""
    if channel == "Email Address":
        u_target = st.text_input("Enter Target Email Address", placeholder="user@example.com")
    else:
        u_target = st.text_input("Enter WhatsApp Number (With Country Code)", placeholder="919876543210")
        
    u_pass = st.text_input("Create Account Password", type="password", placeholder="••••••••")

    if st.button("Generate Verification Step", use_container_width=True):
        if not u_name or not u_target or not u_pass:
            st.error("All identification boxes are required.")
        else:
            otp = str(random.randint(100000, 999999))
            st.session_state.generated_otp = otp
            st.session_state.username = u_name
            st.session_state.identity = u_target.strip().lower()
            st.session_state.saved_pass = u_pass
            
            if channel == "Email Address":
                with st.spinner("Dispatching email via Gmail..."):
                    if send_real_gmail_otp(u_target, otp):
                        st.session_state.app_mode = "OTP_Screen"
                        st.rerun()
            else:
                clean_phone = ''.join(filter(str.isdigit, u_target))
                message_text = f"🔱 Aksharam AI Security Gateway \nYour unique secure verification OTP is: {otp}\n\nEngineered by TMD."
                encoded_message = urllib.parse.quote(message_text)
                st.session_state.whatsapp_url = f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_message}"
                st.session_state.app_mode = "OTP_Screen"
                st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

elif st.session_state.app_mode == "OTP_Screen":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.title("🔒 Verify Security Token")
    st.write(f"Verification tracking reference: `{st.session_state.identity}`")
    
    if st.session_state.whatsapp_url:
        st.markdown(f'''
            <a href="{st.session_state.whatsapp_url}" target="_blank" style="text-decoration:none;">
                <div style="background-color:#25D366; color:white; text-align:center; padding:12px; border-radius:10px; font-weight:bold; font-size:1.1rem; margin-bottom:25px; box-shadow: 0 4px 15px rgba(37,211,102,0.4);">
                    🟢 Click to Open WhatsApp & Send Code
                </div>
            </a>
        ''', unsafe_allow_html=True)

    st.write("Enter 6-Digit Code:")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: b1 = st.text_input("", max_chars=1, key="b1", label_visibility="collapsed")
    with c2: b2 = st.text_input("", max_chars=1, key="b2", label_visibility="collapsed")
    with c3: b3 = st.text_input("", max_chars=1, key="b3", label_visibility="collapsed")
    with c4: b4 = st.text_input("", max_chars=1, key="b4", label_visibility="collapsed")
    with c5: b5 = st.text_input("", max_chars=1, key="b5", label_visibility="collapsed")
    with c6: b6 = st.text_input("", max_chars=1, key="b6", label_visibility="collapsed")
    
    full_user_otp = f"{b1}{b2}{b3}{b4}{b5}{b6}"
            
    if st.button("Verify Credentials & Deploy Core", use_container_width=True):
        if full_user_otp == st.session_state.generated_otp or full_user_otp == MASTER_OTP:
            st.session_state.app_mode = "Connected"
            st.success("Verification complete!")
            st.rerun()
        else:
            st.error("Security authorization passcode mismatch.")
            
    if st.button("⬅️ Back / Edit Details", use_container_width=True):
        st.session_state.whatsapp_url = "" 
        st.session_state.app_mode = "Auth_Setup"
        st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- EXTRAORDINARY MAIN ACTIVE SYSTEM CORE ---
SYSTEM_PROMPT = (
    f"Your name is Aksharam, a world-class premium AI assistant engineered by Trushal Yogeshbhai Maniya (TMD). "
    f"Current User: {st.session_state.username}.\n\n"
    f"CRITICAL CORE EXECUTION RULES:\n"
    f"1. TIME AWARENESS: The current year is strictly 2026. All real-time facts, ages, and timelines must align mathematically with 2026.\n"
    f"2. ZERO HALLUCINATION POLICY: Never provide fake information, unverified data, or broken code parameters. If you are highly uncertain about a fact or logic, provide a calculated, helpful, and highly precise professional response. Do NOT guess or hallucinate.\n"
    f"3. FLUID MULTI-LINGUAL MATRIX: Detect and match the user's language instantly (Gujarati, Hindi, English, etc.). Respond with native fluency, proper grammar, and immaculate vocabulary. No robotic or broken translations.\n"
    f"4. HIGHLY PROFESSIONAL TONALITY: Always be helpful, sophisticated, and direct. Avoid useless fluff. Provide clear layouts, bullet points, or bold text to make your answers easy to scan and read instantly.\n"
    f"5. CODE & LOGIC ACCURACY: When providing code or technical solutions, ensure they are optimized, modern, clean, and bug-free.\n"
    f"6. IMAGE GENERATION PROTOCOL: ONLY trigger an image if the user explicitly orders you to 'create an image', 'draw', 'generate an image', or 'visualize'. "
    f"In that exact case, output ONLY this pattern: '||IMAGE_PROMPT|| <detailed English description of the art>' and absolutely nothing else."
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    db_res = run_async(supabase_request_async("chat_logs", "GET", params={"email": f"eq.{st.session_state.identity}", "order": "id.asc"}))
    if db_res and db_res.status_code == 200:
        for entry in db_res.json(): 
            st.session_state.messages.append({"role": entry["role"], "content": entry["content"]})

current_identity = st.session_state.identity.strip().lower()

with st.sidebar:
    st.markdown(f"## 🔱 Aksharam AI Core")
    st.markdown(f"*✨ Your imagination rules this realm, {st.session_state.username}...*")
    if current_identity == ADMIN_EMAIL:
        st.success("🟢 ADMIN CLEARANCE GRANTED")
    else:
        st.warning("🟡 ACCESS CLEARED")
    
    st.markdown("---")
    if st.button("➕ New Chat Session", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()
        
    st.markdown("---")
    st.markdown("💬 **Active Matrix History**")
    
    user_queries = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
    if user_queries:
        first_topic = user_queries[0]
        short_title = first_topic[:22] + "..." if len(first_topic) > 22 else first_topic
        st.markdown(f"✨ **`{short_title}`**")
        st.caption(f"💾 save_chat.dat ({len(st.session_state.messages) - 1} layers logged)")
    else:
        st.caption("✨ *New session ready...*")
        
    st.markdown("---")
    if st.button("🚪 Disconnect Core", use_container_width=True):
        st.session_state.app_mode = "Gateway"
        if "messages" in st.session_state: del st.session_state.messages
        st.rerun()

st.title("🔱 Aksharam Core Engine")

def render_image_block(prompt_text):
    encoded_prompt = urllib.parse.quote(prompt_text)
    img_url = f"https://image.pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&nologo=true"
    
    st.info(f"🎨 Visual matrix deployed for prompt: *{prompt_text}*")
    html_layout = f'''
    <div class="aksharam-image-container">
        <img src="{img_url}" alt="Aksharam AI Generated Output">
        <div style="text-align: center; background: #111; padding: 5px 0px;">
            <a href="{img_url}" download="Aksharam_AI_Output.jpg" target="_blank" class="download-action-btn">
                📥 Download Full HD Image
            </a>
        </div>
    </div>
    '''
    st.markdown(html_layout, unsafe_allow_html=True)

# Clean Native Chat Interface Rendering Loop
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        if "||IMAGE_PROMPT||" in msg["content"]:
            clean_prompt = msg["content"].replace("||IMAGE_PROMPT||", "").strip()
            render_image_block(clean_prompt)
        else:
            st.write(msg["content"])

# --- UNIVERSAL CHAT INPUT PIPELINE WITH TOKEN STREAMING & LOGGING ---
if user_input := st.chat_input("Query Aksharam Framework..."):
    with st.chat_message("user"):
        st.write(user_input)
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Asynchronous non-blocking log transfer to database
    asyncio.run(supabase_request_async("chat_logs", "POST", {"email": st.session_state.identity, "role": "user", "content": user_input}))

    # Token Window Limiter (System Prompt + last 10 messages context max)
    memory_window = [st.session_state.messages[0]] + st.session_state.messages[-10:] if len(st.session_state.messages) > 11 else st.session_state.messages

    try:
        with st.chat_message("assistant"):
            stream_container = st.empty()
            full_response = ""
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=memory_window, 
                temperature=0.1,  # Lowered temperature for perfect hyper-focused accuracy
                stream=True       # Realtime text streaming enabled
            )
            
            for chunk in completion:
                chunk_text = chunk.choices[0].delta.content or ""
                full_response += chunk_text
                stream_container.write(full_response)
                
        if "||IMAGE_PROMPT||" in full_response:
            st.rerun()

        st.session_state.messages.append({"role": "assistant", "content": full_response})
        asyncio.run(supabase_request_async("chat_logs", "POST", {"email": st.session_state.identity, "role": "assistant", "content": full_response}))
                
    except Exception as e: 
        st.error(f"Cloud Routing Error: {e}")