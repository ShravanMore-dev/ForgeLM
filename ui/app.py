import streamlit as st
import requests
import os
import json

# Configuration: Read the internal Docker bridge URL passed from docker-compose
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/troubleshoot")
BASE_API = API_URL.replace("/troubleshoot", "")

st.set_page_config(page_title="ForgeLM · SRE Agent", page_icon="⚡", layout="wide")

# =============================================================================
# PRODUCTION GEMINI/CLAUDE DARK MODE THEME (Optimized for 2K/4K Displays)
# =============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --bg-app: #131314;
        --bg-surface: #1E1F20;
        --bg-surface-elevated: #282A2C;
        --border-subtle: #333538;
        --border-focus: #5E6368;
        --text-pure: #FFFFFF;
        --text-muted: #9AA0A6;
        --accent-blue: #8AB4F8;
        --accent-blue-soft: rgba(138, 180, 248, 0.12);
    }

    /* Global Reset & Canvas */
    html, body, .stApp, .main, [data-testid="stHeader"] {
        background-color: var(--bg-app) !important;
        font-family: 'Inter', sans-serif !important;
        color: var(--text-pure) !important;
    }

    /* Constrain and Center Chat Feed */
    .main .block-container {
        max-width: 860px !important;
        padding-top: 3.5rem !important;
        padding-bottom: 8rem !important;
        margin: 0 auto !important;
    }

    /* Constrain and Center Floating Bottom Input Bar */
    [data-testid="stBottomBlockContainer"] {
        background: linear-gradient(180deg, rgba(19, 19, 20, 0) 0%, rgba(19, 19, 20, 0.9) 35%, rgba(19, 19, 20, 1) 100%) !important;
        padding-bottom: 1.5rem !important;
    }
    
    [data-testid="stBottomBlockContainer"] > div {
        max-width: 860px !important;
        margin: 0 auto !important;
    }

    [data-testid="stChatInput"] {
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 28px !important;
        padding: 4px 10px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.2s ease-in-out;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: var(--border-focus) !important;
        background-color: var(--bg-surface-elevated) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: var(--text-pure) !important;
        font-size: 0.98rem !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: var(--text-muted) !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #18191A !important;
        border-right: 1px solid var(--border-subtle) !important;
    }

    [data-testid="stSidebar"] h3 {
        color: var(--text-pure) !important;
        font-size: 1.1rem;
        font-weight: 600;
    }

    /* File Uploader Fix */
    [data-testid="stFileUploaderDropzone"] {
        background-color: var(--bg-surface) !important;
        border: 1px dashed var(--border-subtle) !important;
        border-radius: 12px !important;
        padding: 1.2rem 0.5rem !important;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--accent-blue) !important;
    }

    [data-testid="stFileUploaderDropzone"] * {
        color: var(--text-muted) !important;
    }

    /* Sidebar Buttons */
    div[data-testid="stButton"] button {
        background-color: var(--bg-surface) !important;
        color: var(--text-pure) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        font-size: 0.92rem !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.15s ease;
    }

    div[data-testid="stButton"] button:hover {
        background-color: var(--bg-surface-elevated) !important;
        border-color: var(--border-focus) !important;
        color: var(--text-pure) !important;
    }

    /* Modern Header Section */
    .hero-container {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 2rem;
    }

    .hero-badge {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: var(--accent-blue-soft);
        border: 1px solid rgba(138, 180, 248, 0.25);
        color: var(--accent-blue);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
    }

    .hero-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text-pure);
        letter-spacing: -0.02em;
        margin: 0;
        line-height: 1.1;
    }

    .hero-subtitle {
        font-size: 0.92rem;
        color: var(--text-muted);
        margin: 4px 0 0 0;
    }

    /* Starter Cards Grid */
    .cards-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 14px;
        margin-top: 1.5rem;
    }

    .starter-card {
        background-color: var(--bg-surface);
        border: 1px solid var(--border-subtle);
        border-radius: 14px;
        padding: 1.1rem;
        transition: all 0.2s ease;
    }

    .starter-card:hover {
        border-color: var(--border-focus);
        background-color: var(--bg-surface-elevated);
        transform: translateY(-2px);
    }

    .card-icon {
        font-size: 1.25rem;
        margin-bottom: 0.6rem;
    }

    .card-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-pure);
        margin-bottom: 0.3rem;
    }

    .card-prompt {
        font-size: 0.85rem;
        color: var(--text-muted);
        line-height: 1.45;
    }

    /* Chat Messages & Code Blocks */
    [data-testid="stChatMessage"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0.8rem 0 1.6rem 0 !important;
    }

    [data-testid="stChatMessage"] p {
        font-size: 1.02rem !important;
        line-height: 1.65 !important;
        color: var(--text-pure) !important;
    }

    code {
        font-family: 'JetBrains Mono', monospace !important;
        background-color: var(--bg-surface) !important;
        color: var(--accent-blue) !important;
        padding: 0.2rem 0.45rem !important;
        border-radius: 6px !important;
        font-size: 0.88em !important;
    }

    pre {
        background-color: #0E0F10 !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
    }

    pre code {
        background-color: transparent !important;
        color: #E8EAED !important;
    }

    /* Context Dropdown Expander */
    [data-testid="stExpander"] {
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 12px !important;
        margin-top: 0.8rem !important;
    }

    [data-testid="stExpander"] summary {
        font-size: 0.88rem !important;
        color: var(--text-muted) !important;
    }
</style>
""", unsafe_allow_html=True)

# --- State Initialization ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "contexts" not in st.session_state:
    st.session_state.contexts = {}
if "tools" not in st.session_state:
    st.session_state.tools = {}
if "telemetry" not in st.session_state:
    st.session_state.telemetry = {}

# --- Header Section ---------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">⚡</div>
    <div>
        <h1 class="hero-title">ForgeLM</h1>
        <p class="hero-subtitle">Autonomous Site Reliability & Incident Diagnostic Agent</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Sidebar Controls -------------------------------------------------------
with st.sidebar:
    st.markdown("### 📚 Knowledge Base")
    st.caption("Upload runbooks (.txt, .md, .pdf) to expand ForgeLM's memory index.")
    
    uploaded_file = st.file_uploader("", type=["txt", "md", "pdf"], label_visibility="collapsed")

    if st.button("Ingest Document", use_container_width=True):
        if uploaded_file is not None:
            with st.spinner("Transmitting to ForgeLM Backend..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                try:
                    response = requests.post(f"{BASE_API}/ingest", files=files)
                    if response.status_code == 200:
                        st.success("Vector DB reloaded successfully!")
                    else:
                        st.error(f"Failed to ingest: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot reach ForgeLM backend.")
        else:
            st.error("Please select a file to upload first.")
            
    st.divider()
    if st.button("🗑️ Clear Session", use_container_width=True):
        st.session_state.messages = []
        st.session_state.contexts = {}
        st.session_state.tools = {}
        st.session_state.telemetry = {}
        st.rerun()

# --- Starter Suggestions (Empty State) --------------------------------------
if len(st.session_state.messages) == 0:
    st.markdown("""
    <div class="cards-grid">
        <div class="starter-card">
            <div class="card-icon">🚨</div>
            <div class="card-title">Incident Triage</div>
            <div class="card-prompt">"HTTP 503 Service Unavailable on Payment Gateway pod cluster."</div>
        </div>
        <div class="starter-card">
            <div class="card-icon">📖</div>
            <div class="card-title">Runbook Lookup</div>
            <div class="card-prompt">"What is the SOP for rotating database credentials during a breach?"</div>
        </div>
        <div class="starter-card">
            <div class="card-icon">⚡</div>
            <div class="card-title">Diagnostics</div>
            <div class="card-prompt">"Explain OOMKilled error code 137 in Kubernetes worker nodes."</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Render Chat Message History --------------------------------------------
for idx, msg in enumerate(st.session_state.messages):
    avatar_icon = "⚡" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])
        
        # Render Tool Output
        if msg["role"] == "assistant" and idx in st.session_state.tools:
            tool_info = st.session_state.tools[idx]
            with st.expander(f"🛠️ Tool Invoked: `{tool_info['tool']}`"):
                st.code(f"Input Arguments: {json.dumps(tool_info.get('args', {}), indent=2)}\n\nOutput:\n{tool_info.get('result', '')}", language="json")

        # Render Context Expander
        if msg["role"] == "assistant" and idx in st.session_state.contexts:
            with st.expander("🔍 View Retrieved Runbook Context"):
                st.caption(st.session_state.contexts[idx])
        
        # Render Telemetry Pill
        if msg["role"] == "assistant" and idx in st.session_state.telemetry:
            t_data = st.session_state.telemetry[idx]
            st.markdown(
                f"<span style='color:#9AA0A6; font-size:0.75rem; font-family:monospace;'>"
                f"⚡ Latency: {t_data.get('latency_ms', 0)}ms | 🧠 VRAM: {t_data.get('vram_allocated_gb', 0)} GB"
                f"</span>",
                unsafe_allow_html=True
            )

# SSE Generator Function
def stream_response(response, current_idx):
    for line in response.iter_lines(decode_unicode=True):
        if line and line.startswith("data: "):
            raw_json = line[6:]
            try:
                event = json.loads(raw_json)
                event_type = event.get("type")
                
                if event_type == "context":
                    st.session_state.contexts[current_idx] = event.get("content", "")
                elif event_type == "token":
                    yield event.get("content", "")
                elif event_type == "tool_executed":
                    st.session_state.tools[current_idx] = event
                elif event_type == "telemetry":
                    st.session_state.telemetry[current_idx] = event
            except json.JSONDecodeError:
                continue

# --- User Chat Input Interaction --------------------------------------------
if prompt := st.chat_input("Describe the infrastructure or service issue..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚡"):
        history_payload = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages[:-1]
        ]
        payload = {"instruction": prompt, "history": history_payload}

        try:
            response = requests.post(API_URL, json=payload, stream=True)
            if response.status_code == 200:
                msg_idx = len(st.session_state.messages)
                full_response = st.write_stream(stream_response(response, msg_idx))
                
                # Live render tool card if just populated
                if msg_idx in st.session_state.tools:
                    tool_info = st.session_state.tools[msg_idx]
                    with st.expander(f"🛠️ Tool Invoked: `{tool_info['tool']}`"):
                        st.code(f"Input Arguments: {json.dumps(tool_info.get('args', {}), indent=2)}\n\nOutput:\n{tool_info.get('result', '')}", language="json")

                if msg_idx in st.session_state.contexts:
                    with st.expander("🔍 View Retrieved Runbook Context"):
                        st.caption(st.session_state.contexts[msg_idx])
                        
                if msg_idx in st.session_state.telemetry:
                    t_data = st.session_state.telemetry[msg_idx]
                    st.markdown(
                        f"<span style='color:#9AA0A6; font-size:0.75rem; font-family:monospace;'>"
                        f"⚡ Latency: {t_data.get('latency_ms', 0)}ms | 🧠 VRAM: {t_data.get('vram_allocated_gb', 0)} GB"
                        f"</span>",
                        unsafe_allow_html=True
                    )

                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.error(f"API Error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot reach ForgeLM backend. Check if the API container is running.")