import subprocess
import sys
import os

def main():
    # Detect the root directory (where startup.py resides)
    root_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(root_dir)

    # Path to virtual environment python
    if sys.platform == "win32":
        venv_python = os.path.join(root_dir, '.venv', 'Scripts', 'python.exe')
    else:
        venv_python = os.path.join(root_dir, '.venv', 'bin', 'python')

    # Fallback to system python if venv doesn't exist
    if not os.path.exists(venv_python):
        print("Warning: .venv not found. Using system Python.")
        venv_python = sys.executable

    dashboard_script = os.path.join(root_dir, 'src', 'dashboard.py')

    if not os.path.exists(dashboard_script):
        print(f"Error: Could not find {dashboard_script}")
        sys.exit(1)

    print("========================================")
    print("  Market Intelligence Dashboard")
    print("========================================")
    print(f"Starting server from: {dashboard_script}")
    print("Press Ctrl+C to stop.\n")

    try:
        # Run the dashboard script
        subprocess.run([venv_python, dashboard_script], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except subprocess.CalledProcessError as e:
        print(f"\nError: Dashboard exited with code {e.returncode}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")

if __name__ == "__main__":
    main()
