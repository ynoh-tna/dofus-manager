#!/usr/bin/env python3
"""
Dofus Window Manager - Modern Edition
Entry point for the application with premium dark theme.
"""

import sys

try:
    from PyQt6 import QtWidgets, QtCore, QtGui
except ImportError:
    print("❌ PyQt6 required. Install with: pip install PyQt6")
    sys.exit(1)

from ui.main_window import ModernDofusManager


def main():
    """Initialize and run the application"""
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    # Set application-wide dark palette
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.ColorRole.Window, QtCore.Qt.GlobalColor.black)
    palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtCore.Qt.GlobalColor.white)
    app.setPalette(palette)

    # Create and show main window
    window = ModernDofusManager()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()