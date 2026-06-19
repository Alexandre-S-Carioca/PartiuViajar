import sys
import os
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    # Start Dramatiq worker pointing to tasks module portably on all platforms (inc. Windows)
    subprocess.run([sys.executable, "-m", "dramatiq", "workers.tasks", "-p", "2", "-t", "2"])
