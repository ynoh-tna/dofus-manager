import os
import subprocess


def make_executable(path):
    try:
        os.chmod(path, 0o755)
    except Exception:
        pass


def run_cmd(cmd, timeout=5):
    """Execute a command and return (stdout, stderr, returncode)"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1