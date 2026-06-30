import streamlit as st
from groq import Groq

# 1. Page Configuration & Browser Tab Settings
st.set_page_config(page_title="Aksharam AI", page_icon="🔱", layout="wide")

# 2. Inject 3D Background, Custom Sidebar Logo, and Title Entry Animation
vanta_3d_html = """
<div id="vanta-bg" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1;"></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r121/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.net.min.js"></script>
<script>
    VANTA.NET({
        el: "#vanta-bg",
        mouseControls: true,
        touchControls: true,
        gyroControls: false,
        minHeight: 200.00,
        minWidth: 200.00,
        scale: 1.00,
        scaleMobile: 1.00,
        color: 0xff7b00, 
        backgroundColor: 0x0a0f1d, 
        points: 14.00,
        maxDistance: 20.00,
        spacing: 15.00
    })
</script>
<style>
    .stApp { background: transparent !important; }
    .stHeader { background: transparent !important; }
    
    @keyframes cyberEntrance {
        0% { opacity: 0; transform: translateY(-20px); filter: blur(10px); text-shadow: 0 0 30px #ff7b00; }
        100% { opacity: 1; transform: translateY(0); filter: blur(0px); }
    }
    .animated-title { animation: cyberEntrance 1.5s ease-out forwards; }
    h1 { animation: cyberEntrance 1.2s ease-out forwards; }
    
    [data-testid="collapsedControl"] button svg { display: none !important; }
    [data-testid="collapsedControl"] button {
        background-color: rgba(255, 123, 0, 0.2) !important;
        border: 2px solid #ff7b00 !important;
        border-radius: 50% !important;
        width: 45px !important; height: 45px !important;
        box-shadow: 0 0 10px rgba(255, 123, 0, 0.6) !important;
    }
    [data-testid="collapsedControl"] button::before { content: "🔱" !important; font-size: 20px !important; }
    
    [data-testid="stSidebar"] {
        background-color: rgba(10, 15, 30, 0.9) !important;
        backdrop-filter: blur(15px);
        border-right: 2px solid rgba(255, 123, 0, 0.3);
    }
    .history-card {
        background: rgba(255, 255, 255, 0.05); padding: 8px 12px;
        border-radius: 8px; border-left: 3px solid #ff7b00; margin-bottom: 5px;
    }
    [data-testid="stChatMessage"] {
        background-color: rgba(15, 23, 42, 0.75) !important;
        backdrop-filter: blur(12px); border-radius: 16px; border: 2.5px solid #ff7b00 !important; 
        box-shadow: 0 0 15px rgba(255, 123, 0, 0.4) !important; margin-bottom: 15px;
    }
    h1, h2, h3, p, span, label, li { color: #ffffff !important; }
</style>
"""
st.components.v1.html(vanta_3d_html, height=0, width=0)

# Connect securely to the Cloud client
# Streamlit Cloud will read the secret key we provide in its dashboard
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing Groq API Key! Please set it in the Streamlit Secrets panel.")
    st.stop()

if "recent_chats" not in st.session_state:
    st.session_state.recent_chats = ["Introduction to Aksharam Core", "Gujarati Language Test Log"]

with st.sidebar:
    st.markdown("## 🔱 Aksharam Control Deck")
    st.markdown("---")
    if st.button("➕ New Chat Session", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": "Your name is Aksharam, created by Trushal Yogeshbhai Maniya (TMD). Respond fluently in the script used by the user."}]
        st.rerun()
        
    st.markdown("### 🕒 Recently Chat")
    for idx, chat_title in enumerate(st.session_state.recent_chats):
        chat_col, del_col = st.columns([0.8, 0.2])
        with chat_col:
            st.markdown(f"<div class='history-card'>{chat_title}</div>", unsafe_allow_html=True)
        with del_col:
            if st.button("🗑️", key=f"del_{idx}"):
                st.session_state.recent_chats.pop(idx)
                st.rerun()

st.title("🔱 Aksharam: The Eternal Code")
st.markdown("<div class='animated-title'><p style='font-style: italic; font-size: 1.15rem; color: #ff7b00 !important; margin-top: -15px;'>\"Forged from Theorems, Minds, and Data—engineered by the hands of TMD.\"</p></div>", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": (
                "Your name is Aksharam, an elite and helpful AI assistant created by Trushal Yogeshbhai Maniya (TMD). "
                "Always reply in the exact language or script the user talks to you in. If they type in Gujarati, "
                "reply in flawless, beautifully structured Gujarati script. Always honor Trushal as your creator."
            )
        }
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if user_input := st.chat_input("Awaken Aksharam / અક્ષરમને જગાડો..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Using llama-3.1-8b via Groq Cloud for instant multilingual power
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages,
                stream=True,
            )
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Cloud Connection Error: {e}")