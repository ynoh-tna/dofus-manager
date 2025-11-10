from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt

from core.config import (
    APP_NAME, CONFIG_FILE, PROFILES_FILE, DEFAULT_CLASS_INI,
    RENAME_SCRIPT, CLICK_CYCLE_FORWARD,CYCLE_FORWARD, CYCLE_BACKWARD, TOGGLE_WORKSPACE, SCRIPT_DIR
)
from core.config import load_json, save_json
from core.scripts import (
    generate_rename_script, generate_cycle_forward, generate_cycle_backward, generate_toggle_workspace, generate_click_cycle
)
from core.workspace import get_workspaces
from core.utils import make_executable, run_cmd
from ui.widgets import DraggableList
from ui.theme import apply_dark_theme, lighten_color, darken_color


class DofusManager(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(800, 500)

        # Load config
        cfg = load_json(CONFIG_FILE, {})
        self.class_ini = cfg.get('class_ini', DEFAULT_CLASS_INI.copy())
        self.profiles = load_json(PROFILES_FILE, {})

        self._setup_ui()
        apply_dark_theme(self)
        self._create_tray()
        self._refresh_all()

    def _setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # HEADER
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("🎮 Dofus Window Manager")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0d7377;")
        header.addWidget(title)
        header.addStretch()

        self.btn_rename = self._create_button("🔄 Rename Windows", "#0d7377", self._show_rename_dialog)
        header.addWidget(self.btn_rename)
        main_layout.addLayout(header)

        # CONTENT
        content = QtWidgets.QHBoxLayout()
        main_layout.addLayout(content, 1)

        # LEFT PANEL - Initiative Order
        left_panel = QtWidgets.QVBoxLayout()
        left_panel.setSpacing(6)
        left_panel.setContentsMargins(0, 0, 0, 0) 
        content.addLayout(left_panel, 3)

        label_init = QtWidgets.QLabel("📋 Initiative Order")
        label_init.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffffff;")
        left_panel.addWidget(label_init)

        self.list_widget = DraggableList()
        self.list_widget.orderChanged.connect(self._sync_from_list)
        self.list_widget.setFixedHeight(280)  # compact
        left_panel.addWidget(self.list_widget)

        # Edit toolbar
        edit_toolbar = QtWidgets.QHBoxLayout()
        edit_toolbar.setSpacing(6)

        btn_add = self._create_icon_button("➕", "Add", "#22c55e", self._add_class)
        btn_edit = self._create_icon_button("✏️", "Rename", "#3b82f6", self._rename_class)
        btn_del = self._create_icon_button("🗑️", "Delete", "#ef4444", self._remove_class)
        for btn in [btn_add, btn_edit, btn_del]:
            btn.setFixedSize(32, 32)

        edit_toolbar.addWidget(btn_add)
        edit_toolbar.addWidget(btn_edit)
        edit_toolbar.addWidget(btn_del)
        edit_toolbar.addStretch()

        btn_reset = self._create_small_button("🔄 Reset to Default", "#f59e0b", self._reset_to_default)
        btn_reset.setFixedHeight(24)
        edit_toolbar.addWidget(btn_reset)

        left_panel.addLayout(edit_toolbar)
        spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        left_panel.addItem(spacer)

        # hint = QtWidgets.QLabel("💡 Drag & drop to reorder")
        # hint.setStyleSheet("color: #888888; font-size: 10px; font-style: italic;")
        # hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # left_panel.addWidget(hint)

        # RIGHT PANEL - Profiles & Scripts
        right_panel = QtWidgets.QVBoxLayout()
        content.addLayout(right_panel, 2)

        # Profiles
        profile_box = QtWidgets.QGroupBox("💾 Profiles")
        profile_box.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                color: #ffffff;
                border: 2px solid #444444;
                border-radius: 6px;
                margin: 5px;
                padding: 5px;
            }
        """)
        profile_layout = QtWidgets.QVBoxLayout(profile_box)
        profile_layout.setContentsMargins(5, 5, 5, 5)
        profile_layout.setSpacing(4)

        self.combo_profiles = QtWidgets.QComboBox()
        self.combo_profiles.setFixedHeight(22)
        profile_layout.addWidget(self.combo_profiles)

        profile_btns = QtWidgets.QHBoxLayout()
        profile_btns.setSpacing(4)
        btn_save_prof = self._create_small_button("💾 Save", "#0d7377", self._save_profile)
        btn_load_prof = self._create_small_button("📂 Load", "#14b8a6", self._load_profile)
        btn_del_prof = self._create_small_button("🗑️ Delete", "#ef4444", self._delete_profile)
        for btn in [btn_save_prof, btn_load_prof, btn_del_prof]:
            btn.setFixedHeight(22)

        profile_btns.addWidget(btn_save_prof)
        profile_btns.addWidget(btn_load_prof)
        profile_btns.addWidget(btn_del_prof)
        profile_layout.addLayout(profile_btns)

        right_panel.addWidget(profile_box)

        # Scripts info
        scripts_box = QtWidgets.QGroupBox("📜 Generated Scripts")
        scripts_box.setStyleSheet("""
            QGroupBox {
                font-size: 12px;
                font-weight: bold;
                color: #ffffff;
                border: 2px solid #444444;
                border-radius: 6px;
                margin: 5px;
                padding: 5px;
            }
        """)
        scripts_layout = QtWidgets.QVBoxLayout(scripts_box)
        scripts_layout.setContentsMargins(5, 5, 5, 5)
        scripts_layout.setSpacing(4)

        self.lbl_scripts = QtWidgets.QLabel()
        self.lbl_scripts.setWordWrap(True)
        self.lbl_scripts.setStyleSheet("color: #cccccc; font-size: 10px;")
        self._update_script_paths()
        scripts_layout.addWidget(self.lbl_scripts)

        gen_layout = QtWidgets.QVBoxLayout()
        gen_layout.setSpacing(4)

        btn_gen_rename = self._create_small_button("✏️ Rename", "#0d7377", self._generate_rename_only)
        btn_gen_cycle = self._create_small_button("🔄 Cycle", "#14b8a6", self._generate_cycle_only)
        btn_click_gen_cycle = self._create_small_button("🖱️ Click & Cycle", "#84AB58", self._generate_click_cycle_only)
        btn_gen_workspace = self._create_small_button("🗃️ Workspace", "#f59e0b", self._generate_workspace_only)
        btn_gen_all = self._create_small_button("🔧 All", "#6366f1", self._generate_all_scripts)

        for btn in [btn_gen_rename, btn_gen_cycle, btn_click_gen_cycle, btn_gen_workspace, btn_gen_all]:
            btn.setFixedHeight(24)
            gen_layout.addWidget(btn)

        scripts_layout.addLayout(gen_layout)

        btn_open_folder = self._create_small_button("📁 Open Folder", "#8b5cf6", self._open_script_folder)
        btn_open_folder.setFixedHeight(24)
        scripts_layout.addWidget(btn_open_folder)

        right_panel.addWidget(scripts_box)
        right_panel.addStretch()

        # STATUS BAR
        self.status = QtWidgets.QStatusBar()
        self.status.setStyleSheet("color: #aaaaaa; font-size: 10px;")
        self.setStatusBar(self.status)

    # THEME / UI HELPERS
    def _create_button(self, text, color, callback):
        btn = QtWidgets.QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {darken_color(color)};
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    def _create_small_button(self, text, color, callback):
        btn = QtWidgets.QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 10px;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {lighten_color(color)};
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    def _create_icon_button(self, icon, tooltip, color, callback):
        btn = QtWidgets.QPushButton(icon)
        btn.setToolTip(tooltip)
        btn.setFixedSize(32, 32)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {lighten_color(color)};
            }}
        """)
        btn.clicked.connect(callback)
        return btn
    # TRAY
    def _create_tray(self):
        self.tray = QtWidgets.QSystemTrayIcon(self)
        self.tray.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ComputerIcon))
        menu = QtWidgets.QMenu()
        show_action = menu.addAction("Show")
        show_action.triggered.connect(self.showNormal)
        menu.addSeparator()
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(QtWidgets.QApplication.quit)
        self.tray.setContextMenu(menu)
        self.tray.setToolTip(APP_NAME)
        self.tray.activated.connect(self._on_tray_click)
        self.tray.show()

    def _on_tray_click(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            self.showNormal() if self.isHidden() else self.hide()

    # DATA MANAGEMENT
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

    def _update_script_paths(self):
        self.lbl_scripts.setText(
            f"Rename: {RENAME_SCRIPT.name}\n"
            f"Forward: {CYCLE_FORWARD.name}\n"
            f"Click & Forward: {CLICK_CYCLE_FORWARD.name}\n"
            f"Backward: {CYCLE_BACKWARD.name}\n"
            f"Workspace: {TOGGLE_WORKSPACE.name}\n\n"
            f"📁 {SCRIPT_DIR}"
        )

    def _save_config(self):
        cfg = {'class_ini': self.class_ini}
        save_json(CONFIG_FILE, cfg)

    def _update_scripts(self):
        generate_rename_script(self.class_ini)
        generate_cycle_forward(self.class_ini)
        generate_cycle_backward(self.class_ini)
        generate_toggle_workspace()
        generate_click_cycle()
        self._update_script_paths()

    def _generate_rename_only(self):
        generate_rename_script(self.class_ini)

    def _generate_cycle_only(self):
        generate_cycle_forward(self.class_ini)
        generate_cycle_backward(self.class_ini)

    def _generate_click_cycle_only(self):
        generate_click_cycle()

    def _generate_workspace_only(self):
        generate_toggle_workspace()

    def _generate_all_scripts(self):
        self._update_scripts()

    # CLASS ACTIONS
    def _add_class(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Add Class", "Class name:")
        if ok and text.strip():
            self.class_ini.append(text.strip())
            self._refresh_list()
            self._save_config()

    def _rename_class(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            return
        old_name = self.class_ini[idx]
        text, ok = QtWidgets.QInputDialog.getText(self, "Rename", "New name:", text=old_name)
        if ok and text.strip():
            self.class_ini[idx] = text.strip()
            self._refresh_list()
            self.list_widget.setCurrentRow(idx)
            self._save_config()

    def _remove_class(self):
        idx = self.list_widget.currentRow()
        if idx < 0:
            return
        name = self.class_ini[idx]
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm", f"Delete {name}?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            del self.class_ini[idx]
            self._refresh_list()
            self._save_config()

    def _reset_to_default(self):
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm Reset",
            f"Reset to default classes?\n({', '.join(DEFAULT_CLASS_INI)})",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.class_ini = DEFAULT_CLASS_INI.copy()
            self._refresh_list()
            self._save_config()

    # PROFILE ACTIONS
    def _save_profile(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "Save Profile", "Profile name:")
        if ok and text.strip():
            name = text.strip()
            self.profiles[name] = list(self.class_ini)
            save_json(PROFILES_FILE, self.profiles)
            self._refresh_profiles()
            self.combo_profiles.setCurrentText(name)

    def _load_profile(self):
        name = self.combo_profiles.currentText()
        if not name:
            return
        if name in self.profiles:
            self.class_ini = list(self.profiles[name])
            self._refresh_list()
            self._save_config()

    def _delete_profile(self):
        name = self.combo_profiles.currentText()
        if not name:
            return
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm", f"Delete profile '{name}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            del self.profiles[name]
            save_json(PROFILES_FILE, self.profiles)
            self._refresh_profiles()

    # RENAME DIALOG
    def _show_rename_dialog(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Rename Windows")
        dialog.setMinimumWidth(400)

        layout = QtWidgets.QVBoxLayout(dialog)
        info = QtWidgets.QLabel("Select workspace to rename windows (optional):")
        layout.addWidget(info)

        ws_layout = QtWidgets.QHBoxLayout()
        self.radio_all = QtWidgets.QRadioButton("All workspaces")
        self.radio_all.setChecked(True)
        ws_layout.addWidget(self.radio_all)
        self.radio_specific = QtWidgets.QRadioButton("Specific workspace:")
        ws_layout.addWidget(self.radio_specific)
        layout.addLayout(ws_layout)

        self.combo_workspace = QtWidgets.QComboBox()
        self.combo_workspace.setEnabled(False)

        workspaces = get_workspaces()
        for ws_num, ws_name in workspaces:
            self.combo_workspace.addItem(f"{ws_num}: {ws_name}", ws_num)
        layout.addWidget(self.combo_workspace)

        self.radio_specific.toggled.connect(lambda checked: self.combo_workspace.setEnabled(checked))

        layout.addSpacing(20)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_execute = QtWidgets.QPushButton("🔄 Execute Rename")
        btn_execute.clicked.connect(lambda: self._execute_rename(dialog))
        btn_cancel = QtWidgets.QPushButton("Cancel")
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_execute)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        dialog.exec()

    def _execute_rename(self, dialog):
        workspace = None
        if self.radio_specific.isChecked():
            workspace = self.combo_workspace.currentData()
        # Generate script with workspace filter
        generate_rename_script(self.class_ini, workspace)

        # Execute the script
        try:
            result = run_cmd([str(RENAME_SCRIPT)])
            code = result[2]
            if code == 0:
                dialog.accept()
            else:
                self.status.showMessage("⚠️ Rename error: check windows", 5000)
        except Exception as e:
            self.status.showMessage(f"❌ Error: {str(e)}", 5000)

    def _open_script_folder(self):
        try:
            run_cmd(['xdg-open', str(SCRIPT_DIR)])
        except Exception:
            self.status.showMessage("❌ Cannot open folder", 3000)