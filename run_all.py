import subprocess
import time
import webbrowser

# Step 1: Start FastAPI backend
backend = subprocess.Popen(["uvicorn", "main:app", "--reload"])

# Step 2: Give the server time to start
time.sleep(2)

# Step 3: Start Streamlit frontend
frontend = subprocess.Popen(["streamlit", "run", "streamlit_app.py"])

# Optional: Open Streamlit in browser automatically
webbrowser.open("http://localhost:8501")

# Step 4: Keep both running
backend.wait()
frontend.wait()
