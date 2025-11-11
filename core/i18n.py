from pathlib import Path
import json

# Dictionnaire de traductions
TRANSLATIONS = {
    'en': {
        # Menu principal
        'title': 'Dofus Window Manager',
        'app_name': '🎮 Dofus WM',
        'rename': '🔧 Rename',
        'reorder': '🔄 ReOrder',
        'rename_tooltip': 'Rename all Dofus windows\naccording to initiative order',
        'reorder_tooltip': 'Reorganize windows left to right\naccording to initiative order',
        'settings_tooltip': 'Generate all scripts\nand open folder',
        
        # Sections
        'initiative_order': '📋 Initiative Order',
        'profiles': '💾 Profiles',
        'create_scripts': '⚡ Create or Update Scripts',
        'status_ready': 'Ready',
        
        # Profils
        'select_profile': 'Select a saved profile',
        'save_profile_btn': '💾',
        'load_profile_btn': '📤',
        'delete_profile_btn': '🗑️',
        'save_profile_tooltip': 'Save profile',
        'load_profile_tooltip': 'Load profile',
        'delete_profile_tooltip': 'Delete profile',
        
        # Toolbar
        'add_class': '➕',
        'edit_class': '✏️',
        'delete_class': '🗑️',
        'reset': '🔄',
        'add_tooltip': 'Add new class to order',
        'edit_tooltip': 'Rename selected class',
        'delete_tooltip': 'Delete selected class',
        'reset_tooltip': 'Reset to default classes\n(Feca, Cra, Enu, Panda, Sadi)',
        
        # Scripts
        'cycle_bidirectional': '🔄 Cycle <>',
        'rename_windows': '✏️ Rename windows',
        'click_cycle': '🖱️ Click and Cycle',
        'workspaces': '🗃️ Workspaces',
        'cycle_tooltip': 'Generate cycle forward/backward scripts',
        'rename_tooltip_script': 'Rename windows script',
        'click_cycle_tooltip': 'Generate click & cycle script',
        'workspaces_tooltip': 'Generate workspace toggle script',
        
        # Menu contextuel
        'generate_all': '🔧 Generate All Scripts',
        'open_folder': '📁 Open Scripts Folder',
        'about': 'ℹ️ About',
        
        # Tray
        'show_manager': '🎮 Show Manager',
        'tray_rename': '🔄 Rename Windows',
        'tray_order': '🔧 Order Windows',
        'tray_cycle': '🔁 Generate Cycle Scripts',
        'quit': '❌ Quit',
        'minimize_tray': 'Minimize to tray',
        'close_quit': 'Quit',
        'running_tray': 'Running in system tray',
        
        # Dialogues
        'add_class_dialog': 'Add Class',
        'add_class_prompt': 'Class name:',
        'rename_class_dialog': 'Rename Class',
        'rename_prompt': 'New name:',
        'confirm_reset': 'Confirm Reset',
        'reset_message': 'Reset to default?\n({classes})',
        'confirm_delete': 'Confirm Delete',
        'delete_profile_msg': 'Delete profile \'{name}\'?',
        'save_profile_dialog': 'Save Profile',
        'save_profile_prompt': 'Profile name:',
        
        # Workspace
        'workspace_selection': 'Select workspace (optional):',
        'all_workspaces': 'All workspaces',
        'specific_workspace': 'Specific workspace:',
        'execute': '🔄 Execute',
        'cancel': 'Cancel',
        
        # Status messages
        'order_updated': '✅ Order updated',
        'added': '✅ Added: {name}',
        'renamed_to': '✅ Renamed to: {name}',
        'deleted': '✅ Deleted: {name}',
        'reset_default': '✅ Reset to default',
        'profile_saved': '✅ Profile saved: {name}',
        'profile_loaded': '✅ Loaded: {name}',
        'profile_deleted': '✅ Deleted: {name}',
        'select_class': '⚠️ Select a class first',
        'no_profile': '⚠️ No profile selected',
        'cycle_generated': '✅ Cycle scripts generated',
        'click_cycle_gen': '✅ Click & cycle generated',
        'workspace_gen': '✅ Workspace script generated',
        'rename_gen': '✅ Rename script generated',
        'reorder_gen': '✅ Reorganize script generated',
        'all_gen': '✅ All scripts generated',
        'folder_opened': '✅ Folder opened',
        'folder_error': '❌ Cannot open folder',
        'windows_renamed': '✅ Windows renamed successfully',
        'rename_failed': '⚠️ Rename failed - check window count',
        'error': '❌ Error: {msg}',
        'windows_reorg': '✅ Windows reorganized',
        'check_names': '⚠️ Check window names',
        
        # About
        'about_title': 'About',
        'about_text': (
            '⚙️ Dofus Manager\n\n'
            'Manage and organize your Dofus windows efficiently.\n\n'
            '📌 Buttons:\n'
            '• Rename  — Rename opened Dofus windows based on initiative order.\n'
            '• Reorder — Reorganize windows visually by initiative order.\n\n'
            '🧩 Scripts overview:\n'
            '• cycle_forward.sh     — Cycle forward through windows.\n'
            '• cycle_backward.sh    — Cycle backward through windows.\n'
            '• rename_windows.sh    — Rename all opened windows.\n'
            '• reorganize_windows.sh— Align windows left to right.\n'
            '• click_cycle_forward.sh— Click + cycle forward.\n'
            '• toggle_workspace.sh  — Switch between workspaces.\n\n'
            '📁 Script location:\n{script_dir}\n\n'
            '🎮 Suggested key bindings:\n'
            '{cycle_forward}\n{cycle_backward}\n{click_cycle}\n{toggle_workspace}\n'
            '© 2025 Dofus Manager'
        ),
        'yes': 'Yes',
        'no': 'No',
    },
    'fr': {
        # Menu principal
        'title': 'Gestionnaire de Fenêtres Dofus',
        'app_name': '🎮 Dofus WM',
        'rename': '🔧 Renommer',
        'reorder': '🔄 Réorganiser',
        'rename_tooltip': 'Renommer toutes les fenêtres Dofus\nselon l\'ordre d\'initiative',
        'reorder_tooltip': 'Réorganiser les fenêtres de gauche à droite\nselon l\'ordre d\'initiative',
        'settings_tooltip': 'Générer tous les scripts\net ouvrir le dossier',
        
        # Sections
        'initiative_order': '📋 Ordre d\'Initiative',
        'profiles': '💾 Profils',
        'create_scripts': '⚡ Créer ou Mettre à Jour les Scripts',
        'status_ready': 'Prêt',
        
        # Profils
        'select_profile': 'Sélectionner un profil enregistré',
        'save_profile_btn': '💾',
        'load_profile_btn': '📤',
        'delete_profile_btn': '🗑️',
        'save_profile_tooltip': 'Enregistrer le profil',
        'load_profile_tooltip': 'Charger le profil',
        'delete_profile_tooltip': 'Supprimer le profil',
        
        # Toolbar
        'add_class': '➕',
        'edit_class': '✏️',
        'delete_class': '🗑️',
        'reset': '🔄',
        'add_tooltip': 'Ajouter une nouvelle classe à l\'ordre',
        'edit_tooltip': 'Renommer la classe sélectionnée',
        'delete_tooltip': 'Supprimer la classe sélectionnée',
        'reset_tooltip': 'Réinitialiser aux classes par défaut\n(Feca, Cra, Enu, Panda, Sadi)',
        
        # Scripts
        'cycle_bidirectional': '🔄 Cycle',
        'rename_windows': '✏️ Renommer les fenêtres',
        'click_cycle': '🖱️ Clic et Cycle',
        'workspaces': '🗃️ Espaces de Travail',
        'cycle_tooltip': 'Générer les scripts de cycle avant/arrière',
        'rename_tooltip_script': 'Script de renommage des fenêtres',
        'click_cycle_tooltip': 'Générer le script clic & cycle',
        'workspaces_tooltip': 'Générer le script d\'alternance d\'espace de travail',
        
        # Menu contextuel
        'generate_all': '🔧 Générer Tous les Scripts',
        'open_folder': '📁 Ouvrir le Dossier des Scripts',
        'about': 'ℹ️ À Propos',
        
        # Tray
        'show_manager': '🎮 Afficher le Gestionnaire',
        'tray_rename': '🔄 Renommer les Fenêtres',
        'tray_order': '🔧 Organiser les Fenêtres',
        'tray_cycle': '🔁 Générer les Scripts de Cycle',
        'quit': '❌ Quitter',
        'minimize_tray': 'Réduire dans la barre des tâches',
        'close_quit': 'Quitter',
        'running_tray': 'En cours d\'exécution dans la barre des tâches',
        
        # Dialogues
        'add_class_dialog': 'Ajouter une Classe',
        'add_class_prompt': 'Nom de la classe :',
        'rename_class_dialog': 'Renommer la Classe',
        'rename_prompt': 'Nouveau nom :',
        'confirm_reset': 'Confirmer la Réinitialisation',
        'reset_message': 'Réinitialiser aux valeurs par défaut ?\n({classes})',
        'confirm_delete': 'Confirmer la Suppression',
        'delete_profile_msg': 'Supprimer le profil « {name} » ?',
        'save_profile_dialog': 'Enregistrer le Profil',
        'save_profile_prompt': 'Nom du profil :',
        
        # Workspace
        'workspace_selection': 'Sélectionner un espace de travail (optionnel) :',
        'all_workspaces': 'Tous les espaces de travail',
        'specific_workspace': 'Espace de travail spécifique :',
        'execute': '🔄 Exécuter',
        'cancel': 'Annuler',
        
        # Status messages
        'order_updated': '✅ Ordre mis à jour',
        'added': '✅ Ajouté : {name}',
        'renamed_to': '✅ Renommé en : {name}',
        'deleted': '✅ Supprimé : {name}',
        'reset_default': '✅ Réinitialisation aux valeurs par défaut',
        'profile_saved': '✅ Profil enregistré : {name}',
        'profile_loaded': '✅ Chargé : {name}',
        'profile_deleted': '✅ Supprimé : {name}',
        'select_class': '⚠️ Sélectionner d\'abord une classe',
        'no_profile': '⚠️ Aucun profil sélectionné',
        'cycle_generated': '✅ Scripts de cycle générés',
        'click_cycle_gen': '✅ Clic & cycle généré',
        'workspace_gen': '✅ Script d\'espace de travail généré',
        'rename_gen': '✅ Script de renommage généré',
        'reorder_gen': '✅ Script de réorganisation généré',
        'all_gen': '✅ Tous les scripts générés',
        'folder_opened': '✅ Dossier ouvert',
        'folder_error': '❌ Impossible d\'ouvrir le dossier',
        'windows_renamed': '✅ Fenêtres renommées avec succès',
        'rename_failed': '⚠️ Échec du renommage - vérifiez le nombre de fenêtres',
        'error': '❌ Erreur : {msg}',
        'windows_reorg': '✅ Fenêtres réorganisées',
        'check_names': '⚠️ Vérifiez les noms des fenêtres',
        
        # About
        'about_title': 'À Propos',
        'about_text': (
            '⚙️ Gestionnaire Dofus\n\n'
            'Gérez et organisez efficacement vos fenêtres Dofus.\n\n'
            '📌 Boutons :\n'
            '• Renommer    — Renommer les fenêtres Dofus ouvertes selon l\'ordre d\'initiative.\n'
            '• Réorganiser — Réorganiser visuellement les fenêtres par ordre d\'initiative.\n\n'
            '🧩 Aperçu des scripts :\n'
            '• cycle_forward.sh     — Cycle avant à travers les fenêtres.\n'
            '• cycle_backward.sh    — Cycle arrière à travers les fenêtres.\n'
            '• rename_windows.sh    — Renommer toutes les fenêtres ouvertes.\n'
            '• reorganize_windows.sh— Aligner les fenêtres de gauche à droite.\n'
            '• click_cycle_forward.sh— Clic + cycle avant.\n'
            '• toggle_workspace.sh  — Basculer entre les espaces de travail.\n\n'
            '📁 Emplacement des scripts :\n{script_dir}\n\n'
            '🎮 Raccourcis clavier suggérés :\n'
            '{cycle_forward}\n{cycle_backward}\n{click_cycle}\n{toggle_workspace}\n'
            '© 2025 Gestionnaire Dofus'
        ),
        'yes': 'Oui',
        'no': 'Non',
    }
}

class I18n:
    """Gestionnaire de localisation pour l'application"""
    
    def __init__(self, language='en'):
        self.language = language if language in TRANSLATIONS else 'en'
        self.config_dir = Path.home() / ".config" / "dofus_window_manager"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.lang_file = self.config_dir / "language.json"
        self._load_saved_language()
    
    def _load_saved_language(self):
        """Charger la langue précédemment sauvegardée"""
        try:
            if self.lang_file.exists():
                with open(self.lang_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    saved_lang = data.get('language', 'en')
                    if saved_lang in TRANSLATIONS:
                        self.language = saved_lang
        except Exception:
            pass
    
    def save_language(self):
        """Sauvegarder la langue sélectionnée"""
        try:
            with open(self.lang_file, 'w', encoding='utf-8') as f:
                json.dump({'language': self.language}, f)
        except Exception:
            pass
    
    def set_language(self, language):
        """Définir la langue"""
        if language in TRANSLATIONS:
            self.language = language
            self.save_language()
    
    def get(self, key, **kwargs):
        """Obtenir une traduction avec support des variables"""
        text = TRANSLATIONS.get(self.language, {}).get(key, 
               TRANSLATIONS['en'].get(key, key))
        
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        return text
    
    def get_available_languages(self):
        """Obtenir la liste des langues disponibles"""
        return list(TRANSLATIONS.keys())


# Instance globale
_i18n = None

def get_i18n():
    """Obtenir l'instance globale de I18n"""
    global _i18n
    if _i18n is None:
        _i18n = I18n()
    return _i18n

def _(key, **kwargs):
    """Alias court pour la traduction"""
    return get_i18n().get(key, **kwargs)