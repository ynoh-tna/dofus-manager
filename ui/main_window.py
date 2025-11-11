from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt

from core.config import (
    APP_NAME, CONFIG_FILE, PROFILES_FILE, DEFAULT_CLASS_INI,
    RENAME_SCRIPT, REORGANIZE_SCRIPT, CLICK_CYCLE_FORWARD, CYCLE_FORWARD, CYCLE_BACKWARD, 
    TOGGLE_WORKSPACE, SCRIPT_DIR
)
from core.config import load_json, save_json
from core.scripts import (
    generate_rename_script, generate_reorganize_script, generate_cycle_forward, 
    generate_cycle_backward, generate_toggle_workspace, generate_click_cycle
)
from core.workspace import get_workspaces
from core.utils import make_executable, run_cmd
from ui.widgets import CompactDraggableList
from ui.theme import apply_compact_theme, get_icon_button_style, get_action_button_style

class DofusManager(QtWidgets.QMainWindow):
    """Main compact window manager for Dofus multi-instance control"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        
        # Compact window size 
        self.setFixedSize(320, 750)
        
        # Window flags for compact mode (always on top option)
        self.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )

        # Load configuration
        cfg = load_json(CONFIG_FILE, {})
        self.class_ini = cfg.get('class_ini', DEFAULT_CLASS_INI.copy())
        self.profiles = load_json(PROFILES_FILE, {})

        # Setup UI and apply theme
        self._setup_ui()
        apply_compact_theme(self)
        self._create_tray()
        self._refresh_all()

    def _setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # HEADER : Rename / Settings
        main_layout.addLayout(self._create_header())

        # PROFILES
        self.profile_section = self._create_profile_section()
        main_layout.addWidget(self.profile_section)

        # LISTE
        main_layout.addLayout(self._create_list_section(), stretch=1)

        # EDIT TOOLBAR
        main_layout.addLayout(self._create_edit_toolbar())

        # QUICK SCRIPTS
        main_layout.addLayout(self._create_actions_section())

        main_layout.addStretch()

        # STATUS LABEL
        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color:#888;font-size:9px;padding:2px;")
        main_layout.addWidget(self.status_label)

    def _create_header(self):
        """Create compact header with main action button"""
        header = QtWidgets.QHBoxLayout()
        header.setSpacing(6)

        # Title with icon
        title = QtWidgets.QLabel("🎮 Dofus WM")
        title.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #0d7377;
        """)
        title.setToolTip("Dofus Window Manager")
        header.addWidget(title)
        
        header.addStretch()

        # Main rename button
        btn_rename = QtWidgets.QPushButton("🔧 Rename")
        btn_rename.setStyleSheet(get_action_button_style("#0d7377"))
        btn_rename.setFixedSize(80, 28)
        btn_rename.setToolTip("Rename all Dofus windows\naccording to initiative order")
        btn_rename.clicked.connect(self._show_rename_dialog)
        header.addWidget(btn_rename)

        # Reorganize button
        btn_reorganize = QtWidgets.QPushButton("🔄 ReOrder")
        btn_reorganize.setStyleSheet(get_action_button_style("#8b5cf6"))
        btn_reorganize.setFixedSize(80, 28)
        btn_reorganize.setToolTip("Reorganize windows left to right\naccording to initiative order")
        btn_reorganize.clicked.connect(self._quick_reorganize)
        header.addWidget(btn_reorganize)

        # Settings button (gear icon)
        btn_settings = QtWidgets.QPushButton("⚙️")
        btn_settings.setStyleSheet(get_icon_button_style("#6366f1", size=28))
        btn_settings.setFixedSize(28, 28)
        btn_settings.setToolTip("Generate all scripts\nand open folder")
        btn_settings.clicked.connect(self._show_settings_menu)
        header.addWidget(btn_settings)

        return header

    def _create_list_section(self):
        section = QtWidgets.QVBoxLayout()
        section.setSpacing(4)

        label = QtWidgets.QLabel("📋 Initiative Order")
        label.setStyleSheet("font-size:11px;font-weight:bold;color:#ffffff;")
        section.addWidget(label)

        # Liste draggable
        self.list_widget = CompactDraggableList()
        self.list_widget.orderChanged.connect(self._sync_from_list)

        # Scroll area
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.list_widget)
        scroll.setStyleSheet("border:none;")
        section.addWidget(scroll, stretch=1)

        return section

    def _create_edit_toolbar(self):
        """Create compact edit toolbar with icon buttons"""
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(6)

        # Add button
        btn_add = QtWidgets.QPushButton("➕")
        btn_add.setStyleSheet(get_icon_button_style("#22c55e"))
        btn_add.setFixedSize(32, 32)
        btn_add.setToolTip("Add new class to order")
        btn_add.clicked.connect(self._add_class)
        toolbar.addWidget(btn_add)

        # Edit button
        btn_edit = QtWidgets.QPushButton("✏️")
        btn_edit.setStyleSheet(get_icon_button_style("#3b82f6"))
        btn_edit.setFixedSize(32, 32)
        btn_edit.setToolTip("Rename selected class")
        btn_edit.clicked.connect(self._rename_class)
        toolbar.addWidget(btn_edit)

        # Delete button
        btn_del = QtWidgets.QPushButton("🗑️")
        btn_del.setStyleSheet(get_icon_button_style("#ef4444"))
        btn_del.setFixedSize(32, 32)
        btn_del.setToolTip("Delete selected class")
        btn_del.clicked.connect(self._remove_class)
        toolbar.addWidget(btn_del)

        toolbar.addStretch()

        # Reset button
        btn_reset = QtWidgets.QPushButton("🔄")
        btn_reset.setStyleSheet(get_icon_button_style("#f59e0b"))
        btn_reset.setFixedSize(32, 32)
        btn_reset.setToolTip("Reset to default classes\n(Feca, Cra, Enu, Panda, Sadi)")
        btn_reset.clicked.connect(self._reset_to_default)
        toolbar.addWidget(btn_reset)

        return toolbar

    def _create_profile_section(self):
        """Create responsive profile section"""
        group = QtWidgets.QGroupBox("💾 Profiles")
        group.setCheckable(False)
        group.setChecked(False)
        group.setStyleSheet("""
            QGroupBox {
                font-size:10px;color:#aaa;border:1px solid #333;border-radius:4px;margin-top:6px;padding-top:6px;
            }
            QGroupBox::title { left:8px;padding:0 4px; }
        """)

        layout = QtWidgets.QVBoxLayout(group)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        self.combo_profiles = QtWidgets.QComboBox()
        self.combo_profiles.setFixedHeight(26)
        self.combo_profiles.setToolTip("Select a saved profile")
        layout.addWidget(self.combo_profiles)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(4)

        self.profile_buttons = []
        for icon, tooltip, callback in [("💾","Save profile",self._save_profile),
                                        ("📤","Load profile",self._load_profile),
                                        ("🗑️","Delete profile",self._delete_profile)]:
            btn = QtWidgets.QPushButton(icon)
            btn.setFixedSize(30, 26)
            btn.setToolTip(tooltip)
            btn.clicked.connect(callback)
            btn.setStyleSheet(get_icon_button_style("#555", size=26))
            btn_layout.addWidget(btn)
            self.profile_buttons.append(btn)

        layout.addLayout(btn_layout)
        return group

    def _create_actions_section(self):
        """Create quick action buttons section"""
        section = QtWidgets.QVBoxLayout()
        section.setSpacing(4)

        label = QtWidgets.QLabel("⚡ Create or Update Scripts")
        label.setStyleSheet("""
            font-size: 11px; 
            font-weight: bold; 
            color: #ffffff;
        """)
        section.addWidget(label)

        # Grid of action buttons
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(4)
        grid.setContentsMargins(0, 0, 0, 0)

        # Button definitions: (text, tooltip, color, callback, row, col)
        buttons = [
            ("🔄 Cycle <->", "Generate cycle forward/backward scripts", "#14b8a6", 
             self._generate_cycle_only, 0, 0),
            ("✏️ Rename windows", "Rename windows script", "#8b5cf6", 
             self._generate_rename_only, 0, 1),
            ("🖱️ Click and Cycle", "Generate click & cycle script", "#84AB58", 
             self._generate_click_cycle_only, 1, 0),
            ("🗃️ Workspaces", "Generate workspace toggle script", "#f59e0b", 
             self._generate_workspace_only, 1, 1),
        ]

        for text, tooltip, color, callback, row, col in buttons:
            btn = QtWidgets.QPushButton(text)
            btn.setStyleSheet(get_action_button_style(color))
            btn.setFixedHeight(32)
            btn.setToolTip(tooltip)
            btn.clicked.connect(callback)
            grid.addWidget(btn, row, col)

        section.addLayout(grid)
        return section

    def _show_settings_menu(self):
        """Show settings menu popup"""
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #444444;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
            }
            QMenu::item:selected {
                background-color: #0d7377;
            }
        """)

        # Add actions
        act_gen_all = menu.addAction("🔧 Generate All Scripts")
        act_gen_all.triggered.connect(self._generate_all_scripts)

        menu.addSeparator()

        act_open = menu.addAction("📁 Open Scripts Folder")
        act_open.triggered.connect(self._open_script_folder)

        act_about = menu.addAction("ℹ️ About")
        act_about.triggered.connect(self._show_about)

        # Show menu at button position
        sender = self.sender()
        menu.exec(sender.mapToGlobal(sender.rect().bottomLeft()))

    def _show_about(self):
        """Show about dialog"""
        QtWidgets.QMessageBox.information(
            self,
            "About",
            "⚙️ Dofus Manager\n\n"
            "Manage and organize your Dofus windows efficiently.\n\n"
            "📌 Buttons:\n"
            "• Rename  — Rename opened Dofus windows based on initiative order.\n"
            "• Reorder — Reorganize windows visually by initiative order.\n\n"
            "🧩 Scripts overview:\n"
            "• cycle_forward.sh     — Cycle forward through windows.\n"
            "• cycle_backward.sh    — Cycle backward through windows.\n"
            "• rename_windows.sh    — Rename all opened windows.\n"
            "• reorganize_windows.sh— Align windows left to right.\n"
            "• click_cycle_forward.sh— Click + cycle forward.\n"
            "• toggle_workspace.sh  — Switch between workspaces.\n\n"
            "📁 Script location:\n"
            f"{SCRIPT_DIR}\n\n"
            "🎮 Suggested key bindings:\n"
            f"{CYCLE_FORWARD}\n"
            f"{CYCLE_BACKWARD}\n"
            f"{CLICK_CYCLE_FORWARD}\n"
            f"{TOGGLE_WORKSPACE}\n"
            "© 2025 Dofus Manager"
        )


    # === SYSTEM TRAY ===
    def _create_tray(self):
        """Create system tray icon and menu"""
        self.tray = QtWidgets.QSystemTrayIcon(self)
        self.tray.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ComputerIcon)
        )
        
        # Tray menu
        menu = QtWidgets.QMenu()
        
        show_action = menu.addAction("🎮 Show Manager")
        show_action.triggered.connect(self.showNormal)
        
        menu.addSeparator()
        
        rename_action = menu.addAction("🔄 Rename Windows")
        rename_action.triggered.connect(self._quick_rename)
        
        reorganize_action = menu.addAction("🔧 Order Windows")
        reorganize_action.triggered.connect(self._quick_reorganize)
        
        cycle_action = menu.addAction("🔁 Generate Cycle Scripts")
        cycle_action.triggered.connect(self._generate_cycle_only)
        
        menu.addSeparator()
        
        quit_action = menu.addAction("❌ Quit")
        quit_action.triggered.connect(QtWidgets.QApplication.quit)
        
        self.tray.setContextMenu(menu)
        self.tray.setToolTip(APP_NAME)
        self.tray.activated.connect(self._on_tray_click)
        self.tray.show()

    def _on_tray_click(self, reason):
        """Handle tray icon click"""
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            if self.isHidden() or self.isMinimized():
                self.showNormal()
                self.activateWindow()
            else:
                self.hide()

    def closeEvent(self, event):
        """Ask user what to do on close"""       
        menu = QtWidgets.QMessageBox(self)
        menu.setWindowTitle("Exit Options")
        menu.setText("What do you want to do?")
        btn_tray = menu.addButton("Minimize to tray", QtWidgets.QMessageBox.ButtonRole.AcceptRole)
        btn_quit = menu.addButton("Quit", QtWidgets.QMessageBox.ButtonRole.DestructRole)
        menu.exec()

        if menu.clickedButton() == btn_quit:
            event.accept()
        else:
            self.hide()
            self.tray.showMessage(APP_NAME, "Running in system tray", QtWidgets.QSystemTrayIcon.MessageIcon.Information, 2000)
            event.ignore()

    # === DATA MANAGEMENT ===
    def _refresh_all(self):
        """Refresh all UI elements"""
        self._refresh_list()
        self._refresh_profiles()

    def _refresh_list(self):
        """Refresh the initiative order list"""
        self.list_widget.clear()
        for i, name in enumerate(self.class_ini, 1):
            item = QtWidgets.QListWidgetItem(f"{i}. {name}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.list_widget.addItem(item)

    def _refresh_profiles(self):
        """Refresh profiles dropdown"""
        current = self.combo_profiles.currentText()
        self.combo_profiles.clear()
        self.combo_profiles.addItems(sorted(self.profiles.keys()))
        if current in self.profiles:
            self.combo_profiles.setCurrentText(current)

    def _sync_from_list(self):
        """Sync class order from list widget"""
        self.class_ini = [
            self.list_widget.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.list_widget.count())
        ]
        self._refresh_list()
        self._save_config()
        self._show_status("✅ Order updated", 2000)

    def _save_config(self):
        """Save configuration to file"""
        cfg = {'class_ini': self.class_ini}
        save_json(CONFIG_FILE, cfg)

    def _show_status(self, message, duration=3000):
        """Show status message"""
        self.status_label.setText(message)
        QtCore.QTimer.singleShot(duration, lambda: self.status_label.setText("Ready"))

    # === CLASS MANAGEMENT ===
    def _add_class(self):
        """Add new class to order"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Add Class", "Class name:", 
            QtWidgets.QLineEdit.EchoMode.Normal
        )
        if ok and text.strip():
            self.class_ini.append(text.strip())
            self._refresh_list()
            self._save_config()
            self._show_status(f"✅ Added: {text.strip()}")

    def _rename_class(self):
        """Rename selected class"""
        idx = self.list_widget.currentRow()
        if idx < 0:
            self._show_status("⚠️ Select a class first")
            return
        
        old_name = self.class_ini[idx]
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Rename Class", "New name:", 
            QtWidgets.QLineEdit.EchoMode.Normal, old_name
        )
        if ok and text.strip():
            self.class_ini[idx] = text.strip()
            self._refresh_list()
            self.list_widget.setCurrentRow(idx)
            self._save_config()
            self._show_status(f"✅ Renamed to: {text.strip()}")

    def _remove_class(self):
        """Remove selected class"""
        idx = self.list_widget.currentRow()
        if idx < 0:
            self._show_status("⚠️ Select a class first")
            return
        
        name = self.class_ini[idx]
        del self.class_ini[idx]
        self._refresh_list()
        self._save_config()
        self._show_status(f"✅ Deleted: {name}")

    def _reset_to_default(self):
        """Reset to default class order"""
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm Reset",
            f"Reset to default?\n({', '.join(DEFAULT_CLASS_INI)})",
            QtWidgets.QMessageBox.StandardButton.Yes | 
            QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.class_ini = DEFAULT_CLASS_INI.copy()
            self._refresh_list()
            self._save_config()
            self._show_status("✅ Reset to default")

    # === PROFILE MANAGEMENT ===
    def _save_profile(self):
        """Save current order as profile"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, "Save Profile", "Profile name:"
        )
        if ok and text.strip():
            name = text.strip()
            self.profiles[name] = list(self.class_ini)
            save_json(PROFILES_FILE, self.profiles)
            self._refresh_profiles()
            self.combo_profiles.setCurrentText(name)
            self._show_status(f"✅ Profile saved: {name}")

    def _load_profile(self):
        """Load selected profile"""
        name = self.combo_profiles.currentText()
        if not name:
            self._show_status("⚠️ No profile selected")
            return
        
        if name in self.profiles:
            self.class_ini = list(self.profiles[name])
            self._refresh_list()
            self._save_config()
            self._show_status(f"✅ Loaded: {name}")

    def _delete_profile(self):
        """Delete selected profile"""
        name = self.combo_profiles.currentText()
        if not name:
            self._show_status("⚠️ No profile selected")
            return
        
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm Delete", 
            f"Delete profile '{name}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | 
            QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            del self.profiles[name]
            save_json(PROFILES_FILE, self.profiles)
            self._refresh_profiles()
            self._show_status(f"✅ Deleted: {name}")

    # === SCRIPT GENERATION ===
    def _generate_cycle_only(self):
        """Generate cycle scripts only"""
        generate_cycle_forward(self.class_ini)
        generate_cycle_backward(self.class_ini)
        self._show_status("✅ Cycle scripts generated")

    def _generate_click_cycle_only(self):
        """Generate click & cycle script"""
        generate_click_cycle()
        self._show_status("✅ Click & cycle generated")

    def _generate_workspace_only(self):
        """Generate workspace toggle script"""
        generate_toggle_workspace()
        self._show_status("✅ Workspace script generated")

    def _generate_rename_only(self):
        """Generate rename script only"""
        generate_rename_script(self.class_ini)
        self._show_status("✅ Rename script generated")

    def _generate_reorganize_only(self):
        """Generate reorganize script only"""
        generate_reorganize_script(self.class_ini)
        self._show_status("✅ Reorganize script generated")

    def _generate_all_scripts(self):
        """Generate all scripts"""
        generate_rename_script(self.class_ini)
        generate_reorganize_script(self.class_ini)
        generate_cycle_forward(self.class_ini)
        generate_cycle_backward(self.class_ini)
        generate_toggle_workspace()
        generate_click_cycle()
        self._show_status("✅ All scripts generated")

    def _open_script_folder(self):
        """Open scripts folder in file manager"""
        try:
            run_cmd(['xdg-open', str(SCRIPT_DIR)])
            self._show_status("✅ Folder opened")
        except Exception:
            self._show_status("❌ Cannot open folder")

    # === QUICK RENAME ===
    def _quick_rename(self):
        """Quick rename without dialog (all workspaces)"""
        generate_rename_script(self.class_ini, workspace=None)
        try:
            result = run_cmd([str(RENAME_SCRIPT)])
            if result[2] == 0:
                self.tray.showMessage(
                    "Dofus Manager",
                    "✅ Windows renamed successfully",
                    QtWidgets.QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
            else:
                self.tray.showMessage(
                    "Dofus Manager",
                    "⚠️ Rename failed - check window count",
                    QtWidgets.QSystemTrayIcon.MessageIcon.Warning,
                    3000
                )
        except Exception as e:
            self.tray.showMessage(
                "Dofus Manager",
                f"❌ Error: {str(e)}",
                QtWidgets.QSystemTrayIcon.MessageIcon.Critical,
                3000
            )

    # === QUICK REORGANIZE ===
    def _quick_reorganize(self):
        """Quick reorganize windows left to right"""
        generate_reorganize_script(self.class_ini)
        try:
            result = run_cmd([str(REORGANIZE_SCRIPT)], timeout=10)
            if result[2] == 0:
                self._show_status("✅ Windows reorganized")
            else:
                error_msg = result[1] if result[1] else "Check window names"
                self._show_status(f"⚠️ {error_msg}")
        except Exception as e:
            self._show_status(f"❌ Error: {str(e)}")

    # === RENAME DIALOG ===
    def _show_rename_dialog(self):
        """Show workspace selection dialog for renaming"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Rename Windows")
        dialog.setFixedWidth(280)

        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # Info label
        info = QtWidgets.QLabel("Select workspace (optional):")
        info.setStyleSheet("font-size: 11px; color: #cccccc;")
        layout.addWidget(info)

        # Workspace options
        ws_layout = QtWidgets.QVBoxLayout()
        ws_layout.setSpacing(4)
        
        self.radio_all = QtWidgets.QRadioButton("All workspaces")
        self.radio_all.setChecked(True)
        self.radio_all.setStyleSheet("font-size: 11px;")
        ws_layout.addWidget(self.radio_all)
        
        self.radio_specific = QtWidgets.QRadioButton("Specific workspace:")
        self.radio_specific.setStyleSheet("font-size: 11px;")
        ws_layout.addWidget(self.radio_specific)
        
        layout.addLayout(ws_layout)

        # Workspace combo
        self.combo_workspace = QtWidgets.QComboBox()
        self.combo_workspace.setEnabled(False)
        self.combo_workspace.setFixedHeight(24)
        
        workspaces = get_workspaces()
        for ws_num, ws_name in workspaces:
            self.combo_workspace.addItem(f"{ws_num}: {ws_name}", ws_num)
        layout.addWidget(self.combo_workspace)

        self.radio_specific.toggled.connect(
            lambda checked: self.combo_workspace.setEnabled(checked)
        )

        layout.addSpacing(12)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(6)
        
        btn_execute = QtWidgets.QPushButton("🔄 Execute")
        btn_execute.setStyleSheet(get_action_button_style("#0d7377"))
        btn_execute.setFixedHeight(32)
        btn_execute.clicked.connect(lambda: self._execute_rename(dialog))
        
        btn_cancel = QtWidgets.QPushButton("Cancel")
        btn_cancel.setStyleSheet(get_action_button_style("#555555"))
        btn_cancel.setFixedHeight(32)
        btn_cancel.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(btn_execute)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        dialog.exec()

    def _execute_rename(self, dialog):
        """Execute rename with selected workspace"""
        workspace = None
        if self.radio_specific.isChecked():
            workspace = self.combo_workspace.currentData()
        
        # Generate and execute script
        generate_rename_script(self.class_ini, workspace)
        try:
            result = run_cmd([str(RENAME_SCRIPT)])
            if result[2] == 0:
                self._show_status("✅ Windows renamed")
                dialog.accept()
            else:
                self._show_status("⚠️ Check window count")
        except Exception as e:
            self._show_status(f"❌ Error: {str(e)}")