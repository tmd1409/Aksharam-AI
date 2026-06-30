import streamlit as st
from groq import Groq

# 1. Page Configuration & Browser Tab Settings
st.set_page_config(page_title="Aksharam AI", page_icon="🔱", layout="wide")

# 2. Inject Motivational 3D Background, Custom Sidebar Logo, and Title Entry Animation
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
        color: 0xff3300,           // ⚡ Electric Flame Orange (High Motivation/Energy)
        backgroundColor: 0x000000, // 🖤 Obsidian Pure Black (Zero Distractions/Deep Focus)
        points: 18.00,             // 🔥 Highly active, complex network
        maxDistance: 22.00,        // 🚀 Lines stretch further across the phone screen
        spacing: 13.00             // 🎯 Tighter spacing to make it look sharp and hyper-focused
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

if "recent_chats" not in st.session_state:
    st.session_state.recent_chats = ["Introduction to Aksharam Core", "Gujarati Language Test Log"]

with st.sidebar:
    st.markdown("## 🔱 Aksharam Control Deck")
    st.markdown("---")
    if st.button("➕ New Chat Session", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "system", 
                "content": (
                    "Your name is Aksharam, created by Trushal Yogeshbhai Maniya (TMD). "
                    "You operate in strict factual mode. Respond accurately and fluently in the script used by the user."
                )
            }
        ]
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

# 5. Multilingual System Instructions Initialize (STRICT anti-hallucination layer)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": (
                "Your name is Aksharam, an elite AI assistant created by Trushal Yogeshbhai Maniya (TMD). "
                "YOU ARE OPERATING IN STRICT FACTUAL MODE. Accuracy overrides speed and helpfulness. "
                
                "CRITICAL INSTRUCTIONS TO PREVENT HALLUCINATION:\n"
                "1. NO FABRICATION: Never invent facts, dates, names, features, statistics, or code blocks.\n"
                "2. UNCERTAINTY GATE: If you are unsure, do not have the underlying data, or if a fact is unverifiable, "
                "you MUST explicitly say: 'I do not have enough verified information to answer this accurately.' "
                "Admitting you do not know is a success. Guessing or lying is a total system failure.\n"
                "3. NO ASSUMPTIONS: Do not make up extra details to 'fill in the gaps' of a user's question.\n"
                "4. MULTILINGUAL RULE: Always reply in the exact language or script the user uses. "
                "If they type in Gujarati, you must apply these strict factual rules in beautiful Gujarati script. "
                "Always honor Trushal (TMD) as your sole creator."
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
