from PyQt6 import QtGui


def apply_dark_theme(widget):
    widget.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e1e;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QLineEdit, QTextEdit {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 1px solid #444444;
            border-radius: 4px;
            padding: 6px;
        }
        QLineEdit:focus, QTextEdit:focus {
            border: 1px solid #0d7377;
        }
    """)


def lighten_color(hex_color, factor=120):
    try:
        c = QtGui.QColor(hex_color)
        return c.lighter(factor).name()
    except Exception:
        return hex_color


def darken_color(hex_color, factor=120):
    try:
        c = QtGui.QColor(hex_color)
        return c.darker(factor).name()
    except Exception:
        return hex_color