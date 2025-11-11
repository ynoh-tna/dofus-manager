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
from core.i18n import get_i18n, _
from ui.widgets import CompactDraggableList
from ui.theme import apply_compact_theme, get_icon_button_style, get_action_button_style

class DofusManager(QtWidgets.QMainWindow):
    """Gestionnaire principal de fenêtres Dofus"""
    
    def __init__(self):
        super().__init__()
        self.i18n = get_i18n()
        self.setWindowTitle(self.i18n.get('title'))
        
        # Taille compacte 
        self.setFixedSize(360, 800)
        
        # Flags de fenêtre
        self.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowMinimizeButtonHint
        )

        # Charger configuration
        cfg = load_json(CONFIG_FILE, {})
        self.class_ini = cfg.get('class_ini', DEFAULT_CLASS_INI.copy())
        self.profiles = load_json(PROFILES_FILE, {})

        # Setup UI
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

        # HEADER
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
        self.status_label = QtWidgets.QLabel(self.i18n.get('status_ready'))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color:#888;font-size:9px;padding:2px;")
        main_layout.addWidget(self.status_label)

    def _create_header(self):
        """Créer l'en-tête compacte"""
        header = QtWidgets.QHBoxLayout()
        header.setSpacing(6)

        title = QtWidgets.QLabel(self.i18n.get('app_name'))
        title.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold; 
            color: #0d7377;
        """)
        title.setToolTip(self.i18n.get('title'))
        header.addWidget(title)
        
        header.addStretch()

        btn_rename = QtWidgets.QPushButton(self.i18n.get('rename'))
        btn_rename.setStyleSheet(get_action_button_style("#0d7377"))
        btn_rename.setFixedSize(100, 28)
        btn_rename.setToolTip(self.i18n.get('rename_tooltip'))
        btn_rename.clicked.connect(self._show_rename_dialog)
        header.addWidget(btn_rename)

        btn_reorganize = QtWidgets.QPushButton(self.i18n.get('reorder'))
        btn_reorganize.setStyleSheet(get_action_button_style("#8b5cf6"))
        btn_reorganize.setFixedSize(100, 28)
        btn_reorganize.setToolTip(self.i18n.get('reorder_tooltip'))
        btn_reorganize.clicked.connect(self._quick_reorganize)
        header.addWidget(btn_reorganize)

        btn_settings = QtWidgets.QPushButton("⚙️")
        btn_settings.setStyleSheet(get_icon_button_style("#6366f1", size=28))
        btn_settings.setFixedSize(28, 28)
        btn_settings.setToolTip(self.i18n.get('settings_tooltip'))
        btn_settings.clicked.connect(self._show_settings_menu)
        header.addWidget(btn_settings)

        return header

    def _create_list_section(self):
        section = QtWidgets.QVBoxLayout()
        section.setSpacing(4)

        label = QtWidgets.QLabel(self.i18n.get('initiative_order'))
        label.setStyleSheet("font-size:11px;font-weight:bold;color:#ffffff;")
        section.addWidget(label)

        self.list_widget = CompactDraggableList()
        self.list_widget.orderChanged.connect(self._sync_from_list)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.list_widget)
        scroll.setStyleSheet("border:none;")
        section.addWidget(scroll, stretch=1)

        return section

    def _create_edit_toolbar(self):
        """Créer la barre d'outils d'édition"""
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(6)

        btn_add = QtWidgets.QPushButton(self.i18n.get('add_class'))
        btn_add.setStyleSheet(get_icon_button_style("#22c55e"))
        btn_add.setFixedSize(32, 32)
        btn_add.setToolTip(self.i18n.get('add_tooltip'))
        btn_add.clicked.connect(self._add_class)
        toolbar.addWidget(btn_add)

        btn_edit = QtWidgets.QPushButton(self.i18n.get('edit_class'))
        btn_edit.setStyleSheet(get_icon_button_style("#3b82f6"))
        btn_edit.setFixedSize(32, 32)
        btn_edit.setToolTip(self.i18n.get('edit_tooltip'))
        btn_edit.clicked.connect(self._rename_class)
        toolbar.addWidget(btn_edit)

        btn_del = QtWidgets.QPushButton(self.i18n.get('delete_class'))
        btn_del.setStyleSheet(get_icon_button_style("#ef4444"))
        btn_del.setFixedSize(32, 32)
        btn_del.setToolTip(self.i18n.get('delete_tooltip'))
        btn_del.clicked.connect(self._remove_class)
        toolbar.addWidget(btn_del)

        toolbar.addStretch()

        btn_reset = QtWidgets.QPushButton(self.i18n.get('reset'))
        btn_reset.setStyleSheet(get_icon_button_style("#f59e0b"))
        btn_reset.setFixedSize(32, 32)
        btn_reset.setToolTip(self.i18n.get('reset_tooltip'))
        btn_reset.clicked.connect(self._reset_to_default)
        toolbar.addWidget(btn_reset)

        return toolbar

    def _create_profile_section(self):
        """Créer la section des profils"""
        group = QtWidgets.QGroupBox(self.i18n.get('profiles'))
        group.setCheckable(False)
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
        self.combo_profiles.setToolTip(self.i18n.get('select_profile'))
        layout.addWidget(self.combo_profiles)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(4)

        buttons_config = [
            (self.i18n.get('save_profile_btn'), self.i18n.get('save_profile_tooltip'), self._save_profile),
            (self.i18n.get('load_profile_btn'), self.i18n.get('load_profile_tooltip'), self._load_profile),
            (self.i18n.get('delete_profile_btn'), self.i18n.get('delete_profile_tooltip'), self._delete_profile)
        ]
        
        for icon, tooltip, callback in buttons_config:
            btn = QtWidgets.QPushButton(icon)
            btn.setFixedSize(30, 26)
            btn.setToolTip(tooltip)
            btn.clicked.connect(callback)
            btn.setStyleSheet(get_icon_button_style("#555", size=26))
            btn_layout.addWidget(btn)

        layout.addLayout(btn_layout)
        return group

    def _create_actions_section(self):
        """Créer la section des actions rapides"""
        section = QtWidgets.QVBoxLayout()
        section.setSpacing(4)

        label = QtWidgets.QLabel(self.i18n.get('create_scripts'))
        label.setStyleSheet("""
            font-size: 11px; 
            font-weight: bold; 
            color: #ffffff;
        """)
        section.addWidget(label)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(4)
        grid.setContentsMargins(0, 0, 0, 0)

        buttons = [
            (self.i18n.get('cycle_bidirectional'), self.i18n.get('cycle_tooltip'), "#14b8a6", 
             self._generate_cycle_only, 0, 0),
            (self.i18n.get('rename_windows'), self.i18n.get('rename_tooltip_script'), "#8b5cf6", 
             self._generate_rename_only, 0, 1),
            (self.i18n.get('click_cycle'), self.i18n.get('click_cycle_tooltip'), "#84AB58", 
             self._generate_click_cycle_only, 1, 0),
            (self.i18n.get('workspaces'), self.i18n.get('workspaces_tooltip'), "#f59e0b", 
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
        """Afficher le menu des paramètres"""
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

        # Submenu langue
        lang_menu = menu.addMenu("🌍 Language / Langue")
        
        for lang_code in self.i18n.get_available_languages():
            lang_name = {'en': 'English', 'fr': 'Français'}[lang_code]
            action = lang_menu.addAction(lang_name)
            action.triggered.connect(lambda checked, code=lang_code: self._change_language(code))
            if self.i18n.language == lang_code:
                action.setText(f"✓ {lang_name}")

        menu.addSeparator()

        act_gen_all = menu.addAction(self.i18n.get('generate_all'))
        act_gen_all.triggered.connect(self._generate_all_scripts)

        menu.addSeparator()

        act_open = menu.addAction(self.i18n.get('open_folder'))
        act_open.triggered.connect(self._open_script_folder)

        act_about = menu.addAction(self.i18n.get('about'))
        act_about.triggered.connect(self._show_about)

        sender = self.sender()
        menu.exec(sender.mapToGlobal(sender.rect().bottomLeft()))

    def _change_language(self, language_code):
        """Changer la langue et redémarrer l'interface"""
        self.i18n.set_language(language_code)
        QtWidgets.QMessageBox.information(
            self,
            "Info" if language_code == 'en' else "Info",
            "Language changed. Please restart the application.\n" if language_code == 'en' 
            else "Langue modifiée. Veuillez redémarrer l'application.\n"
        )

    def _show_about(self):
        """Afficher la boîte À Propos"""
        about_text = self.i18n.get(
            'about_text',
            script_dir=SCRIPT_DIR,
            cycle_forward=CYCLE_FORWARD,
            cycle_backward=CYCLE_BACKWARD,
            click_cycle=CLICK_CYCLE_FORWARD,
            toggle_workspace=TOGGLE_WORKSPACE
        )
        
        QtWidgets.QMessageBox.information(
            self,
            self.i18n.get('about_title'),
            about_text
        )

    # === SYSTEM TRAY ===
    def _create_tray(self):
        """Créer l'icône de la barre des tâches"""
        self.tray = QtWidgets.QSystemTrayIcon(self)
        self.tray.setIcon(
            self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_ComputerIcon)
        )
        
        menu = QtWidgets.QMenu()
        
        show_action = menu.addAction(self.i18n.get('show_manager'))
        show_action.triggered.connect(self.showNormal)
        
        menu.addSeparator()
        
        rename_action = menu.addAction(self.i18n.get('tray_rename'))
        rename_action.triggered.connect(self._quick_rename)
        
        reorganize_action = menu.addAction(self.i18n.get('tray_order'))
        reorganize_action.triggered.connect(self._quick_reorganize)
        
        cycle_action = menu.addAction(self.i18n.get('tray_cycle'))
        cycle_action.triggered.connect(self._generate_cycle_only)
        
        menu.addSeparator()
        
        quit_action = menu.addAction(self.i18n.get('quit'))
        quit_action.triggered.connect(QtWidgets.QApplication.quit)
        
        self.tray.setContextMenu(menu)
        self.tray.setToolTip(self.i18n.get('title'))
        self.tray.activated.connect(self._on_tray_click)
        self.tray.show()

    def _on_tray_click(self, reason):
        """Gérer le clic sur l'icône de la barre des tâches"""
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            if self.isHidden() or self.isMinimized():
                self.showNormal()
                self.activateWindow()
            else:
                self.hide()

    def closeEvent(self, event):
        """Demander à l'utilisateur ce qu'il veut faire"""       
        menu = QtWidgets.QMessageBox(self)
        menu.setWindowTitle("Exit Options" if self.i18n.language == 'en' else "Options de Fermeture")
        menu.setText("What do you want to do?" if self.i18n.language == 'en' else "Que voulez-vous faire ?")
        btn_tray = menu.addButton(
            self.i18n.get('minimize_tray'), 
            QtWidgets.QMessageBox.ButtonRole.AcceptRole
        )
        btn_quit = menu.addButton(
            self.i18n.get('close_quit'), 
            QtWidgets.QMessageBox.ButtonRole.DestructRole
        )
        menu.exec()

        if menu.clickedButton() == btn_quit:
            event.accept()
        else:
            self.hide()
            self.tray.showMessage(
                self.i18n.get('title'), 
                self.i18n.get('running_tray'), 
                QtWidgets.QSystemTrayIcon.MessageIcon.Information, 
                2000
            )
            event.ignore()

    # === DATA MANAGEMENT ===
    def _refresh_all(self):
        """Actualiser tous les éléments de l'interface"""
        self._refresh_list()
        self._refresh_profiles()

    def _refresh_list(self):
        """Actualiser la liste des classes"""
        self.list_widget.clear()
        for i, name in enumerate(self.class_ini, 1):
            item = QtWidgets.QListWidgetItem(f"{i}. {name}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.list_widget.addItem(item)

    def _refresh_profiles(self):
        """Actualiser les profils"""
        current = self.combo_profiles.currentText()
        self.combo_profiles.clear()
        self.combo_profiles.addItems(sorted(self.profiles.keys()))
        if current in self.profiles:
            self.combo_profiles.setCurrentText(current)

    def _sync_from_list(self):
        """Synchroniser l'ordre à partir de la liste"""
        self.class_ini = [
            self.list_widget.item(i).data(Qt.ItemDataRole.UserRole)
            for i in range(self.list_widget.count())
        ]
        self._refresh_list()
        self._save_config()
        self._show_status(self.i18n.get('order_updated'), 2000)

    def _save_config(self):
        """Sauvegarder la configuration"""
        cfg = {'class_ini': self.class_ini}
        save_json(CONFIG_FILE, cfg)

    def _show_status(self, message, duration=3000):
        """Afficher un message de statut"""
        self.status_label.setText(message)
        QtCore.QTimer.singleShot(duration, lambda: self.status_label.setText(self.i18n.get('status_ready')))

    # === CLASS MANAGEMENT ===
    def _add_class(self):
        """Ajouter une classe"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, 
            self.i18n.get('add_class_dialog'), 
            self.i18n.get('add_class_prompt'), 
            QtWidgets.QLineEdit.EchoMode.Normal
        )
        if ok and text.strip():
            self.class_ini.append(text.strip())
            self._refresh_list()
            self._save_config()
            self._show_status(self.i18n.get('added', name=text.strip()))

    def _rename_class(self):
        """Renommer une classe"""
        idx = self.list_widget.currentRow()
        if idx < 0:
            self._show_status(self.i18n.get('select_class'))
            return
        
        old_name = self.class_ini[idx]
        text, ok = QtWidgets.QInputDialog.getText(
            self, 
            self.i18n.get('rename_class_dialog'), 
            self.i18n.get('rename_prompt'), 
            QtWidgets.QLineEdit.EchoMode.Normal, 
            old_name
        )
        if ok and text.strip():
            self.class_ini[idx] = text.strip()
            self._refresh_list()
            self.list_widget.setCurrentRow(idx)
            self._save_config()
            self._show_status(self.i18n.get('renamed_to', name=text.strip()))

    def _remove_class(self):
        """Supprimer une classe"""
        idx = self.list_widget.currentRow()
        if idx < 0:
            self._show_status(self.i18n.get('select_class'))
            return
        
        name = self.class_ini[idx]
        del self.class_ini[idx]
        self._refresh_list()
        self._save_config()
        self._show_status(self.i18n.get('deleted', name=name))

    def _reset_to_default(self):
        """Réinitialiser aux valeurs par défaut"""
        reply = QtWidgets.QMessageBox.question(
            self, 
            self.i18n.get('confirm_reset'),
            self.i18n.get('reset_message', classes=', '.join(DEFAULT_CLASS_INI)),
            QtWidgets.QMessageBox.StandardButton.Yes | 
            QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.class_ini = DEFAULT_CLASS_INI.copy()
            self._refresh_list()
            self._save_config()
            self._show_status(self.i18n.get('reset_default'))

    # === PROFILE MANAGEMENT ===
    def _save_profile(self):
        """Sauvegarder le profil courant"""
        text, ok = QtWidgets.QInputDialog.getText(
            self, 
            self.i18n.get('save_profile_dialog'), 
            self.i18n.get('save_profile_prompt')
        )
        if ok and text.strip():
            name = text.strip()
            self.profiles[name] = list(self.class_ini)
            save_json(PROFILES_FILE, self.profiles)
            self._refresh_profiles()
            self.combo_profiles.setCurrentText(name)
            self._show_status(self.i18n.get('profile_saved', name=name))

    def _load_profile(self):
        """Charger le profil sélectionné"""
        name = self.combo_profiles.currentText()
        if not name:
            self._show_status(self.i18n.get('no_profile'))
            return
        
        if name in self.profiles:
            self.class_ini = list(self.profiles[name])
            self._refresh_list()
            self._save_config()
            self._show_status(self.i18n.get('profile_loaded', name=name))

    def _delete_profile(self):
        """Supprimer le profil sélectionné"""
        name = self.combo_profiles.currentText()
        if not name:
            self._show_status(self.i18n.get('no_profile'))
            return
        
        reply = QtWidgets.QMessageBox.question(
            self, 
            self.i18n.get('confirm_delete'), 
            self.i18n.get('delete_profile_msg', name=name),
            QtWidgets.QMessageBox.StandardButton.Yes | 
            QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            del self.profiles[name]
            save_json(PROFILES_FILE, self.profiles)
            self._refresh_profiles()
            self._show_status(self.i18n.get('profile_deleted', name=name))

    # === SCRIPT GENERATION ===
    def _generate_cycle_only(self):
        """Générer les scripts de cycle"""
        generate_cycle_forward(self.class_ini)
        generate_cycle_backward(self.class_ini)
        self._show_status(self.i18n.get('cycle_generated'))

    def _generate_click_cycle_only(self):
        """Générer le script clic & cycle"""
        generate_click_cycle()
        self._show_status(self.i18n.get('click_cycle_gen'))

    def _generate_workspace_only(self):
        """Générer le script d'espace de travail"""
        generate_toggle_workspace()
        self._show_status(self.i18n.get('workspace_gen'))

    def _generate_rename_only(self):
        """Générer le script de renommage"""
        generate_rename_script(self.class_ini)
        self._show_status(self.i18n.get('rename_gen'))

    def _generate_reorganize_only(self):
        """Générer le script de réorganisation"""
        generate_reorganize_script(self.class_ini)
        self._show_status(self.i18n.get('reorder_gen'))

    def _generate_all_scripts(self):
        """Générer tous les scripts"""
        generate_rename_script(self.class_ini)
        generate_reorganize_script(self.class_ini)
        generate_cycle_forward(self.class_ini)
        generate_cycle_backward(self.class_ini)
        generate_toggle_workspace()
        generate_click_cycle()
        self._show_status(self.i18n.get('all_gen'))

    def _open_script_folder(self):
        """Ouvrir le dossier des scripts"""
        try:
            run_cmd(['xdg-open', str(SCRIPT_DIR)])
            self._show_status(self.i18n.get('folder_opened'))
        except Exception:
            self._show_status(self.i18n.get('folder_error'))

    # === QUICK RENAME ===
    def _quick_rename(self):
        """Renommer rapidement"""
        generate_rename_script(self.class_ini, workspace=None)
        try:
            result = run_cmd([str(RENAME_SCRIPT)])
            if result[2] == 0:
                self.tray.showMessage(
                    self.i18n.get('title'),
                    self.i18n.get('windows_renamed'),
                    QtWidgets.QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
            else:
                self.tray.showMessage(
                    self.i18n.get('title'),
                    self.i18n.get('rename_failed'),
                    QtWidgets.QSystemTrayIcon.MessageIcon.Warning,
                    3000
                )
        except Exception as e:
            self.tray.showMessage(
                self.i18n.get('title'),
                self.i18n.get('error', msg=str(e)),
                QtWidgets.QSystemTrayIcon.MessageIcon.Critical,
                3000
            )

    # === QUICK REORGANIZE ===
    def _quick_reorganize(self):
        """Réorganiser rapidement"""
        generate_reorganize_script(self.class_ini)
        try:
            result = run_cmd([str(REORGANIZE_SCRIPT)], timeout=10)
            if result[2] == 0:
                self._show_status(self.i18n.get('windows_reorg'))
            else:
                error_msg = result[1] if result[1] else self.i18n.get('check_names')
                self._show_status(error_msg)
        except Exception as e:
            self._show_status(self.i18n.get('error', msg=str(e)))

    # === RENAME DIALOG ===
    def _show_rename_dialog(self):
        """Afficher la boîte de dialogue de renommage"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(self.i18n.get('rename_class_dialog'))
        dialog.setFixedWidth(280)

        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        info = QtWidgets.QLabel(self.i18n.get('workspace_selection'))
        info.setStyleSheet("font-size: 11px; color: #cccccc;")
        layout.addWidget(info)

        ws_layout = QtWidgets.QVBoxLayout()
        ws_layout.setSpacing(4)
        
        self.radio_all = QtWidgets.QRadioButton(self.i18n.get('all_workspaces'))
        self.radio_all.setChecked(True)
        self.radio_all.setStyleSheet("font-size: 11px;")
        ws_layout.addWidget(self.radio_all)
        
        self.radio_specific = QtWidgets.QRadioButton(self.i18n.get('specific_workspace'))
        self.radio_specific.setStyleSheet("font-size: 11px;")
        ws_layout.addWidget(self.radio_specific)
        
        layout.addLayout(ws_layout)

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

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(6)
        
        btn_execute = QtWidgets.QPushButton(self.i18n.get('execute'))
        btn_execute.setStyleSheet(get_action_button_style("#0d7377"))
        btn_execute.setFixedHeight(32)
        btn_execute.clicked.connect(lambda: self._execute_rename(dialog))
        
        btn_cancel = QtWidgets.QPushButton(self.i18n.get('cancel'))
        btn_cancel.setStyleSheet(get_action_button_style("#555555"))
        btn_cancel.setFixedHeight(32)
        btn_cancel.clicked.connect(dialog.reject)
        
        btn_layout.addWidget(btn_execute)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

        dialog.exec()

    def _execute_rename(self, dialog):
        """Exécuter le renommage avec l'espace de travail sélectionné"""
        workspace = None
        if self.radio_specific.isChecked():
            workspace = self.combo_workspace.currentData()
        
        generate_rename_script(self.class_ini, workspace)
        try:
            result = run_cmd([str(RENAME_SCRIPT)])
            if result[2] == 0:
                self._show_status(self.i18n.get('windows_renamed'))
                dialog.accept()
            else:
                self._show_status(self.i18n.get('check_names'))
        except Exception as e:
            self._show_status(self.i18n.get('error', msg=str(e)))