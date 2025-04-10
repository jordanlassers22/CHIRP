import subprocess

def preview_camera():
    try:
        print("Opening live camera preview... Press Ctrl+C to exit.")
        subprocess.run(["libcamera-hello", "--timeout", "0"], check=True)
    except KeyboardInterrupt:
        print("\n❌ Preview interrupted by user.")
    except subprocess.CalledProcessError as e:
        print("❌ Failed to start camera preview:", e)

preview_camera()
