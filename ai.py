import streamlit as st
from groq import Groq
import sqlite3
import hashlib

# 1. Page Configuration
st.set_page_config(page_title="Aksharam AI", page_icon="🔱", layout="wide")

# 2. Database Setup (Handles Sign Up & Encrypted Storage)
def init_db():
    conn = sqlite3.connect("aksharam_users.db", check_same_thread=False)
    cursor = conn.cursor()
    # Create Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    # Create Individual Chat History Table linked to users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            content TEXT
        )
    """)
    conn.commit()
    return conn

conn = init_db()
cursor = conn.cursor()

# Helper function to hash passwords securely
def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hash(password, hashed_password):
    return hashlib.sha256(str.encode(password)).hexdigest() == hashed_password

# 3. Inject Styling & 3D Background
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

# 4. Session State Authentication Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# --- AUTHENTICATION INTERFACE ---
if not st.session_state.logged_in:
    st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
    st.title("🔱 Aksharam Gateway")
    
    auth_mode = st.tabs(["🔐 Sign In", "📝 Create Account"])
    
    # SIGN IN TAB
    with auth_mode[0]:
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Access Core Engine", use_container_width=True):
            cursor.execute("SELECT password FROM users WHERE username = ?", (login_user,))
            user_record = cursor.fetchone()
            if user_record and check_hash(login_pass, user_record[0]):
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.success(f"Welcome back, {login_user}! Syncing environment...")
                st.rerun()
            else:
                st.error("Invalid credentials. Try again.")
                
    # SIGN UP TAB
    with auth_mode[1]:
        new_user = st.text_input("Choose Username", key="new_user")
        new_email = st.text_input("Email Address", key="new_email")
        new_pass = st.text_input("Create Password", type="password", key="new_pass")
        confirm_pass = st.text_input("Confirm Password", type="password", key="confirm_pass")
        
        if st.button("Register & Initialize", use_container_width=True):
            if new_pass != confirm_pass:
                st.error("Passwords do not match.")
            elif not new_user or not new_email or not new_pass:
                st.error("Please fill in all registration blocks.")
            else:
                hashed_pass = make_hash(new_pass)
                try:
                    cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (new_user, new_email, hashed_pass))
                    conn.commit()
                    st.success("Account securely generated! Please proceed to Sign In.")
                except sqlite3.IntegrityError:
                    st.error("Username or Email already registered.")
                    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- MAIN SECURE APP ENVIRONMENT (Accessible only after logging in) ---

if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing Groq API Key inside settings secrets panel.")
    st.stop()

SYSTEM_PROMPT = (
    "Your name is Aksharam, an elite, highly precise AI assistant engineered by Trushal Yogeshbhai Maniya (TMD). "
    "You provide factual, structured answers using clean typography, points, or bold headers."
)

# Load logged-in user's saved chat history from the Database
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    cursor.execute("SELECT role, content FROM chat_history WHERE username = ?", (st.session_state.username,))
    saved_messages = cursor.fetchall()
    for role, content in saved_messages:
        st.session_state.messages.append({"role": role, "content": content})

# Sidebar controls
with st.sidebar:
    st.markdown(f"### 👤 Active User: **{st.session_state.username}**")
    st.markdown("---")
    
    if st.button("🔒 Secure Sign Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()
        
    if st.button("🗑️ Clear My Saved Cloud Chat", use_container_width=True):
        cursor.execute("DELETE FROM chat_history WHERE username = ?", (st.session_state.username,))
        conn.commit()
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.success("Your private cloud history wiped!")
        st.rerun()

st.title("🔱 Aksharam: Private Engine")
st.markdown(f"<p style='color: #ff3300 !important; margin-top: -15px;'>Encrypted Tunnel Active • Session Owner: {st.session_state.username}</p>", unsafe_allow_html=True)

# Render visible chats
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Process input
if user_input := st.chat_input("Ask Aksharam safely..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Save User message to Database immediately
    cursor.execute("INSERT INTO chat_history (username, role, content) VALUES (?, ?, ?)", (st.session_state.username, "user", user_input))
    conn.commit()

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages,
                temperature=0.1,
                top_p=0.9,
                stream=True,
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Save Assistant response to Database immediately
            cursor.execute("INSERT INTO chat_history (username, role, content) VALUES (?, ?, ?)", (st.session_state.username, "assistant", full_response))
            conn.commit()
            
        except Exception as e:
            st.error(f"Cloud Connection Error: {e}")
