#!/usr/bin/env python3
"""
Entrée principale pour l'application.
"""
import sys

try:
    from PyQt6 import QtWidgets
except ImportError:
    print("❌ PyQt6 required. Install with: pip install PyQt6")
    sys.exit(1)

from ui.main_window import DofusManager
from core.config import APP_NAME


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    # Icon (use default system icon)
    try:
        app.setWindowIcon(app.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ComputerIcon))
    except Exception:
        pass

    window = DofusManager()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()