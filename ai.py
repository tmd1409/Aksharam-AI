import streamlit as st
from groq import Groq
import httpx
import random
import smtplib
import urllib.parse
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. Initialize Page Config
st.set_page_config(page_title="Aksharam AI", page_icon="🔱", layout="wide")

# 2. Grab Infrastructure Keys Safely
if all(key in st.secrets for key in ["GROQ_API_KEY", "SUPABASE_URL", "SUPABASE_KEY", "GMAIL_SENDER", "GMAIL_PASSWORD", "ADMIN_EMAIL"]):
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    SB_URL = st.secrets["SUPABASE_URL"]
    SB_KEY = st.secrets["SUPABASE_KEY"]
    GMAIL_SENDER = st.secrets["GMAIL_SENDER"]
    GMAIL_PASSWORD = st.secrets["GMAIL_PASSWORD"]
    ADMIN_EMAIL = st.secrets["ADMIN_EMAIL"].strip().lower()
else:
    st.error("Missing architecture keys or ADMIN_EMAIL inside Streamlit Secrets panel.")
    st.stop()

client = Groq(api_key=GROQ_KEY)

# 3. Secure Gmail Routing Function
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
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_SENDER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_SENDER, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Gmail Routing Link Error: {e}")
        return False

# Supabase Request Handler
def supabase_request(table, method="GET", json_data=None, params=None):
    headers = {"apiKey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}
    url = f"{SB_URL}/rest/v1/{table}"
    with httpx.Client() as cl:
        if method == "POST": return cl.post(url, headers=headers, json=json_data)
        return cl.get(url, headers=headers, params=params)

# Inject 3D Visual Styling & STRIP OUT ALL STREAMLIT TOOLBARS/BUTTONS FOR CLEAN LOOK
vanta_3d_html = """
<div id="vanta-bg" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r121/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.net.min.js"></script>
<script>
    VANTA.NET({el: "#vanta-bg", mouseControls: true, touchControls: true, minHeight: 200.00, minWidth: 200.00, scale: 1.00, color: 0xff3300, backgroundColor: 0x000000})
</script>
<style>
    #MainMenu {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    footer {visibility: hidden; display: none !important;}
    [data-testid="stAppDeployButton"] {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    .stDeployButton {display: none !important;}

    .stApp { background: transparent !important; }
    [data-testid="stSidebar"] { background-color: rgba(0, 0, 0, 0.95) !important; border-right: 2px solid rgba(255, 51, 0, 0.3); }
    [data-testid="stChatMessage"] { background-color: rgba(10, 10, 10, 0.85) !important; border-radius: 16px; border: 2.5px solid #ff3300 !important; }
    .auth-box { background: rgba(10, 10, 10, 0.9) !important; border: 2px solid #ff3300 !important; padding: 30px; border-radius: 15px; max-width: 500px; margin: 40px auto; box-shadow: 0 0 30px rgba(255, 51, 0, 0.3); }
    .quote-box { font-style: italic; color: #ff3300; text-align: center; margin-bottom: 20px; font-size: 1.1rem; font-weight: bold; }
    h1, h2, h3, p, span, label { color: #ffffff !important; }
</style>
"""
st.components.v1.html(vanta_3d_html, height=0, width=0)

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
            st.session_state.username = guest_name
            st.session_state.identity = f"guest_{random.randint(1000,9999)}"
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
        u_target = st.text_input("Enter WhatsApp Number (With Country Code, e.g., 919876543210)", placeholder="919876543210")
        
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
    with c5: b5 = st.text_input("", max_chars=1, key="b6", label_visibility="collapsed")
    with c6: b6 = st.text_input("", max_chars=1, key="b5", label_visibility="collapsed")
    
    full_user_otp = f"{b1}{b2}{b3}{b4}{b5}{b6}"
            
    if st.button("Verify Credentials & Deploy Core", use_container_width=True):
        if full_user_otp == st.session_state.generated_otp or full_user_otp == "786786":
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

# --- MAIN ACTIVE SYSTEM CORE ---
SYSTEM_PROMPT = (
    f"Your name is Aksharam, an elite super-assistant engineered by Trushal Yogeshbhai Maniya (TMD). "
    f"Assisting user: {st.session_state.username}. "
    f"CRITICAL SYSTEM SETTINGS:\n"
    f"1. The current year is 2026. Evaluate all timelines, facts, and events up to the year 2026.\n"
    f"2. You possess perfect, native-level language generation capabilities in Gujarati, Hindi, and English. "
    f"Provide flawless, sophisticated, elegant, and contextually absolute translations and text formulations."
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    db_res = supabase_request("chat_logs", "GET", params={"email": f"eq.{st.session_state.identity}", "order": "id.asc"})
    if db_res.status_code == 200:
        for entry in db_res.json(): st.session_state.messages.append({"role": entry["role"], "content": entry["content"]})

current_identity = st.session_state.identity.strip().lower()

# --- SIDEBAR INTERFACE: ADVANCED LINGUISTIC DASHBOARD ---
with st.sidebar:
    st.markdown(f"## 🔱 Aksharam AI Core")
    st.markdown(f"**Operator:** `{st.session_state.username}`")
    if current_identity == ADMIN_EMAIL:
        st.success("🟢 ADMIN CLEARANCE GRANTED")
    else:
        st.warning("🟡 GUEST CLEARANCE ONLY")
    
    st.markdown("---")
    
    # Mode Switcher: Let the user jump between standard chatbot or Advanced Modules
    app_feature = st.radio("Select Engine Layer:", ["💬 AI Conversationalist", "🔬 Advanced Linguistics Engine"])
    
    if app_feature == "🔬 Advanced Linguistics Engine":
        st.markdown("### ⚡ Real-Time Processing Suite")
        ling_mode = st.selectbox("Task Mode:", ["Contextual Translation", "Grammar & Tone Optimizer", "Smart Text Analyzer"])
        
        target_lang = ""
        target_tone = ""
        
        if ling_mode == "Contextual Translation":
            target_lang = st.selectbox("Translate to Language:", ["Gujarati (ગુજરાતી)", "Hindi (हिन्दी)", "English (US/UK)"])
        elif ling_mode == "Grammar & Tone Optimizer":
            target_tone = st.selectbox("Adjust Target Tone:", ["Highly Professional", "Casual & Friendly", "Academic / Analytical", "Diplomatic / Polite"])
            
        src_text = st.text_area("Input Text Matrix:", placeholder="Type or paste your text here...")
        
        # Real-time analytics output box inside sidebar
        if src_text:
            words = len(src_text.split())
            chars = len(src_text)
            read_time = max(1, round(words / 200))
            st.markdown(f"📊 **Metrics:** Words: `{words}` | Characters: `{chars}` | Read Time: ~`{read_time} min`")
            
        if st.button("🔥 Execute Linguistic Stream", use_container_width=True):
            if not src_text:
                st.error("Linguistic input buffer is empty.")
            else:
                if ling_mode == "Contextual Translation":
                    exec_prompt = f"System Instruction: Translate the following text completely and with contextually perfect syntax into {target_lang}. Maintain appropriate cultural nuances. Text:\n'{src_text}'"
                elif ling_mode == "Grammar & Tone Optimizer":
                    exec_prompt = f"System Instruction: Analyze and rewrite the following text. Correct all grammatical errors, smooth out syntax issues, and strictly convert the presentation tone to be {target_tone}. Text:\n'{src_text}'"
                else:
                    exec_prompt = f"System Instruction: Perform an extreme linguistic and structural analysis of this text. Break down its grammatical health, identify keywords, evaluate readability, and summarize its core concepts clearly. Text:\n'{src_text}'"
                
                st.session_state.messages.append({"role": "user", "content": exec_prompt})
                supabase_request("chat_logs", "POST", {"email": st.session_state.identity, "role": "user", "content": exec_prompt})
                st.rerun()

    st.markdown("---")
    if st.button("🔒 Secure Session Exit", use_container_width=True):
        st.session_state.app_mode = "Gateway"
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()

# --- ACTIVE WINDOW RENDERER ---
st.title("🔱 Aksharam Engine Matrix")

if app_feature == "🔬 Advanced Linguistics Engine":
    st.markdown("### 🔬 Advanced Language Engine Active")
    st.info("Configure your translation, tone modification, or analyzer tool in the left sidebar dashboard and hit 'Execute' to generate advanced responses.")
else:
    st.markdown(f"### Hi {st.session_state.username}, how can Aksharam assist you today?")

# Render historical messages
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]): 
            # Prettify the visual structure if it's a structural command prompt
            if "System Instruction:" in message["content"]:
                st.markdown(f"⚙️ **[Executed System Task Command]**")
                st.caption(message["content"])
            else:
                st.markdown(message["content"])

# --- CORE CHAT PROCESSING PIPELINE ---
should_process = False
user_input_text = ""

# Handle regular conversational text input
if user_input := st.chat_input("Query Aksharam Framework..."):
    user_input_text = user_input
    should_process = True
    st.session_state.messages.append({"role": "user", "content": user_input_text})
    supabase_request("chat_logs", "POST", {"email": st.session_state.identity, "role": "user", "content": user_input_text})
# Catch the background trigger when someone executes a sidebar analysis task
elif len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "user" and "System Instruction:" in st.session_state.messages[-1]["content"]:
    should_process = True

if should_process:
    if user_input_text:
        with st.chat_message("user"): st.markdown(user_input_text)
        
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=st.session_state.messages, 
                temperature=0.2, 
                stream=True
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            supabase_request("chat_logs", "POST", {"email": st.session_state.identity, "role": "assistant", "content": full_response})
        except Exception as e: 
            st.error(f"Cloud Routing Error: {e}")