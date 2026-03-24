import subprocess
import time
import os
import sys
import socket
import streamlit as st
from phase_6.src.ui.app import main

# Function to check if a port is already in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Use st.cache_resource to ensure this runs only once per app session (globally)
@st.cache_resource
def start_backend():
    port = 8000
    if is_port_in_use(port):
        st.info(f"Port {port} is already in use, assuming backend is running.")
        return None
        
    python_path = sys.executable
    cmd = [
        python_path, "-m", "uvicorn", 
        "phase_6.src.api.main:app", 
        "--host", "0.0.0.0", 
        "--port", str(port)
    ]
    
    env = os.environ.copy()
    env["PYTHONPATH"] = f".:{env.get('PYTHONPATH', '')}"
    
    # Start the backend as a background process
    process = subprocess.Popen(cmd, env=env)
    
    # Wait for the backend to be ready
    max_retries = 10
    for i in range(max_retries):
        if is_port_in_use(port):
            break
        time.sleep(1)
        
    return process

# Entry point for Streamlit
def run_app():
    # 1. Start backend as a global resource
    _ = start_backend()
    
    # 2. Run the UI logic
    main()

if __name__ == "__main__":
    run_app()
