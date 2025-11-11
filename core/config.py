from pathlib import Path
import json

APP_NAME = "Dofus Window Manager"

CONFIG_DIR = Path.home() / ".config" / "dofus_window_manager"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_FILE = CONFIG_DIR / "config.json"
PROFILES_FILE = CONFIG_DIR / "profiles.json"

SCRIPT_DIR = CONFIG_DIR / "scripts"
SCRIPT_DIR.mkdir(exist_ok=True)

RENAME_SCRIPT = SCRIPT_DIR / "rename_windows.sh"
REORGANIZE_SCRIPT = SCRIPT_DIR / "reorganize_windows.sh"
CLICK_CYCLE_FORWARD = SCRIPT_DIR / "click_cycle_forward.sh"
CYCLE_FORWARD = SCRIPT_DIR / "cycle_forward.sh"
CYCLE_BACKWARD = SCRIPT_DIR / "cycle_backward.sh"
TOGGLE_WORKSPACE = SCRIPT_DIR / "toggle_workspace.sh"

DEFAULT_CLASS_INI = ['Feca', 'Cra', 'Enu', 'Panda', 'Sadi']


def load_json(path, default=None):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}


def save_json(path, data):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass