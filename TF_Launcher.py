import subprocess
import webbrowser
import time
import os

# === CONFIG ===
LOGDIR = "Tensorboard"  # Folder where your tensorboard logs are stored
PORT = 6006           # Change if 6006 is busy

def launch_tensorboard():
    if not os.path.exists(LOGDIR):
        print(f"❌ Folder '{LOGDIR}' not found.")
        return

    print(f"🚀 Launching TensorBoard on port {PORT}...")
    tb_proc = subprocess.Popen([
        "tensorboard",
        f"--logdir={LOGDIR}",
        f"--port={PORT}",
        "--reload_interval=5",  # refresh logs every 5 seconds
    ])

    time.sleep(2)  # Wait a moment for the server to start

    # Open browser to TensorBoard
    url = f"http://localhost:{PORT}/"
    print(f"🌐 Opening {url} in your browser...")
    webbrowser.open(url)

    try:
        tb_proc.wait()
    except KeyboardInterrupt:
        print("🛑 TensorBoard stopped by user.")
        tb_proc.terminate()

if __name__ == "__main__":
    launch_tensorboard()
