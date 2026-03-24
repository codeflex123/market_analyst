import subprocess
import time
import os
import sys
import streamlit as st

# Function to start FastAPI in the background
def start_backend():
    # Use the same python executable as streamlit
    python_path = sys.executable
    cmd = [
        python_path, "-m", "uvicorn", 
        "phase_6.src.api.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000"
    ]
    # Set PYTHONPATH to include the current directory
    env = os.environ.copy()
    env["PYTHONPATH"] = f".:{env.get('PYTHONPATH', '')}"
    
    process = subprocess.Popen(cmd, env=env)
    return process

# Entry point for Streamlit
if __name__ == "__main__":
    # 1. Start backend if not already started
    if "backend_started" not in st.session_state:
        st.session_state.backend_process = start_backend()
        st.session_state.backend_started = True
        # Give the backend a moment to warm up
        time.sleep(2)
    
    # 2. Import and run the UI logic
    from phase_6.src.ui.app import main
    main()
