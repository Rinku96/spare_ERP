from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, 
                             QComboBox, QGroupBox, QCheckBox, QFileDialog, QDialog, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
from styles import (COLOR_ACCENT_CYAN, COLOR_ACCENT_GREEN, COLOR_TEXT_PRIMARY, STYLE_INPUT_CYBER)
from custom_components import ProMessageBox

class SettingsPage(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.load_settings()

    def load_data(self):
        """Called by Main Window refresh"""
        self.load_settings()
        self.load_cloud_settings()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Modern Header with Subtitle
        header_container = QVBoxLayout()
        header = QLabel("⚙️ SYSTEM SETTINGS")
        header.setStyleSheet(f"color: {COLOR_ACCENT_CYAN}; font-size: 26px; font-weight: bold; letter-spacing: 3px;")
        header_container.addWidget(header)
        
        subtitle = QLabel("Configure your application preferences")
        subtitle.setStyleSheet("color: #888; font-size: 12px; margin-top: 5px;")
        header_container.addWidget(subtitle)
        
        main_layout.addLayout(header_container)
        
        # Scroll Area for Content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(20)
        
        # --- CARD 1: APPEARANCE SETTINGS ---
        self.create_appearance_card()
        
        # --- CARD 2: BACKUP & RESTORE ---
        self.create_backup_card()
        
        # --- CARD 3: DATA MANAGEMENT ---
        self.create_data_management_card()
        
        # --- CARD 4: NETWORK SETUP ---
        self.create_network_card()
        
        self.content_layout.addStretch()
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # Save Button (Full Width, Green)
        self.btn_save = QPushButton("💾 SAVE ALL SETTINGS")
        self.btn_save.setFixedHeight(55)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLOR_ACCENT_GREEN}, stop:1 #00cc35);
                color: black;
                font-weight: bold;
                border-radius: 8px;
                font-size: 16px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff41, stop:1 {COLOR_ACCENT_GREEN});
            }}
        """)
        self.btn_save.clicked.connect(self.save_settings)
        main_layout.addWidget(self.btn_save)

    def create_card_frame(self, title, icon=""):
        """Create a modern card-style frame"""
        group = QGroupBox(f"{icon} {title}")
        group.setStyleSheet(f"""
            QGroupBox {{
                color: {COLOR_TEXT_PRIMARY};
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #1a1a1a;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(10, 15, 20, 0.8),
                    stop:1 rgba(5, 8, 12, 0.9));
                margin-top: 15px;
                padding: 20px;
                border-radius: 12px;
            }}
            QGroupBox:hover {{
                border-color: rgba(0, 242, 255, 0.3);
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 15px;
                background-color: rgba(0, 242, 255, 0.1);
                border-radius: 6px;
                margin-left: 10px;
            }}
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        return group, layout

    def create_appearance_card(self):
        """Appearance Settings Card"""
        group, layout = self.create_card_frame("APPEARANCE", "🎨")
        
        lbl = QLabel("PDF Invoice Theme:")
        lbl.setStyleSheet("color: #aaa; font-weight: normal;")
        layout.addWidget(lbl)
        
        self.combo_theme = QComboBox()
        self.combo_theme.addItems(["Modern (Blue)", "Executive (Black/Gold)", "Minimal (B&W)", "Logo Adaptive"])
        self.combo_theme.setFixedHeight(40)
        self.combo_theme.setStyleSheet(STYLE_INPUT_CYBER)
        layout.addWidget(self.combo_theme)
        
        info = QLabel("ℹ️ 'Logo Adaptive' extracts colors from your uploaded logo")
        info.setStyleSheet("color: #666; font-size: 10px; font-style: italic; margin-top: 5px;")
        layout.addWidget(info)
        
        self.content_layout.addWidget(group)

    def create_backup_card(self):
        """Backup & Restore Card with Enhanced UI"""
        from backup_manager import BackupManager
        
        self.backup_mgr = BackupManager(self.db_manager.db_name)
        
        group, layout = self.create_card_frame("BACKUP & RESTORE", "💾")
        
        desc = QLabel("Protect your data with automatic backups")
        desc.setStyleSheet("color: #999; font-weight: normal; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Button Row: Backup and Restore side by side
        btn_row = QHBoxLayout()
        btn_row.setSpacing(15)
        
        # Create Backup Button
        btn_backup = QPushButton("📦 CREATE BACKUP")
        btn_backup.setFixedHeight(50)
        btn_backup.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_backup.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 242, 255, 0.15),
                    stop:1 rgba(0, 242, 255, 0.05));
                color: {COLOR_ACCENT_CYAN};
                border: 2px solid {COLOR_ACCENT_CYAN};
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {COLOR_ACCENT_CYAN};
                color: black;
            }}
        """)
        btn_backup.clicked.connect(self.manual_backup)
        btn_row.addWidget(btn_backup)
        
        # Restore Button
        btn_restore = QPushButton("♻️ RESTORE DATA")
        btn_restore.setFixedHeight(50)
        btn_restore.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_restore.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 152, 0, 0.15),
                    stop:1 rgba(255, 152, 0, 0.05));
                color: #ff9800;
                border: 2px solid #ff9800;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: #ff9800;
                color: black;
            }}
        """)
        btn_restore.clicked.connect(self.show_restore_dialog)
        btn_row.addWidget(btn_restore)
        
        layout.addLayout(btn_row)
        
        # Status Label
        self.lbl_backup_status = QLabel("✓ Local backup enabled")
        self.lbl_backup_status.setStyleSheet("color: #00ff41; font-size: 11px; font-style: italic; margin-top: 10px;")
        layout.addWidget(self.lbl_backup_status)
        
        # Cloud Backup Section
        sep = QLabel("─── Cloud Backup ───")
        sep.setStyleSheet("color: #555; margin-top: 20px; margin-bottom: 15px;")
        sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sep)
        
        self.chk_cloud_backup = QCheckBox("☁️ Enable automatic cloud sync")
        self.chk_cloud_backup.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: bold; font-size: 13px;")
        self.chk_cloud_backup.stateChanged.connect(self.on_cloud_backup_toggled)
        layout.addWidget(self.chk_cloud_backup)
        
        # Cloud Path Row
        cloud_row = QHBoxLayout()
        cloud_row.setSpacing(10)
        
        self.lbl_cloud_path = QLabel("Not configured")
        self.lbl_cloud_path.setStyleSheet("""
            color: #888;
            padding: 10px;
            background-color: #0a0a0a;
            border-radius: 6px;
            font-size: 11px;
        """)
        cloud_row.addWidget(self.lbl_cloud_path, 1)
        
        btn_browse = QPushButton("📁 Browse")
        btn_browse.setFixedHeight(38)
        btn_browse.setFixedWidth(100)
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.setStyleSheet(f"""
            QPushButton {{
                background-color: #1a1a1a;
                color: {COLOR_ACCENT_CYAN};
                border: 1px solid #333;
                border-radius: 6px;
                padding: 5px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border-color: {COLOR_ACCENT_CYAN};
                background-color: #252525;
            }}
        """)
        btn_browse.clicked.connect(self.select_cloud_folder)
        cloud_row.addWidget(btn_browse)
        
        layout.addLayout(cloud_row)
        
        self.lbl_cloud_status = QLabel("")
        self.lbl_cloud_status.setStyleSheet("color: #666; font-size: 10px; font-style: italic; margin-top: 5px;")
        layout.addWidget(self.lbl_cloud_status)
        
        info = QLabel("ℹ️ Syncs to: Google Drive, OneDrive, Dropbox, or external drives")
        info.setStyleSheet("color: #666; font-size: 10px; font-style: italic; margin-top: 10px;")
        layout.addWidget(info)
        
        self.content_layout.addWidget(group)
        self.load_cloud_settings()

    def create_data_management_card(self):
        """Data Management Card"""
        group, layout = self.create_card_frame("DATA MANAGEMENT", "🗃️")
        
        desc = QLabel("Advanced data operations")
        desc.setStyleSheet("color: #999; font-weight: normal; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Export Data Button
        btn_export = QPushButton("📤 EXPORT ALL DATA")
        btn_export.setFixedHeight(45)
        btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_export.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0, 200, 100, 0.1);
                color: #00c864;
                border: 1px solid #00c864;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #00c864;
                color: black;
            }}
        """)
        btn_export.clicked.connect(self.export_data)
        layout.addWidget(btn_export)
        
        info = QLabel("ℹ️ Export all inventory, sales, and invoices to Excel")
        info.setStyleSheet("color: #666; font-size: 10px; font-style: italic; margin-top: 5px;")
        layout.addWidget(info)
        
        self.content_layout.addWidget(group)

    def create_network_card(self):
        """Network Setup Card"""
        group, layout = self.create_card_frame("NETWORK DATABASE", "🌐")
        
        desc = QLabel("Multi-computer database sharing setup")
        desc.setStyleSheet("color: #999; font-weight: normal; margin-bottom: 10px;")
        layout.addWidget(desc)
        
        # Current Mode Display
        import db_config
        config = db_config.load_config()
        
        if config:
            mode = config.get("mode", "LOCAL")
            if mode == "SERVER":
                ip = db_config.get_local_ip()
                pc = db_config.get_computer_name()
                mode_text = f"🖥️ SERVER MODE  •  IP: {ip}  •  PC: {pc}"
                mode_color = COLOR_ACCENT_CYAN
            elif mode == "CLIENT":
                server = config.get("server_ip", "?")
                mode_text = f"💻 CLIENT MODE  •  Server: {server}"
                mode_color = COLOR_ACCENT_GREEN
            else:
                mode_text = "📁 LOCAL MODE (Single PC)"
                mode_color = "#888"
        else:
            mode_text = "⚠️ Not configured"
            mode_color = "#ff9800"
        
        self.lbl_network_mode = QLabel(mode_text)
        self.lbl_network_mode.setStyleSheet(f"color: {mode_color}; font-weight: bold; font-size: 13px; padding: 12px; background-color: #0a0a0a; border-radius: 8px; border: 1px solid #222;")
        self.lbl_network_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_network_mode)
        
        btn_network = QPushButton("🔄 RECONFIGURE NETWORK")
        btn_network.setFixedHeight(45)
        btn_network.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_network.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(0, 242, 255, 0.1);
                color: {COLOR_ACCENT_CYAN};
                border: 2px solid {COLOR_ACCENT_CYAN};
                border-radius: 8px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_ACCENT_CYAN}; color: black;
            }}
        """)
        btn_network.clicked.connect(self.open_network_setup)
        layout.addWidget(btn_network)
        
        info = QLabel("ℹ️ Changes take effect after restarting the application")
        info.setStyleSheet("color: #666; font-size: 10px; font-style: italic; margin-top: 5px;")
        layout.addWidget(info)
        
        self.content_layout.addWidget(group)

    def open_network_setup(self):
        """Open Network Setup Dialog from Settings."""
        from network_setup import NetworkSetupDialog
        dlg = NetworkSetupDialog(self)
        if dlg.exec():
            ProMessageBox.information(self, "Network Updated", "Network configuration saved!\n\nPlease restart the application for changes to take effect.")
            # Refresh the label
            import db_config
            config = db_config.load_config()
            if config:
                mode = config.get("mode", "LOCAL")
                if mode == "SERVER":
                    ip = db_config.get_local_ip()
                    self.lbl_network_mode.setText(f"🖥️ SERVER MODE  •  IP: {ip}  •  PC: {db_config.get_computer_name()}")
                    self.lbl_network_mode.setStyleSheet(f"color: {COLOR_ACCENT_CYAN}; font-weight: bold; font-size: 13px; padding: 12px; background-color: #0a0a0a; border-radius: 8px; border: 1px solid #222;")
                elif mode == "CLIENT":
                    server = config.get("server_ip", "?")
                    self.lbl_network_mode.setText(f"💻 CLIENT MODE  •  Server: {server}")
                    self.lbl_network_mode.setStyleSheet(f"color: {COLOR_ACCENT_GREEN}; font-weight: bold; font-size: 13px; padding: 12px; background-color: #0a0a0a; border-radius: 8px; border: 1px solid #222;")

    def show_restore_dialog(self):
        """Show dialog to select and restore backup"""
        dialog = QDialog(self)
        dialog.setWindowTitle("♻️ Restore Backup")
        dialog.setModal(True)
        dialog.setMinimumSize(600, 400)
        dialog.setStyleSheet("background-color: #080a10;")
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Select a backup to restore:")
        title.setStyleSheet(f"color: {COLOR_ACCENT_CYAN}; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # Backup List
        backup_list = QListWidget()
        backup_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #0a0a0a;
                border: 1px solid #333;
                border-radius: 6px;
                color: {COLOR_TEXT_PRIMARY};
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-radius: 4px;
            }}
            QListWidget::item:hover {{
                background-color: rgba(0, 242, 255, 0.1);
            }}
            QListWidget::item:selected {{
                background-color: rgba(0, 242, 255, 0.2);
                border: 1px solid {COLOR_ACCENT_CYAN};
            }}
        """)
        
        # Load available backups
        backups = self.backup_mgr.get_backups()
        if not backups:
            no_backup_item = QListWidgetItem("No backups available")
            no_backup_item.setFlags(Qt.ItemFlag.NoItemFlags)
            backup_list.addItem(no_backup_item)
        else:
            for backup in backups:
                size_mb = backup['size'] / (1024 * 1024)
                item_text = f"📦 {backup['filename']}\n    📅 {backup['date']}  |  💾 {size_mb:.2f} MB"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, backup['filename'])
                backup_list.addItem(item)
        
        layout.addWidget(backup_list)
        
        # Warning
        warning = QLabel("⚠️ WARNING: This will replace your current database. A safety backup will be created first.")
        warning.setStyleSheet("color: #ff9800; font-size: 11px; font-style: italic; padding: 10px; background-color: rgba(255, 152, 0, 0.1); border-radius: 4px;")
        warning.setWordWrap(True)
        layout.addWidget(warning)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        btn_cancel = QPushButton("✖️ Cancel")
        btn_cancel.setFixedHeight(40)
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #333;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_cancel)
        
        btn_restore = QPushButton("♻️ RESTORE SELECTED")
        btn_restore.setFixedHeight(40)
        btn_restore.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_restore.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: black;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ffaa00;
            }
        """)
        btn_restore.clicked.connect(lambda: self.perform_restore(backup_list, dialog))
        btn_layout.addWidget(btn_restore)
        
        layout.addLayout(btn_layout)
        
        dialog.exec()

    def perform_restore(self, backup_list, dialog):
        """Perform the restore operation"""
        selected_items = backup_list.selectedItems()
        if not selected_items:
            ProMessageBox.warning(self, "No Selection", "Please select a backup to restore.")
            return
        
        backup_filename = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # Confirm
        confirm = ProMessageBox.question(
            self,
            "Confirm Restore",
            f"Are you sure you want to restore from:\n\n{backup_filename}\n\nThis will replace all current data!"
        )
        
        if confirm == ProMessageBox.StandardButton.Yes:
            success, msg = self.backup_mgr.restore_backup(backup_filename)
            if success:
                ProMessageBox.information(self, "Restore Complete", f"{msg}\n\nPlease restart the application.")
                dialog.accept()
            else:
                ProMessageBox.critical(self, "Restore Failed", msg)

    def export_data(self):
        """Export all data to Excel"""
        ProMessageBox.information(self, "Coming Soon", "Data export feature will be available in next update!")

    def load_settings(self):
        settings = self.db_manager.get_shop_settings()
        if not settings: return
        
        theme = settings.get('invoice_theme', 'Modern (Blue)')
        index = self.combo_theme.findText(theme)
        if index >= 0:
            self.combo_theme.setCurrentIndex(index)

    def save_settings(self):
        val = self.combo_theme.currentText()
        self.db_manager.update_setting('invoice_theme', val)
        ProMessageBox.information(self, "Saved", "Settings saved successfully!")

    def load_cloud_settings(self):
        """Load cloud backup settings from database"""
        settings = self.db_manager.get_shop_settings()
        
        cloud_enabled = settings.get('backup_cloud_enabled', 'false') == 'true'
        self.chk_cloud_backup.setChecked(cloud_enabled)
        
        cloud_path = settings.get('backup_cloud_path', '')
        if cloud_path:
            self.lbl_cloud_path.setText(cloud_path)
            self.lbl_cloud_path.setStyleSheet("color: #00ff41; padding: 10px; background-color: #0a0a0a; border-radius: 6px; font-size: 11px;")
            
            is_valid, status_msg, _ = self.backup_mgr.get_cloud_backup_status(cloud_path)
            if is_valid:
                self.lbl_cloud_status.setText(f"✓ {status_msg}")
                self.lbl_cloud_status.setStyleSheet("color: #00ff41; font-size: 10px; font-style: italic;")
            else:
                self.lbl_cloud_status.setText(f"⚠ {status_msg}")
                self.lbl_cloud_status.setStyleSheet("color: #ff9800; font-size: 10px; font-style: italic;")

    def on_cloud_backup_toggled(self, state):
        """Handle cloud backup checkbox toggle"""
        enabled = state == Qt.CheckState.Checked.value
        self.db_manager.update_setting('backup_cloud_enabled', 'true' if enabled else 'false')
        
        if enabled:
            self.lbl_backup_status.setText("✓ Local + Cloud backup enabled")
        else:
            self.lbl_backup_status.setText("✓ Local backup enabled")

    def select_cloud_folder(self):
        """Open folder selection dialog for cloud backup"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Cloud Drive Folder for Backups",
            "",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            success, result = self.backup_mgr.set_cloud_backup_path(folder)
            
            if success:
                validated_path = result
                self.db_manager.update_setting('backup_cloud_path', validated_path)
                self.lbl_cloud_path.setText(validated_path)
                self.lbl_cloud_path.setStyleSheet("color: #00ff41; padding: 10px; background-color: #0a0a0a; border-radius: 6px; font-size: 11px;")
                self.lbl_cloud_status.setText("✓ Cloud folder configured successfully")
                self.lbl_cloud_status.setStyleSheet("color: #00ff41; font-size: 10px; font-style: italic;")
                ProMessageBox.information(self, "Success", f"Cloud backup folder set to:\n{validated_path}")
            else:
                ProMessageBox.critical(self, "Error", f"Invalid folder:\n{result}")

    def manual_backup(self):
        """Manual backup trigger with cloud sync"""
        settings = self.db_manager.get_shop_settings()
        cloud_enabled = settings.get('backup_cloud_enabled', 'false') == 'true'
        cloud_path = settings.get('backup_cloud_path', '') if cloud_enabled else None
        
        success, msg = self.backup_mgr.create_backup(cloud_path=cloud_path)
        
        if success:
            ProMessageBox.information(self, "Backup Created", msg)
            self.lbl_backup_status.setText(f"✓ {msg}")
        else:
            ProMessageBox.critical(self, "Backup Failed", msg)
