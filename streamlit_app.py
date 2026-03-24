import subprocess
import time
import os
import sys
import socket
import streamlit as st

# Function to check if a port is already in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # On some cloud environments, localhost might be restricted
        # We try 0.0.0.0 as well
        return s.connect_ex(('127.0.0.1', port)) == 0

# Use st.cache_resource to ensure this runs only once per app session (globally)
@st.cache_resource
def start_backend():
    port = 8000
    if is_port_in_use(port):
        return "Backend already running"
        
    python_path = sys.executable
    # Absolute path to the main.py
    cmd = [
        python_path, "-m", "uvicorn", 
        "phase_6.src.api.main:app", 
        "--host", "0.0.0.0", 
        "--port", str(port)
    ]
    
    env = os.environ.copy()
    # Add current directory to PYTHONPATH
    current_dir = os.getcwd()
    env["PYTHONPATH"] = f"{current_dir}:{env.get('PYTHONPATH', '')}"
    
    # Start the backend as a background process
    process = subprocess.Popen(cmd, env=env)
    
    # Wait for the backend to be ready (up to 20 seconds)
    max_retries = 20
    for i in range(max_retries):
        if is_port_in_use(port):
            return "Backend started"
        time.sleep(1)
        
    return "Backend failed to start in time"

# Entry point for Streamlit
def run_app():
    # 1. Start backend as a global resource with status updates
    with st.spinner("Initializing Market Analyst Backend..."):
        status = start_backend()
    
    # 2. Run the UI logic
    try:
        # Dynamic import to avoid early st.set_page_config calls
        from phase_6.src.ui.app import main
        main()
    except Exception as e:
        st.error("### ❌ UI Rendering Error")
        st.write("The backend is running, but the frontend failed to load.")
        st.exception(e)
        st.info("Check the Streamlit Logs (bottom right) for more details.")

if __name__ == "__main__":
    run_app()
