from PyQt6 import QtGui


def apply_compact_theme(widget):
    """
    Apply modern dark theme optimized for compact window.
    Designed for readability and visual clarity.
    """
    widget.setStyleSheet("""
        /* Main window background */
        QMainWindow {
            background-color: #1a1a1a;
        }
        
        /* Default widget styling */
        QWidget {
            background-color: #1a1a1a;
            color: #ffffff;
            font-family: 'Segoe UI', 'Ubuntu', sans-serif;
        }
        
        /* Input fields */
        QLineEdit, QTextEdit {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 2px solid #444444;
            border-radius: 4px;
            padding: 6px 8px;
            font-size: 11px;
        }
        
        QLineEdit:focus, QTextEdit:focus {
            border: 2px solid #0d7377;
            background-color: #333333;
        }
        
        /* Combo boxes */
        QComboBox {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 2px solid #444444;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 11px;
        }
        
        QComboBox:hover {
            border: 2px solid #555555;
        }
        
        QComboBox:focus {
            border: 2px solid #0d7377;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid #aaaaaa;
            width: 0;
            height: 0;
        }
        
        QComboBox QAbstractItemView {
            background-color: #2b2b2b;
            color: #ffffff;
            selection-background-color: #0d7377;
            border: 1px solid #444444;
        }
        
        /* Group boxes */
        QGroupBox {
            background-color: #242424;
            border: 2px solid #333333;
            border-radius: 6px;
            margin-top: 8px;
            padding-top: 8px;
            font-size: 11px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: #aaaaaa;
        }
        
        /* Radio buttons */
        QRadioButton {
            color: #ffffff;
            spacing: 6px;
        }
        
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
            border-radius: 8px;
            border: 2px solid #555555;
            background-color: #2b2b2b;
        }
        
        QRadioButton::indicator:checked {
            background-color: #0d7377;
            border: 2px solid #14b8a6;
        }
        
        QRadioButton::indicator:hover {
            border: 2px solid #777777;
        }
        
        /* Scrollbars */
        QScrollBar:vertical {
            background-color: #2b2b2b;
            width: 10px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #555555;
            border-radius: 5px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #666666;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        /* Tooltips */
        QToolTip {
            background-color: #2b2b2b;
            color: #ffffff;
            border: 2px solid #0d7377;
            border-radius: 4px;
            padding: 6px 8px;
            font-size: 11px;
        }
    """)


def get_icon_button_style(color, size=32):
    """
    Generate stylesheet for circular icon buttons.
    
    Args:
        color: Base color for the button
        size: Button size in pixels (default: 32)
    
    Returns:
        CSS stylesheet string
    """
    hover_color = lighten_color(color, 120)
    pressed_color = darken_color(color, 120)
    
    return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            border-radius: {size // 2}px;
            font-size: {size // 2}px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        QPushButton:pressed {{
            background-color: {pressed_color};
        }}
    """


def get_action_button_style(color):
    """
    Generate stylesheet for action buttons with rounded corners.
    
    Args:
        color: Base color for the button
    
    Returns:
        CSS stylesheet string
    """
    hover_color = lighten_color(color, 115)
    pressed_color = darken_color(color, 115)
    
    return f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            font-weight: bold;
            font-size: 11px;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        QPushButton:pressed {{
            background-color: {pressed_color};
        }}
    """


def lighten_color(hex_color, factor=120):
    """
    Lighten a hex color by a given factor.
    
    Args:
        hex_color: Hex color string (e.g., '#0d7377')
        factor: Lightening factor (100-200, default: 120)
    
    Returns:
        Lightened hex color string
    """
    try:
        color = QtGui.QColor(hex_color)
        return color.lighter(factor).name()
    except Exception:
        return hex_color


def darken_color(hex_color, factor=120):
    """
    Darken a hex color by a given factor.
    
    Args:
        hex_color: Hex color string (e.g., '#0d7377')
        factor: Darkening factor (100-200, default: 120)
    
    Returns:
        Darkened hex color string
    """
    try:
        color = QtGui.QColor(hex_color)
        return color.darker(factor).name()
    except Exception:
        return hex_color