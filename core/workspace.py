import subprocess


def get_workspaces():
    """Return list of (num, name) tuples for workspaces using wmctrl."""
    try:
        result = subprocess.run(['wmctrl', '-d'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            workspaces = []
            for line in result.stdout.strip().split('\n'):
                parts = line.split(None, 9)
                if len(parts) >= 10:
                    ws_num = parts[0]
                    ws_name = parts[9]
                    workspaces.append((ws_num, ws_name))
            return workspaces
        return []
    except Exception:
        return []