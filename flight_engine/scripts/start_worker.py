import sys
import os
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    # Start Dramatiq worker pointing to tasks module
    subprocess.run(["dramatiq", "workers.tasks", "-p", "2", "-t", "2"])
