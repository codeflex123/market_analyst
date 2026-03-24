import subprocess
import time
import os
import sys
import socket
import streamlit as st

# MUST BE THE FIRST COMMAND
st.set_page_config(page_title="Market Analyst AI", layout="wide", page_icon="📈")

# Function to check if a port is already in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

# Start backend once
@st.cache_resource
def start_backend():
    port = 8000
    if is_port_in_use(port):
        return "Backend already running"
        
    python_path = sys.executable
    cmd = [python_path, "-m", "uvicorn", "phase_6.src.api.main:app", "--host", "0.0.0.0", "--port", str(port)]
    env = os.environ.copy()
    env["PYTHONPATH"] = f".:{env.get('PYTHONPATH', '')}"
    
    process = subprocess.Popen(cmd, env=env)
    
    # Wait for the backend
    for _ in range(15):
        if is_port_in_use(port): return "Backend started"
        time.sleep(1)
    return "Backend failed to start"

def run_app():
    # 1. Sidebar selection at the TOP level
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2622/2622649.png", width=100)
        st.title("Market Analyst AI")
        st.markdown("---")
        analysis_mode = st.radio(
            "Navigation Mode",
            ["Market Analyst", "Stock Comparison", "Portfolio Analysis"],
            index=0
        )
        st.markdown("---")
        st.info(f"📍 Mode: **{analysis_mode}**")
        st.markdown("---")
        with st.expander("🛡️ About"):
            st.caption("Multi-agent Institutional Portfolio Intelligence.")

    # 2. Start backend
    _ = start_backend()
    
    # 3. Dynamic import and run
    try:
        from phase_6.src.ui.app import main
        main(analysis_mode)
    except Exception as e:
        st.error("### ❌ UI Rendering Error")
        st.exception(e)

if __name__ == "__main__":
    run_app()
