# 🚀 How to Deploy on Streamlit Cloud

Your project is now **Deployment-Ready**! Follow these steps to host it online:

### 1. Push to GitHub
Ensure all your files (especially `streamlit_app.py` and `requirements.txt` in the root) are pushed to a public or private GitHub repository.

### 2. Connect to Streamlit Cloud
1.  Go to [share.streamlit.io](https://share.streamlit.io).
2.  Click **"New app"**.
3.  Select your repository and branch.
4.  **Main file path**: Set this to `streamlit_app.py` (not app.py).

### 3. Set Up API Keys (Secrets)
Before clicking Deploy, click **"Advanced settings..."** and go to **"Secrets"**. Paste your API keys in this format:

```toml
GEMINI_API_KEY_MASTER = "your_key_here"
GEMINI_API_KEY_FUNDAMENTAL = "your_key_here"
GROQ_API_KEY_TECHNICAL = "your_key_here"
GROQ_API_KEY_SENTIMENT = "your_key_here"
BRAVE_SEARCH_API_KEY = "your_key_here" (Optional)
```

### 4. Deploy!
Click **"Deploy!"**. Streamlit will install all dependencies from `requirements.txt` and start your backend + frontend automatically.

---
**Note**: The first deployment might take 2-4 minutes as it installs Python packages.
