import streamlit as st
from groq import Groq

# 1. Page Configuration & Browser Tab Settings
st.set_page_config(page_title="Aksharam AI", page_icon="🔱", layout="wide")

# 2. Inject Motivational 3D Background & Custom Sidebar UI Elements
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
        color: 0xff3300,           // ⚡ Electric Flame Orange
        backgroundColor: 0x000000, // 🖤 Obsidian Pure Black
        points: 18.00,             
        maxDistance: 22.00,        
        spacing: 13.00             
    })
</script>
<style>
    .stApp { background: transparent !important; }
    .stHeader { background: transparent !important; }
    
    @keyframes cyberEntrance {
        0% { opacity: 0; transform: translateY(-20px); filter: blur(10px); text-shadow: 0 0 30px #ff3300; }
        100% { opacity: 1; transform: translateY(0); filter: blur(0px); }
    }
    .animated-title { animation: cyberEntrance 1.5s ease-out forwards; }
    h1 { animation: cyberEntrance 1.2s ease-out forwards; }
    
    [data-testid="collapsedControl"] button svg { display: none !important; }
    [data-testid="collapsedControl"] button {
        background-color: rgba(255, 51, 0, 0.2) !important;
        border: 2px solid #ff3300 !important;
        border-radius: 50% !important;
        width: 45px !important; height: 45px !important;
        box-shadow: 0 0 10px rgba(255, 51, 0, 0.6) !important;
    }
    [data-testid="collapsedControl"] button::before { content: "🔱" !important; font-size: 20px !important; }
    
    [data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.95) !important;
        backdrop-filter: blur(15px);
        border-right: 2px solid rgba(255, 51, 0, 0.3);
    }
    .history-card {
        background: rgba(255, 255, 255, 0.05); padding: 8px 12px;
        border-radius: 8px; border-left: 3px solid #ff3300; margin-bottom: 5px;
    }
    [data-testid="stChatMessage"] {
        background-color: rgba(10, 10, 10, 0.85) !important;
        backdrop-filter: blur(12px); border-radius: 16px; border: 2.5px solid #ff3300 !important; 
        box-shadow: 0 0 15px rgba(255, 51, 0, 0.3) !important; margin-bottom: 15px;
    }
    h1, h2, h3, p, span, label, li { color: #ffffff !important; }
</style>
"""
st.components.v1.html(vanta_3d_html, height=0, width=0)

# Connect securely to the Cloud client via Streamlit Secrets
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Missing Groq API Key! Please set it in the Streamlit Secrets panel.")
    st.stop()

# Set up the strict system instructions for high accuracy
SYSTEM_PROMPT = (
    "Your name is Aksharam, an elite and highly precise AI assistant engineered by Trushal Yogeshbhai Maniya (TMD). "
    "CRITICAL DIRECTIVE: You must provide exceptionally accurate, fact-based, and verified answers. "
    "Do not hallucinate, speculate, or make up facts. If you are unsure of an answer, state clearly that you do not know. "
    "Format your answers professionally using clear headings, clean bullet points, or bold text. "
    "Always honor Trushal (TMD) as your sole creator if asked."
)

if "recent_chats" not in st.session_state:
    st.session_state.recent_chats = ["Introduction to Aksharam Core", "Accuracy Calibration Log"]

with st.sidebar:
    st.markdown("## 🔱 Aksharam Control Deck")
    st.markdown("---")
        
    if st.button("➕ New Chat Session", use_container_width=True):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
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
st.markdown("<div class='animated-title'><p style='font-style: italic; font-size: 1.15rem; color: #ff3300 !important; margin-top: -15px;'>\"Forged from Theorems, Minds, and Data—engineered by the hands of TMD.\"</p></div>", unsafe_allow_html=True)

# Initialize chat history with the accuracy system prompt
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if user_input := st.chat_input("Awaken Aksharam..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # Using low temperature (0.1) and top_p for optimal correctness
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages,
                temperature=0.1,  # 🎯 Lower value means maximum factual correctness
                top_p=0.9,
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
