"""
Ultra-Modern Premium Theme for Dofus Window Manager
Glassmorphism design with smooth animations and gradients.
No external dependencies - pure PyQt6 styling.
"""

def apply_ultra_modern_theme(widget):
    """Apply cutting-edge dark theme with glassmorphism effects"""
    widget.setStyleSheet("""
        /* === MAIN WINDOW === */
        QMainWindow {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #0a0a0f, stop:1 #0f0f15
            );
        }

        /* === DEFAULT WIDGETS === */
        QWidget {
            background-color: transparent;
            color: #ffffff;
            font-family: 'Segoe UI', 'Ubuntu', 'DejaVu Sans', sans-serif;
        }

        /* === TEXT INPUT FIELDS === */
        QLineEdit, QTextEdit {
            background-color: rgba(20, 20, 30, 0.6);
            color: #ffffff;
            border: 1px solid rgba(20, 184, 166, 0.2);
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 12px;
            selection-background-color: #0d7377;
        }

        QLineEdit:focus, QTextEdit:focus {
            border: 2px solid #14b8a6;
            background-color: rgba(20, 20, 30, 0.8);
        }

        /* === COMBOBOX === */
        QComboBox {
            background-color: rgba(20, 20, 30, 0.6);
            color: #ffffff;
            border: 1px solid rgba(20, 184, 166, 0.2);
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 12px;
        }

        QComboBox:hover {
            border: 1px solid rgba(20, 184, 166, 0.4);
        }

        QComboBox:focus {
            border: 2px solid #14b8a6;
            background-color: rgba(20, 20, 30, 0.8);
        }

        QComboBox::drop-down {
            border: none;
            width: 20px;
        }

        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 7px solid rgba(255, 255, 255, 0.5);
            width: 0;
            height: 0;
        }

        QComboBox QAbstractItemView {
            background-color: rgba(20, 20, 30, 0.95);
            color: #ffffff;
            selection-background-color: rgba(13, 115, 119, 0.6);
            border: 1px solid rgba(20, 184, 166, 0.2);
            border-radius: 6px;
            padding: 4px;
        }

        QComboBox QAbstractItemView::item {
            padding: 6px;
            border-radius: 4px;
        }

        QComboBox QAbstractItemView::item:selected {
            background-color: #0d7377;
        }

        /* === RADIO BUTTON === */
        QRadioButton {
            color: #ffffff;
            spacing: 8px;
            font-size: 12px;
        }

        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 2px solid rgba(20, 184, 166, 0.3);
            background-color: rgba(20, 20, 30, 0.6);
        }

        QRadioButton::indicator:hover {
            border: 2px solid #14b8a6;
        }

        QRadioButton::indicator:checked {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #0d7377, stop:1 #14b8a6
            );
            border: 2px solid #14b8a6;
        }

        /* === CHECKBOX === */
        QCheckBox {
            color: #ffffff;
            spacing: 8px;
            font-size: 12px;
        }

        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid rgba(20, 184, 166, 0.3);
            background-color: rgba(20, 20, 30, 0.6);
        }

        QCheckBox::indicator:hover {
            border: 2px solid #14b8a6;
        }

        QCheckBox::indicator:checked {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #0d7377, stop:1 #14b8a6
            );
            border: 2px solid #14b8a6;
        }

        /* === SCROLLBAR === */
        QScrollBar:vertical {
            background-color: rgba(30, 30, 40, 0.2);
            width: 10px;
            border-radius: 5px;
        }

        QScrollBar::handle:vertical {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #0d7377, stop:1 #14b8a6
            );
            border-radius: 5px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #14b8a6, stop:1 #1dd1bb
            );
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar:horizontal {
            background-color: rgba(30, 30, 40, 0.2);
            height: 10px;
            border-radius: 5px;
        }

        QScrollBar::handle:horizontal {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #0d7377, stop:1 #14b8a6
            );
            border-radius: 5px;
            min-width: 20px;
        }

        QScrollBar::handle:horizontal:hover {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #14b8a6, stop:1 #1dd1bb
            );
        }

        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {
            width: 0px;
        }

        /* === TOOLTIP === */
        QToolTip {
            background-color: rgba(20, 20, 30, 0.95);
            color: #ffffff;
            border: 1px solid rgba(20, 184, 166, 0.3);
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 11px;
            font-weight: 500;
        }

        /* === MENU === */
        QMenu {
            background-color: rgba(20, 20, 30, 0.95);
            color: #ffffff;
            border: 1px solid rgba(20, 184, 166, 0.2);
            border-radius: 8px;
            padding: 6px;
        }

        QMenu::item {
            padding: 8px 16px;
            border-radius: 4px;
            margin: 2px;
        }

        QMenu::item:selected {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(13, 115, 119, 0.4), stop:1 rgba(20, 184, 166, 0.4)
            );
        }

        QMenu::separator {
            background-color: rgba(20, 184, 166, 0.1);
            height: 1px;
            margin: 4px 0px;
        }

        /* === PUSH BUTTON (DEFAULT) === */
        QPushButton {
            background-color: rgba(30, 30, 40, 0.5);
            color: #ffffff;
            border: 1px solid rgba(20, 184, 166, 0.1);
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 600;
            font-size: 12px;
        }

        QPushButton:hover {
            background-color: rgba(40, 40, 50, 0.7);
            border: 1px solid rgba(20, 184, 166, 0.3);
        }

        QPushButton:pressed {
            background-color: rgba(20, 20, 30, 0.7);
            border: 1px solid rgba(20, 184, 166, 0.2);
        }

        QPushButton:disabled {
            color: #666;
            background-color: rgba(20, 20, 30, 0.3);
            border: 1px solid rgba(20, 184, 166, 0.05);
        }

        /* === DIALOG === */
        QDialog {
            background-color: #0a0a0f;
        }

        /* === MESSAGEBOX === */
        QMessageBox QLabel {
            color: #ffffff;
        }

        /* === SCROLL AREA === */
        QScrollArea {
            background-color: transparent;
            border: none;
        }

        /* === LIST WIDGET === */
        QListWidget {
            background-color: rgba(10, 10, 10, 0.5);
            border: 1px solid rgba(20, 184, 166, 0.1);
            border-radius: 12px;
            outline: none;
        }

        QListWidget::item {
            background-color: rgba(20, 30, 30, 0.6);
            border-left: 3px solid #14b8a6;
            border-radius: 8px;
            padding: 8px;
            margin: 3px 0;
        }

        QListWidget::item:selected {
            background-color: rgba(13, 115, 119, 0.6);
            border-left: 3px solid #1dd1bb;
        }

        QListWidget::item:hover {
            background-color: rgba(20, 30, 30, 0.8);
        }
    """)