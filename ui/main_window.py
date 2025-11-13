#!/usr/bin/env python3
"""
DOFUS WINDOW MANAGER - Clean & Modern Edition
Simple, elegant, and easy to use interface.
"""

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QTimer

from core.config import (
    APP_NAME, CONFIG_FILE, PROFILES_FILE, DEFAULT_CLASS_INI,
    RENAME_SCRIPT, REORGANIZE_SCRIPT, CLICK_CYCLE_FORWARD, CYCLE_FORWARD, CYCLE_BACKWARD, 
    TOGGLE_WORKSPACE, SPACE_CYCLE_FORWARD, SCRIPT_DIR
)
from core.config import load_json, save_json
from core.scripts import (
    generate_rename_script, generate_reorganize_script, generate_cycle_forward, 
    generate_cycle_backward, generate_toggle_workspace, generate_space_cycle_forward,
    generate_click_cycle
)
from core.workspace import get_workspaces
from core.utils import run_cmd
from ui.widgets import CompactDraggableList


class ModernDofusManager(QtWidgets.QMainWindow):
    """Clean and modern Dofus Window Manager"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎮 Gestionnaire Dofus")
        self.setFixedSize(480, 900)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )

        # Load config
        cfg = load_json(CONFIG_FILE, {})
        self.class_ini = cfg.get('class_ini', DEFAULT_CLASS_INI.copy())
        self.profiles = load_json(PROFILES_FILE, {})

        self._setup_ui()
        self._apply_theme()
        self._create_tray()
        self._refresh_all()

    def _setup_ui(self):
        """Build clean interface"""
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # Header with title and quick actions
        header_layout = QtWidgets.QVBoxLayout()
        header_layout.setSpacing(12)

        # Title
        title = QtWidgets.QLabel("🎮 Dofus Manager")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #14b8a6;")
        header_layout.addWidget(title)

        # Quick action buttons
        quick_layout = QtWidgets.QHBoxLayout()
        quick_layout.setSpacing(8)

        btn_rename = QtWidgets.QPushButton("✏️  Renommer Fenêtres")
        btn_rename.setFixedHeight(40)
        btn_rename.clicked.connect(self._show_rename_dialog)
        btn_rename.setStyleSheet(self._get_btn_style("#0d7377"))
        quick_layout.addWidget(btn_rename)

        btn_reorder = QtWidgets.QPushButton("🔄 Réorganiser Fenêtres")
        btn_reorder.setFixedHeight(40)
        btn_reorder.clicked.connect(self._quick_reorganize)
        btn_reorder.setStyleSheet(self._get_btn_style("#8b5cf6"))
        quick_layout.addWidget(btn_reorder)

        btn_menu = QtWidgets.QPushButton("⚙️")
        btn_menu.setFixedSize(40, 40)
        btn_menu.clicked.connect(self._show_menu)
        btn_menu.setStyleSheet(self._get_icon_btn_style("#333"))
        quick_layout.addWidget(btn_menu)

        header_layout.addLayout(quick_layout)
        main_layout.addLayout(header_layout)

        # Scroll area for content
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")

        content = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        # Initiative Order
        content_layout.addWidget(self._create_initiative_section())

        # Profiles
        content_layout.addWidget(self._create_profiles_section())

        # Scripts
        content_layout.addWidget(self._create_scripts_section())

        content_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Status bar
        self.status_label = QtWidgets.QLabel("Prêt")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #14b8a6; font-size: 11px; padding: 6px;")
        main_layout.addWidget(self.status_label)

    def _create_initiative_section(self):
        """Initiative order section"""
        group = QtWidgets.QGroupBox("📋 Ordre d'Initiative")
        group.setStyleSheet(self._get_group_style())
        
        layout = QtWidgets.QVBoxLayout(group)
        layout.setSpacing(8)

        # List
        self.list_widget = CompactDraggableList()
        self.list_widget.orderChanged.connect(self._sync_from_list)
        self.list_widget.setMinimumHeight(240)
        layout.addWidget(self.list_widget)

        # Toolbar
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(6)

        buttons = [
            ("➕", "#22c55e", self._add_class),
            ("✏️", "#3b82f6", self._rename_class),
            ("🗑️", "#ef4444", self._remove_class),
        ]

        for icon, color, callback in buttons:
            btn = QtWidgets.QPushButton(icon)
            btn.setFixedSize(36, 36)
            btn.clicked.connect(callback)
            btn.setStyleSheet(self._get_icon_btn_style(color))
            toolbar.addWidget(btn)

        toolbar.addStretch()

        btn_reset = QtWidgets.QPushButton("🔄")
        btn_reset.setFixedSize(36, 36)
        btn_reset.clicked.connect(self._reset_to_default)
        btn_reset.setStyleSheet(self._get_icon_btn_style("#f59e0b"))
        toolbar.addWidget(btn_reset)

        layout.addLayout(toolbar)
        return group

    def _create_profiles_section(self):
        """Profiles management section"""
        group = QtWidgets.QGroupBox("💾 Profils")
        group.setStyleSheet(self._get_group_style())
        
        layout = QtWidgets.QVBoxLayout(group)
        layout.setSpacing(8)

        # Selector
        selector_layout = QtWidgets.QHBoxLayout()
        selector_layout.setSpacing(6)

        self.combo_profiles = QtWidgets.QComboBox()
        self.combo_profiles.setFixedHeight(32)
        self.combo_profiles.currentTextChanged.connect(self._on_profile_selected)
        selector_layout.addWidget(self.combo_profiles)

        # Buttons
        btn_save = QtWidgets.QPushButton("💾")
        btn_save.setFixedSize(32, 32)
        btn_save.clicked.connect(self._save_profile)
        btn_save.setStyleSheet(self._get_icon_btn_style("#555"))
        selector_layout.addWidget(btn_save)

        btn_delete = QtWidgets.QPushButton("🗑️")
        btn_delete.setFixedSize(32, 32)
        btn_delete.clicked.connect(self._delete_profile)
        btn_delete.setStyleSheet(self._get_icon_btn_style("#ef4444"))
        selector_layout.addWidget(btn_delete)

        layout.addLayout(selector_layout)
        return group

    def _create_scripts_section(self):
        """Scripts generation section"""
        group = QtWidgets.QGroupBox("⚡ Générer Scripts")
        group.setStyleSheet(self._get_group_style())
        
        layout = QtWidgets.QVBoxLayout(group)
        layout.setSpacing(8)

        # Grid of scripts
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(8)

        scripts = [
            ("🔄 Cycle", "#14b8a6", self._generate_cycle_only),
            ("✏️ Renommer", "#8b5cf6", self._generate_rename_only),
            ("🖱️ Clic+Cycle", "#84AB58", self._generate_click_cycle_only),
            ("🗃️ Workspace", "#f59e0b", self._generate_workspace_only),
            ("⌨️ Espace+Cycle", "#f97316", self._generate_space_cycle_only),
            ("🔧 Générer Tous", "#0d7377", self._generate_all_scripts),
        ]

        for i, (label, color, callback) in enumerate(scripts):
            row = i // 2
            col = i % 2
            btn = QtWidgets.QPushButton(label)
            btn.setMinimumHeight(40)
            btn.clicked.connect(callback)
            btn.setStyleSheet(self._get_btn_style(color))
            grid.addWidget(btn, row, col)

        layout.addLayout(grid)
        return group

    def _get_btn_style(self, color):
        """Button style"""
        lighter = self._lighten(color, 120)
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color}, stop:1 {lighter});
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {lighter}, stop:1 {self._lighten(color, 130)});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self._darken(color, 120)}, stop:1 {color});
            }}
        """

    def _get_icon_btn_style(self, color):
        """Icon button style"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._lighten(color, 120)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken(color, 120)};
            }}
        """

    def _get_group_style(self):
        """Group box style"""
        return """
            QGroupBox {
                background-color: transparent;
                border: 1px solid #333;
                border-radius: 8px;
                color: #ffffff;
                font-weight: 600;
                font-size: 12px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                color: #14b8a6;
            }
        """

    def _apply_theme(self):
        """Apply clean dark theme"""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0f0f0f;
                color: #ffffff;
                font-family: 'Segoe UI', 'Ubuntu', sans-serif;
            }
            
            QComboBox {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 6px;
                font-size: 11px;
            }
            QComboBox:focus {
                border: 2px solid #14b8a6;
            }
            QComboBox::drop-down {
                border: none;
                width: 18px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a1a;
                color: #ffffff;
                selection-background-color: #0d7377;
                border: 1px solid #333;
            }

            QRadioButton {
                color: #ffffff;
                spacing: 6px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #555;
                background-color: #1a1a1a;
            }
            QRadioButton::indicator:checked {
                background-color: #14b8a6;
                border: 2px solid #0d7377;
            }

            QScrollBar:vertical {
                background-color: #1a1a1a;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0d7377, stop:1 #14b8a6);
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #14b8a6, stop:1 #1dd1bb);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QListWidget {
                background-color: #1a1a1a;
                border: 1px solid #333;
                border-radius: 6px;
            }
            QListWidget::item {
                padding: 8px;
                background-color: #242424;
                border-left: 3px solid #333;
            }
            QListWidget::item:selected {
                background-color: #0d7377;
                border-left: 3px solid #14b8a6;
            }

            QMessageBox QLabel {
                color: #ffffff;
            }
        """)

    def _show_menu(self):
        """Show menu"""
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 1px solid #333;
                padding: 4px;
            }
            QMenu::item:selected {
                background-color: #0d7377;
            }
        """)

        menu.addAction("📁 Ouvrir Dossier Scripts").triggered.connect(self._open_script_folder)
        menu.addSeparator()
        menu.addAction("ℹ️ À Propos").triggered.connect(self._show_about)

        menu.exec(QtGui.QCursor.pos())

    def _change_language(self, lang):
        """Change language on the fly"""
        self.i18n.set_language(lang)
        self._update_ui_text()

    def _update_ui_text(self):
        """Update all UI text with current language"""
        # Update title and labels
        # This is a simple approach - just show message and let user see changes
        self._show_status(f"✅ Language changed")

    def _show_about(self):
        """Show about dialog with your original content"""
        about_text = f"""⚙️ Gestionnaire Dofus

Gérez et organisez efficacement vos fenêtres Dofus.

📌 Boutons :
• Renommer    — Renommer les fenêtres Dofus ouvertes selon l'ordre d'initiative.
• Réorganiser — Réorganiser visuellement les fenêtres par ordre d'initiative.

🧩 Aperçu des scripts :
• cycle_forward.sh     — Cycle avant à travers les fenêtres.
• cycle_backward.sh    — Cycle arrière à travers les fenêtres.
• rename_windows.sh    — Renommer toutes les fenêtres ouvertes.
• reorganize_windows.sh— Aligner les fenêtres de gauche à droite.
• click_cycle_forward.sh— Clic + cycle avant.
• toggle_workspace.sh  — Basculer entre les espaces de travail.

📁 Emplacement des scripts :
{SCRIPT_DIR}

🎮 Raccourcis clavier suggérés :
• Super + Right        → cycle_forward.sh
• Super + Left         → cycle_backward.sh
• Super + Space        → space_cycle_forward.sh
• Super + Up           → rename_windows.sh
• Super + Down         → reorganize_windows.sh
• Super + Shift+Space  → toggle_workspace.sh

© 2025 Gestionnaire Dofus"""
        QtWidgets.QMessageBox.information(self, "À Propos", about_text)

    def _create_tray(self):
        """Create system tray"""
        self.tray = QtWidgets.QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ComputerIcon))

        menu = QtWidgets.QMenu()
        menu.addAction("Show").triggered.connect(self.showNormal)
        menu.addSeparator()
        menu.addAction("Rename").triggered.connect(self._quick_rename)
        menu.addAction("Reorder").triggered.connect(self._quick_reorganize)
        menu.addSeparator()
        menu.addAction("Quit").triggered.connect(QtWidgets.QApplication.quit)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_click)
        self.tray.show()

    def _on_tray_click(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            self.showNormal() if self.isHidden() else self.hide()

    def closeEvent(self, event):
        event.accept()

    # === DATA MANAGEMENT ===
    def _refresh_all(self):
        self._refresh_list()
        self._refresh_profiles()

    def _refresh_list(self):
        self.list_widget.clear()
        for i, name in enumerate(self.class_ini, 1):
            item = QtWidgets.QListWidgetItem(f"{i}. {name}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.list_widget.addItem(item)

    def _refresh_profiles(self):
        current = self.combo_profiles.currentText()
        self.combo_profiles.clear()
        self.combo_profiles.addItems(sorted(self.profiles.keys()))
        if current in self.profiles:
            self.combo_profiles.setCurrentText(current)

    def _sync_from_list(self):
        self.class_ini = [
            self.list_widget.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.list_widget.count())
        ]
        self._refresh_list()
        self._save_config()
        self._show_status("✅ Order updated")

    def _save_config(self):
        save_json(CONFIG_FILE, {'class_ini': self.class_ini})

    def _show_status(self, message, duration=2000):
        self.status_label.setText(message)
        QTimer.singleShot(duration, lambda: self.status_label.setText("Prêt"))

    def _lighten(self, hex_color, factor=120):
        try:
            return QtGui.QColor(hex_color).lighter(factor).name()
        except:
            return hex_color

    def _darken(self, hex_color, factor=120):
        try:
            return QtGui.QColor(hex_color).darker(factor).name()
        except:
            return hex_color

    # === CLASS MANAGEMENT ===
    def _add_class(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Add Class", "Class name:")
        if ok and text.strip():
            self.class_ini.append(text.strip())
            self._refresh_list()
            self._save_config()
            self._show_status(f"✅ Added: {text.strip()}")

    def _rename_class(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            self._show_status("⚠️ Select a class")
            return
        old = self.class_ini[idx]
        text, ok = QtWidgets.QInputDialog.getText(self, "Rename", "New name:", text=old)
        if ok and text.strip():
            self.class_ini[idx] = text.strip()
            self._refresh_list()
            self._save_config()
            self._show_status(f"✅ Renamed: {text.strip()}")

    def _remove_class(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            self._show_status("⚠️ Select a class")
            return
        name = self.class_ini[idx]
        del self.class_ini[idx]
        self._refresh_list()
        self._save_config()
        self._show_status(f"✅ Deleted: {name}")

    def _reset_to_default(self):
        reply = QtWidgets.QMessageBox.question(
            self, "Reset", "Reset to default?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.class_ini = DEFAULT_CLASS_INI.copy()
            self._refresh_list()
            self._save_config()
            self._show_status("✅ Reset to default")

    # === PROFILES ===
    def _save_profile(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Save Profile", "Profile name:")
        if ok and text.strip():
            self.profiles[text.strip()] = list(self.class_ini)
            save_json(PROFILES_FILE, self.profiles)
            self._refresh_profiles()
            self._show_status(f"✅ Profile saved: {text.strip()}")

    def _on_profile_selected(self, name):
        """Auto-load profile when selected"""
        if not name or name not in self.profiles:
            return
        self.class_ini = list(self.profiles[name])
        self._refresh_list()
        self._save_config()
        self._show_status(f"✅ Loaded: {name}")

    def _delete_profile(self):
        name = self.combo_profiles.currentText()
        if not name:
            return
        reply = QtWidgets.QMessageBox.question(
            self, "Delete", f"Delete '{name}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            del self.profiles[name]
            save_json(PROFILES_FILE, self.profiles)
            self._refresh_profiles()
            self._show_status(f"✅ Deleted: {name}")

    # === SCRIPTS ===
    def _generate_cycle_only(self):
        generate_cycle_forward(self.class_ini)
        generate_cycle_backward(self.class_ini)
        self._show_status("✅ Cycle scripts generated")

    def _generate_click_cycle_only(self):
        generate_click_cycle()
        self._show_status("✅ Click+Cycle generated")

    def _generate_workspace_only(self):
        generate_toggle_workspace()
        self._show_status("✅ Workspace script generated")

    def _generate_rename_only(self):
        generate_rename_script(self.class_ini)
        self._show_status("✅ Rename script generated")

    def _generate_space_cycle_only(self):
        generate_space_cycle_forward()
        self._show_status("✅ Space+Cycle generated")

    def _generate_all_scripts(self):
        generate_rename_script(self.class_ini)
        generate_reorganize_script(self.class_ini)
        generate_cycle_forward(self.class_ini)
        generate_cycle_backward(self.class_ini)
        generate_toggle_workspace()
        generate_space_cycle_forward()
        generate_click_cycle()
        self._show_status("✅ All scripts generated")

    def _open_script_folder(self):
        try:
            run_cmd(['xdg-open', str(SCRIPT_DIR)])
            self._show_status("✅ Folder opened")
        except:
            self._show_status("❌ Cannot open folder")

    def _quick_rename(self):
        generate_rename_script(self.class_ini)
        result = run_cmd([str(RENAME_SCRIPT)])
        if result[2] == 0:
            self.tray.showMessage("Dofus Manager", "Windows renamed!", 1)

    def _quick_reorganize(self):
        generate_reorganize_script(self.class_ini)
        result = run_cmd([str(REORGANIZE_SCRIPT)], timeout=10)
        if result[2] == 0:
            self._show_status("✅ Windows reordered")

    def _show_rename_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Renommer Fenêtres")
        dialog.setFixedWidth(340)
        dialog.setStyleSheet("background-color: #0f0f0f; color: white;")

        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(12)

        label = QtWidgets.QLabel("Sélectionner l'espace de travail:")
        label.setStyleSheet("color: #14b8a6; font-weight: 600;")
        layout.addWidget(label)

        self.radio_all = QtWidgets.QRadioButton("Tous les espaces de travail")
        self.radio_all.setChecked(True)
        layout.addWidget(self.radio_all)

        self.radio_specific = QtWidgets.QRadioButton("Espace de travail spécifique:")
        layout.addWidget(self.radio_specific)

        self.combo_workspace = QtWidgets.QComboBox()
        self.combo_workspace.setEnabled(False)
        self.combo_workspace.setFixedHeight(32)
        for ws_num, ws_name in get_workspaces():
            self.combo_workspace.addItem(f"{ws_num}: {ws_name}", ws_num)
        layout.addWidget(self.combo_workspace)

        self.radio_specific.toggled.connect(lambda checked: self.combo_workspace.setEnabled(checked))

        layout.addSpacing(12)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_execute = QtWidgets.QPushButton("Exécuter")
        btn_execute.setFixedHeight(36)
        btn_execute.clicked.connect(lambda: self._execute_rename(dialog))
        btn_execute.setStyleSheet(self._get_btn_style("#0d7377"))
        btn_cancel = QtWidgets.QPushButton("Annuler")
        btn_cancel.setFixedHeight(36)
        btn_cancel.clicked.connect(dialog.reject)
        btn_cancel.setStyleSheet(self._get_btn_style("#555"))
        btn_layout.addWidget(btn_execute)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        dialog.exec()

    def _execute_rename(self, dialog):
        workspace = None
        if self.radio_specific.isChecked():
            workspace = self.combo_workspace.currentData()
        
        generate_rename_script(self.class_ini, workspace)
        result = run_cmd([str(RENAME_SCRIPT)])
        if result[2] == 0:
            self._show_status("✅ Windows renamed")
            dialog.accept()
        else:
            self._show_status("❌ Rename failed")