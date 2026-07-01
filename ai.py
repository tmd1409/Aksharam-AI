import streamlit as st
from groq import Groq
import httpx
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. Initialize Page Config
st.set_page_config(page_title="Aksharam AI", page_icon="🔱", layout="wide")

# 2. Grab Infrastructure Keys Safely from Streamlit Secrets
if all(key in st.secrets for key in ["GROQ_API_KEY", "SUPABASE_URL", "SUPABASE_KEY", "GMAIL_SENDER", "GMAIL_PASSWORD"]):
    GROQ_KEY = st.secrets["GROQ_API_KEY"]
    SB_URL = st.secrets["SUPABASE_URL"]
    SB_KEY = st.secrets["SUPABASE_KEY"]
    GMAIL_SENDER = st.secrets["GMAIL_SENDER"]
    GMAIL_PASSWORD = st.secrets["GMAIL_PASSWORD"]
else:
    st.error("Missing primary infrastructure keys inside Streamlit Secrets panel.")
    st.stop()

client = Groq(api_key=GROQ_KEY)

# 3. Secure Unified Mail & SMS Gateway Routing Function
def send_unified_otp(target_destination, otp_code, mode="Email"):
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Aksharam AI <{GMAIL_SENDER}>"
        msg['To'] = target_destination
        
        if mode == "Email":
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
        else:
            # Plain text mobile network formatting optimize rules
            msg['Subject'] = "OTP"
            body = f"🔱 Aksharam AI Secure Code: {otp_code} . TMD Gateway System."
            msg.attach(MIMEText(body, 'plain'))
            
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_SENDER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_SENDER, target_destination, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"Routing Pipeline Gate Error: {e}")
        return False

# 4. Supabase Database Handler
def supabase_request(table, method="GET", json_data=None, params=None):
    headers = {"apiKey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Content-Type": "application/json", "Prefer": "return=representation"}
    url = f"{SB_URL}/rest/v1/{table}"
    with httpx.Client() as cl:
        if method == "POST": return cl.post(url, headers=headers, json=json_data)
        return cl.get(url, headers=headers, params=params)

# 5. Inject 3D Visual Styling Core
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
    h1, h2, h3, p, span, label { color: #ffffff !important; }
</style>
"""
st.components.v1.html(vanta_3d_html, height=0, width=0)

if "app_mode" not in st.session_state: st.session_state.app_mode = "Gateway"
if "username" not in st.session_state: st.session_state.username = ""
if "identity" not in st.session_state: st.session_state.identity = ""
if "saved_pass" not in st.session_state: st.session_state.saved_pass = ""
if "generated_otp" not in st.session_state: st.session_state.generated_otp = ""

# --- ROUTING LIFE CYCLE STATES ---

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
    
    channel = st.radio("Choose Verification Mode:", ["Email Address", "Mobile Network SMS / WhatsApp Fallback"], horizontal=True)
    u_name = st.text_input("Choose Username", placeholder="Your Name")
    
    final_routing_target = ""
    if channel == "Email Address":
        final_routing_target = st.text_input("Enter Target Email Address", placeholder="user@example.com")
    else:
        phone_num = st.text_input("Enter 10-Digit Mobile Number (No country code)", placeholder="9876543210")
        carrier_domain = st.selectbox("Select Network Operator Provider:", [
            "Jio (jio.com / Alternate Route)", 
            "Airtel (airtelmail.com)", 
            "Vodafone Idea (vtext.com)",
            "AT&T USA (txt.att.net)",
            "T-Mobile USA (tmomail.net)",
            "Verizon USA (vtext.com)"
        ])
        
        # Mapping gateway text structures
        if "Jio" in carrier_domain: domain_suffix = "jio.com"
        elif "Airtel" in carrier_domain: domain_suffix = "airtelmail.com"
        elif "AT&T" in carrier_domain: domain_suffix = "txt.att.net"
        elif "T-Mobile" in carrier_domain: domain_suffix = "tmomail.net"
        else: domain_suffix = "vtext.com"
        
        if phone_num:
            final_routing_target = f"{phone_num}@{domain_suffix}"
        
    u_pass = st.text_input("Create Account Password", type="password", placeholder="••••••••")

    if st.button("Generate & Dispatch Secure OTP Code", use_container_width=True):
        if not u_name or not final_routing_target or not u_pass:
            st.error("All identification form values are strictly required.")
        else:
            otp = str(random.randint(100000, 999999))
            st.session_state.generated_otp = otp
            st.session_state.username = u_name
            st.session_state.identity = final_routing_target
            st.session_state.saved_pass = u_pass
            
            with st.spinner("Processing automated global transmission layer..."):
                current_mode = "Email" if channel == "Email Address" else "SMS"
                if send_unified_otp(final_routing_target, otp, mode=current_mode):
                    st.session_state.app_mode = "OTP_Screen"
                    st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

elif st.session_state.app_mode == "OTP_Screen":
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.title("🔒 Verify Security Token")
    st.write(f"An automated verification code transmission pack has been fired out to: `{st.session_state.identity}`")
    st.info("💡 Pro-Tip Backdoor: If mobile network queues are congested in your region right now, use master bypass code: 786786")
    
    st.write("Enter Verification Code:")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: b1 = st.text_input("", max_chars=1, key="b1", label_visibility="collapsed")
    with c2: b2 = st.text_input("", max_chars=1, key="b2", label_visibility="collapsed")
    with c3: b3 = st.text_input("", max_chars=1, key="b3", label_visibility="collapsed")
    with c4: b4 = st.text_input("", max_chars=1, key="b4", label_visibility="collapsed")
    with c5: b5 = st.text_input("", max_chars=1, key="b5", label_visibility="collapsed")
    with c6: b6 = st.text_input("", max_chars=1, key="b6", label_visibility="collapsed")
    
    full_user_otp = f"{b1}{b2}{b3}{b4}{b5}{b6}"
            
    if st.button("Verify Credentials & Deploy Core", use_container_width=True):
        if full_user_otp == st.session_state.generated_otp or full_user_otp == "786786":
            st.session_state.app_mode = "Connected"
            st.success("Verification complete!")
            st.rerun()
        else:
            st.error("Security authorization passcode mismatch.")
            
    if st.button("⬅️ Back / Edit Details", use_container_width=True):
        st.session_state.app_mode = "Auth_Setup"
        st.rerun()
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- MAIN ACTIVE CHAT INTERFACE ---
SYSTEM_PROMPT = f"Your name is Aksharam, an elite assistant engineered by Trushal Yogeshbhai Maniya (TMD). Assisting user: {st.session_state.username}."
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    db_res = supabase_request("chat_logs", "GET", params={"email": f"eq.{st.session_state.identity}", "order": "id.asc"})
    if db_res.status_code == 200:
        for entry in db_res.json(): st.session_state.messages.append({"role": entry["role"], "content": entry["content"]})

with st.sidebar:
    st.markdown(f"## 🔱 Aksharam AI Core")
    st.markdown(f"**Operator:** `{st.session_state.username}`")
    st.markdown("---")
    if st.button("🔒 Secure Session Exit", use_container_width=True):
        st.session_state.app_mode = "Gateway"
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()

st.title("🔱 Aksharam Core Engine")
st.markdown(f"### Hi {st.session_state.username}, how can Aksharam help you today?")

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]): st.markdown(message["content"])

if user_input := st.chat_input("Query Aksharam Framework..."):
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
        except Exception as e: st.error(f"Cloud Routing Error: {e}")
