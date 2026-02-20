from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QPushButton, QFrame, QDateEdit, QDialog, QFormLayout, 
                              QLineEdit, QDialogButtonBox, QAbstractItemView, QTextEdit, QFileDialog, QProgressBar, QGridLayout, QStackedWidget)
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis
from custom_components import ProMessageBox, ProDialog, ReactorStatCard
from return_dialog import ReturnDialog
from PyQt6.QtCore import Qt, QDate, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QLinearGradient, QFont
from styles import (COLOR_ACCENT_CYAN, COLOR_BACKGROUND, COLOR_SURFACE, COLOR_TEXT_PRIMARY, COLOR_ACCENT_GREEN,
                   COLOR_ACCENT_YELLOW, COLOR_ACCENT_RED, STYLE_NEON_BUTTON, STYLE_INPUT_CYBER, STYLE_TABLE_CYBER, STYLE_GLASS_PANEL)
import os
import sys
import shutil
import json
import hashlib
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QInputDialog

class AnimatedStatCard(QFrame):
    """Animated statistics card with glow effect and counting animation"""
    def __init__(self, title, value="0", icon="📊", color=COLOR_ACCENT_CYAN, parent=None):
        super().__init__(parent)
        self.setFixedHeight(120)
        self._current_value = 0
        self._target_value = 0
        self._color = color
        self._is_currency = False
        
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(11, 11, 20, 0.9),
                    stop:1 rgba(20, 20, 35, 0.9));
                border: 2px solid {color};
                border-radius: 12px;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15, 15, 25, 0.95),
                    stop:1 rgba(25, 25, 40, 0.95));
                border: 2px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Icon + Title
        top_row = QHBoxLayout()
        self.lbl_icon = QLabel(icon)
        self.lbl_icon.setStyleSheet(f"font-size: 32px; border: none; background: transparent;")
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet(f"color: #aaa; font-size: 11px; font-weight: bold; border: none; background: transparent;")
        
        top_row.addWidget(self.lbl_icon)
        top_row.addStretch()
        top_row.addWidget(self.lbl_title)
        layout.addLayout(top_row)
        
        # Value
        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: bold; border: none; background: transparent;")
        layout.addWidget(self.lbl_value)
        
        layout.addStretch()
        
        # Animation timer
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._animate_step)
        
    def set_value(self, value, animate=True):
        """Set value with optional animation"""
        # Detect if currency
        if isinstance(value, str) and '₹' in value:
            self._is_currency = True
            # Extract numeric value
            numeric_str = value.replace('₹', '').replace(',', '').strip()
            try:
                self._target_value = float(numeric_str)
            except:
                self.lbl_value.setText(value)
                return
        elif isinstance(value, str) and '%' in value:
            self.lbl_value.setText(value)
            return
        else:
            self._is_currency = False
            try:
                self._target_value = float(str(value).replace(',', ''))
            except:
                self.lbl_value.setText(str(value))
                return
        
        if animate and self._target_value > 0:
            self._current_value = 0
            self.animation_timer.start(20)  # Update every 20ms
        else:
            self._current_value = self._target_value
            self._update_display()
    
    def _animate_step(self):
        """Animate counting up"""
        if self._current_value < self._target_value:
            # Increment by 5% of remaining value or minimum 1
            increment = max(1, (self._target_value - self._current_value) * 0.15)
            self._current_value = min(self._current_value + increment, self._target_value)
            self._update_display()
        else:
            self.animation_timer.stop()
    
    def _update_display(self):
        """Update the displayed value"""
        if self._is_currency:
            self.lbl_value.setText(f"₹ {self._current_value:,.0f}")
        else:
            self.lbl_value.setText(f"{int(self._current_value)}")


class TopPerformerWidget(QFrame):
    """Widget showing top selling parts"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(11, 11, 20, 0.8);
                border: 1px solid #333;
                border-radius: 10px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel("🎯 TOP PERFORMERS")
        header.setStyleSheet(f"color: {COLOR_ACCENT_YELLOW}; font-size: 16px; font-weight: bold; border: none; background: transparent;")
        layout.addWidget(header)
        
        # List container
        self.list_layout = QVBoxLayout()
        layout.addLayout(self.list_layout)
        layout.addStretch()
        
    def set_data(self, top_parts):
        """Display top selling parts with animated bars"""
        # Clear existing
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not top_parts:
            no_data = QLabel("No sales data available")
            no_data.setStyleSheet("color: #666; font-style: italic; border: none; background: transparent;")
            self.list_layout.addWidget(no_data)
            return
        
        max_qty = max([p[2] for p in top_parts]) if top_parts else 1
        
        for idx, (part_id, part_name, qty, revenue) in enumerate(top_parts):
            # Item frame
            item_frame = QFrame()
            item_frame.setStyleSheet("background: transparent; border: none;")
            item_layout = QVBoxLayout(item_frame)
            item_layout.setContentsMargins(0, 5, 0, 5)
            item_layout.setSpacing(3)
            
            # Rank + Name
            rank_colors = ["#FFD700", "#C0C0C0", "#CD7F32", "#00e5ff", "#00e5ff"]
            medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
            
            name_row = QHBoxLayout()
            rank_lbl = QLabel(medals[idx])
            rank_lbl.setStyleSheet(f"font-size: 18px; border: none; background: transparent;")
            
            name_lbl = QLabel(part_name[:30])
            name_lbl.setStyleSheet(f"color: {rank_colors[idx]}; font-weight: bold; font-size: 12px; border: none; background: transparent;")
            
            qty_lbl = QLabel(f"{int(qty)} units")
            qty_lbl.setStyleSheet(f"color: #aaa; font-size: 10px; border: none; background: transparent;")
            
            name_row.addWidget(rank_lbl)
            name_row.addWidget(name_lbl)
            name_row.addStretch()
            name_row.addWidget(qty_lbl)
            item_layout.addLayout(name_row)
            
            # Progress bar
            progress = QProgressBar()
            progress.setRange(0, 100)
            progress.setValue(int((qty / max_qty) * 100))
            progress.setTextVisible(False)
            progress.setFixedHeight(8)
            progress.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #1a1a2e;
                    border: none;
                    border-radius: 4px;
                }}
                QProgressBar::chunk {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {rank_colors[idx]},
                        stop:1 rgba(0, 229, 255, 0.3));
                    border-radius: 4px;
                }}
            """)
            item_layout.addWidget(progress)
            
            self.list_layout.addWidget(item_frame)

class CustomerInsightsWidget(QFrame):
    """Widget showing top customers"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(11, 11, 20, 0.8);
                border: 1px solid #333;
                border-radius: 10px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel("💎 TOP CUSTOMERS")
        header.setStyleSheet(f"color: {COLOR_ACCENT_GREEN}; font-size: 16px; font-weight: bold; border: none; background: transparent;")
        layout.addWidget(header)
        
        # List container
        self.list_layout = QVBoxLayout()
        layout.addLayout(self.list_layout)
        layout.addStretch()
        
    def set_data(self, top_customers):
        """Display top customers"""
        # Clear existing
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if not top_customers:
            no_data = QLabel("No customer data available")
            no_data.setStyleSheet("color: #666; font-style: italic; border: none; background: transparent;")
            self.list_layout.addWidget(no_data)
            return
        
        for idx, (name, purchase_count, total_spent) in enumerate(top_customers):
            # Item frame
            item_frame = QFrame()
            item_frame.setStyleSheet("""
                QFrame {
                    background: rgba(0, 255, 136, 0.05);
                    border: 1px solid rgba(0, 255, 136, 0.2);
                    border-radius: 6px;
                    padding: 8px;
                }
            """)
            item_layout = QHBoxLayout(item_frame)
            item_layout.setContentsMargins(8, 5, 8, 5)
            
            # Rank
            rank_lbl = QLabel(f"#{idx+1}")
            rank_lbl.setStyleSheet(f"color: {COLOR_ACCENT_GREEN}; font-weight: bold; font-size: 14px; border: none; background: transparent;")
            rank_lbl.setFixedWidth(30)
            
            # Name
            name_lbl = QLabel(name[:25])
            name_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 11px; border: none; background: transparent;")
            
            # Stats
            stats_layout = QVBoxLayout()
            stats_layout.setSpacing(2)
            
            spent_lbl = QLabel(f"₹{total_spent:,.0f}")
            spent_lbl.setStyleSheet(f"color: {COLOR_ACCENT_YELLOW}; font-size: 12px; font-weight: bold; border: none; background: transparent;")
            
            orders_lbl = QLabel(f"{purchase_count} orders")
            orders_lbl.setStyleSheet("color: #888; font-size: 9px; border: none; background: transparent;")
            
            stats_layout.addWidget(spent_lbl)
            stats_layout.addWidget(orders_lbl)
            
            item_layout.addWidget(rank_lbl)
            item_layout.addWidget(name_lbl)
            item_layout.addStretch()
            item_layout.addLayout(stats_layout)
            
            self.list_layout.addWidget(item_frame)

class ShopBrandingDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Configure Shop Branding")
        self.setStyleSheet(f"background-color: #050505; color: {COLOR_TEXT_PRIMARY};")
        self.resize(550, 650)
        
        self.logo_path_to_save = None
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20,20,20,20)
        
        # --- Header ---
        self.lbl_title = QLabel("⚙️ SHOP IDENTITY & SETTINGS")
        self.lbl_title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLOR_ACCENT_CYAN}; border-bottom: 2px solid {COLOR_ACCENT_CYAN}; padding-bottom: 10px;")
        layout.addWidget(self.lbl_title)
        
        # --- Logo Section ---
        logo_frame = QFrame()
        logo_frame.setStyleSheet("border: 1px solid #333; border-radius: 8px; padding: 10px; background: #111;")
        logo_layout = QHBoxLayout(logo_frame)
        
        self.logo_preview = QLabel("No Logo")
        self.logo_preview.setFixedSize(160, 90)
        self.logo_preview.setStyleSheet("border: 1px dashed #666; background: #000; color: #aaa;")
        self.logo_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_preview.setScaledContents(True)
        
        btn_upload = QPushButton("🖼️ UPLOAD SHOP LOGO")
        btn_upload.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_upload.setStyleSheet(STYLE_NEON_BUTTON)
        btn_upload.clicked.connect(self.browse_logo)
        
        logo_layout.addWidget(self.logo_preview)
        logo_layout.addWidget(btn_upload)
        layout.addWidget(logo_frame)
        
        # --- Form ---
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        form_layout.setVerticalSpacing(20)
        
        # Load current
        current = self.db_manager.get_shop_settings()
        
        # Name
        self.in_name = QLineEdit(current.get("shop_name", ""))
        self.in_name.setStyleSheet(STYLE_INPUT_CYBER)
        form_layout.addRow("Shop Name:", self.in_name)
        
        # GSTIN
        self.in_gst = QLineEdit(current.get("gstin", ""))
        self.in_gst.setStyleSheet(STYLE_INPUT_CYBER)
        form_layout.addRow("GSTIN No:", self.in_gst)
        
        # Mobile
        self.in_mobile = QLineEdit(current.get("mobile", ""))
        self.in_mobile.setPlaceholderText("e.g. 9800012345, 9900054321")
        self.in_mobile.setStyleSheet(STYLE_INPUT_CYBER)
        form_layout.addRow("Mobile Nos:", self.in_mobile)
        
        # Address (Multi-line)
        self.in_addr = QTextEdit()
        self.in_addr.setPlainText(current.get("address", ""))
        self.in_addr.setFixedHeight(100)
        self.in_addr.setStyleSheet(STYLE_INPUT_CYBER)
        form_layout.addRow("Address:", self.in_addr)
        
        layout.addLayout(form_layout)
        
        # --- Buttons ---
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_save = QPushButton("SAVE CHANGES")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet(f"background-color: {COLOR_ACCENT_CYAN}; color: black; font-weight: bold; padding: 10px 20px; border-radius: 6px;")
        self.btn_save.clicked.connect(self.save_settings)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet("background: transparent; color: white; border: 1px solid #666; padding: 10px 20px; border-radius: 6px;")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(btn_layout)
        
        # --- Factory Reset Link ---
        # A small, less prominent button/link at the bottom
        self.btn_reset = QPushButton("⚠️ Factory Reset System")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #666;
                border: none;
                font-size: 10px;
                text-decoration: underline;
                margin-top: 10px;
            }
            QPushButton:hover {
                color: #ff4444;
            }
        """)
        self.btn_reset.clicked.connect(self.perform_factory_reset)
        layout.addWidget(self.btn_reset, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Load existing
        existing_logo = current.get("logo_path", "")
        if existing_logo and os.path.exists(existing_logo):
            self.logo_preview.setPixmap(QPixmap(existing_logo))
            self.logo_path_to_save = existing_logo 

    def browse_logo(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.jpg *.jpeg)")
        if fname:
            pix = QPixmap(fname)
            self.logo_preview.setPixmap(pix)
            self.logo_path_to_save = fname

    def save_settings(self):
        final_logo_path = os.path.join("logos", "logo.png")
        
        if self.logo_path_to_save and os.path.abspath(self.logo_path_to_save) != os.path.abspath(final_logo_path):
            try:
                if not os.path.exists("logos"):
                    os.makedirs("logos")
                shutil.copy(self.logo_path_to_save, final_logo_path)
            except Exception as e:
                ProMessageBox.warning(self, "Warning", f"Could not save logo file: {e}")

        new_settings = {
            "shop_name": self.in_name.text(),
            "shop_address": self.in_addr.toPlainText(),
            "shop_mobile": self.in_mobile.text(),
            "shop_gstin": self.in_gst.text(),
            "logo_path": final_logo_path 
        }
        
        # Confirm Save
        if not ProMessageBox.question(self, "Confirm Save", "Are you sure you want to update Shop Branding?"):
            return

        success, msg = self.db_manager.update_shop_settings(new_settings)
        if success:
            ProMessageBox.information(self, "Success", "Shop Configuration Updated Successfully!")
            self.accept()
        else:
            ProMessageBox.warning(self, "Error", msg)

    def perform_factory_reset(self):
        # 1. First Warning
        if not ProMessageBox.question(self, "FACTORY RESET", "⚠️ WARNING: This will DELETE ALL DATA.\n\nAre you absolutely sure you want to proceed?"):
            return
            
        # 2. Second Confirmation
        text, ok = QInputDialog.getText(self, "Confirm Reset", "Type 'RESET' to confirm deletion:", QLineEdit.EchoMode.Normal)
        
        if ok and text == "RESET":
            success, msg = self.db_manager.factory_reset()
            if success:
                ProMessageBox.information(self, "System Reset", "System has been reset successfully.\nThe application will now restart/close.")
                import sys
                sys.exit(0)
            else:
                ProMessageBox.critical(self, "Reset Failed", f"Error: {msg}")
        else:
             if ok:
                 ProMessageBox.warning(self, "Cancelled", "Incorrect confirmation text. Reset cancelled.")

class ReportsPage(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # --- Header ---
        header_row = QHBoxLayout()
        # Config Shop Button (Stealth Mode - Top Left)
        self.btn_config = QPushButton("")
        self.btn_config.setFixedSize(50, 40)
        self.btn_config.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_config.setStyleSheet("background: transparent; border: none;")
        self.btn_config.clicked.connect(self.open_config_dialog)
        header_row.addWidget(self.btn_config)

        self.title = QLabel("📊 SALES ANALYTICS & REPORTS")
        self.title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLOR_ACCENT_CYAN};")
        header_row.addWidget(self.title)
        header_row.addStretch()
        layout.addLayout(header_row)
        
        # Toggle Button
        self.btn_view_toggle = QPushButton("📈 INSIGHTS")
        self.btn_view_toggle.setFixedSize(100, 40)
        self.btn_view_toggle.setCheckable(True)
        self.btn_view_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_view_toggle.setStyleSheet(STYLE_NEON_BUTTON)
        self.btn_view_toggle.toggled.connect(self.toggle_view)
        header_row.addWidget(self.btn_view_toggle)
        
        layout.addLayout(header_row)
        
        # --- Top Filter Bar ---
        self.filter_frame = QFrame()
        self.filter_frame.setStyleSheet(STYLE_GLASS_PANEL)
        filter_layout = QHBoxLayout(self.filter_frame)
        filter_layout.setContentsMargins(15, 10, 15, 10)
        
        # Live Search
        self.search_in = QLineEdit()
        self.search_in.setPlaceholderText("🔍 Search Customer, Mobile, or Inv ID...")
        self.search_in.setStyleSheet(STYLE_INPUT_CYBER)
        self.search_in.setFixedWidth(300)
        self.search_in.textChanged.connect(self.load_data)
        
        # Date Pickers
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setStyleSheet(STYLE_INPUT_CYBER)
        self.date_from.setFixedWidth(120)
        self.date_from.dateChanged.connect(self.load_data)
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setStyleSheet(STYLE_INPUT_CYBER)
        self.date_to.setFixedWidth(120)
        self.date_to.dateChanged.connect(self.load_data)
        
        # Refresh Button
        btn_refresh = QPushButton("🔄 REFRESH")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(STYLE_NEON_BUTTON)
        btn_refresh.clicked.connect(self.load_data)
        
        # Export Button
        btn_export = QPushButton("📥 EXPORT")
        btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_export.setStyleSheet(f"color: {COLOR_ACCENT_GREEN}; border: 1px solid {COLOR_ACCENT_GREEN}; border-radius: 4px; padding: 5px 15px; font-weight: bold;")
        btn_export.clicked.connect(self.export_to_excel)

        self.lbl_search = QLabel("Search:")
        filter_layout.addWidget(self.lbl_search)
        filter_layout.addWidget(self.search_in)
        filter_layout.addSpacing(20)
        filter_layout.addWidget(QLabel("From:"))
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel("To:"))
        filter_layout.addWidget(self.date_to)
        filter_layout.addWidget(btn_refresh)
        filter_layout.addStretch()
        filter_layout.addWidget(btn_export)
        
        layout.addWidget(self.filter_frame)
        
        # --- Content Stack ---
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        # PAGE 0: Table View
        self.page_table = QWidget()
        page_table_layout = QVBoxLayout(self.page_table)
        page_table_layout.setContentsMargins(0, 0, 0, 0)
        
        # --- Smart Table ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        # DATE, INVOICE ID, CUSTOMER, ITEMS, AMOUNT, ACTION
        self.table.setHorizontalHeaderLabels(["DATE", "INVOICE ID", "CUSTOMER", "ITEMS", "AMOUNT", "ACTION"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents) # Date
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) # Items
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed) # Action
        self.table.setColumnWidth(5, 120)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setStyleSheet(STYLE_TABLE_CYBER)
        page_table_layout.addWidget(self.table)
        
        # --- Bottom Analytics Bar ---
        analytics_frame = QFrame()
        analytics_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(0, 0, 0, 0.6);
                border-top: 2px solid {COLOR_ACCENT_CYAN};
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }}
        """)
        an_layout = QHBoxLayout(analytics_frame)
        an_layout.setContentsMargins(20, 15, 20, 15)
        
        self.lbl_total_rev = QLabel("TOTAL REVENUE: ₹ 0.00")
        self.lbl_total_rev.setStyleSheet(f"color: {COLOR_ACCENT_YELLOW}; font-size: 18px; font-weight: bold;")
        
        self.lbl_total_count = QLabel("TOTAL INVOICES: 0")
        self.lbl_total_count.setStyleSheet(f"color: {COLOR_ACCENT_CYAN}; font-size: 18px; font-weight: bold;")
        
        an_layout.addWidget(self.lbl_total_rev)
        an_layout.addStretch()
        an_layout.addWidget(self.lbl_total_count)
        
        page_table_layout.addWidget(analytics_frame)
        
        self.stack.addWidget(self.page_table)
        
        # PAGE 1: Dashboard
        self.setup_dashboard_ui()

    def setup_dashboard_ui(self):
        self.page_dashboard = QWidget()
        dash_layout = QVBoxLayout(self.page_dashboard)
        dash_layout.setContentsMargins(0,0,0,0)
        
        # 1. Top Cards
        cards_layout = QHBoxLayout()
        self.card_revenue = AnimatedStatCard("TOTAL REVENUE", "₹ 0", "💰", COLOR_ACCENT_YELLOW)
        self.card_orders = AnimatedStatCard("TOTAL ORDERS", "0", "📦", COLOR_ACCENT_CYAN)
        self.card_top_item = AnimatedStatCard("TOP ITEM", "-", "🔥", COLOR_ACCENT_RED)
        
        cards_layout.addWidget(self.card_revenue)
        cards_layout.addWidget(self.card_orders)
        cards_layout.addWidget(self.card_top_item)
        dash_layout.addLayout(cards_layout)
        
        # 2. Insights Split
        split_layout = QHBoxLayout()
        
        # Left: Top Parts
        self.widget_top_parts = TopPerformerWidget()
        split_layout.addWidget(self.widget_top_parts, 1)
        
        # Right: Top Customers
        self.widget_top_customers = CustomerInsightsWidget()
        split_layout.addWidget(self.widget_top_customers, 1)
        
        dash_layout.addLayout(split_layout)
        self.stack.addWidget(self.page_dashboard)
        
    def toggle_view(self, checked):
        if checked:
            self.btn_view_toggle.setText("📋 LIST")
            self.stack.setCurrentIndex(1)
            # Hide Search
            self.search_in.setVisible(False)
            self.lbl_search.setVisible(False)
            self.load_dashboard_data()
        else:
            self.btn_view_toggle.setText("📈 INSIGHTS")
            self.stack.setCurrentIndex(0)
            # Show Search
            self.search_in.setVisible(True)
            self.lbl_search.setVisible(True)

    def load_dashboard_data(self):
        # Load stats for dashboard
        d_from = self.date_from.date().toString("yyyy-MM-dd")
        d_to = self.date_to.date().toString("yyyy-MM-dd")
        
        # 1. Stats
        stats = self.db_manager.get_sales_statistics(d_from, d_to)
        # stats: (total_invoices, total_revenue, avg, max, min)
        if stats:
             rev = stats[1] if stats[1] else 0
             orders = stats[0] if stats[0] else 0
             
             self.card_revenue.set_value(f"₹ {rev:,.0f}")
             self.card_orders.set_value(str(orders))
        
        # 2. Top Parts
        # get_top_selling_parts(date_from, date_to, limit)
        top_parts = self.db_manager.get_top_selling_parts(d_from, d_to, 5)
        self.widget_top_parts.set_data(top_parts)
        
        if top_parts:
             # Set top item card
             best = top_parts[0] # (id, name, qty, rev)
             name = best[1] if best[1] else "Unknown"
             self.card_top_item.set_value(str(name)[:15]) # Short name
        else:
             self.card_top_item.set_value("-")

        # 3. Top Customers
        top_customers = self.db_manager.get_top_customers(d_from, d_to, 5)
        self.widget_top_customers.set_data(top_customers)

    def load_data(self):
        # Update Dashboard if active
        if self.stack.currentIndex() == 1:
            self.load_dashboard_data()
            
        d_from = self.date_from.date().toString("yyyy-MM-dd")
        d_to = self.date_to.date().toString("yyyy-MM-dd")
        query = self.search_in.text().strip()
        
        # Fetch Data: (date, invoice_id, customer_name, items_count, total_amount, invoice_id)
        rows = self.db_manager.get_sales_report(d_from, d_to, query)
        
        self.table.setRowCount(0)
        
        total_rev = 0.0
        
        for i, row in enumerate(rows):
            self.table.insertRow(i)
            
            # Check Return Status (index 7: return_count)
            has_return = False
            if len(row) > 7 and row[7] > 0:
                has_return = True
                
            # Helper to create item with conditional styling
            def create_item(text, is_return=False):
                item = QTableWidgetItem(str(text))
                if is_return:
                    item.setForeground(QColor("#ff4444")) # Red Text
                    font = item.font()
                    font.setStrikeOut(True)
                    # item.setFont(font) # Optional Strikethrough? Maybe just red is better
                return item

            # 0: Date
            self.table.setItem(i, 0, create_item(row[0], has_return))
            
            # 1: Inv ID
            inv_text = str(row[1])
            if has_return: inv_text += " (RET)"
            self.table.setItem(i, 1, create_item(inv_text, has_return))
            
            # 2: Customer
            cust_item = create_item(row[2], has_return)
            cust_item.setToolTip(str(row[2]))
            self.table.setItem(i, 2, cust_item)
            
            # 3: Items
            self.table.setItem(i, 3, create_item(row[3], has_return))
            
            # 4: Amount
            amt = row[4] if row[4] else 0.0
            total_rev += amt
            item_amt = create_item(f"₹ {amt:,.2f}", has_return)
            item_amt.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 4, item_amt)
            
            # 5: Action (View PDF)
            container = QWidget()
            clayout = QHBoxLayout(container)
            clayout.setContentsMargins(2, 2, 2, 2)
            clayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            btn_view = QPushButton("📄")
            btn_view.setFixedSize(34, 28)
            btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_view.setToolTip("Open Invoice PDF")
            btn_view.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(0, 242, 255, 0.1);
                    color: {COLOR_ACCENT_CYAN};
                    border: 1px solid {COLOR_ACCENT_CYAN};
                    border-radius: 4px;
                    padding: 0px;
                    text-align: center;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background-color: {COLOR_ACCENT_CYAN};
                    color: black;
                }}
            """)
            # Use row[1] (Invoice ID)
            btn_view.clicked.connect(lambda _, inv=row[1]: self.open_pdf(inv))
            
            # Determine Action Button
            if has_return:
                # Show a "Glow Up" Icon instead of text
                lbl_ret = QLabel("↩️")
                lbl_ret.setToolTip("Returned")
                # Neon Green Glow Style
                lbl_ret.setStyleSheet("color: #00ff00; font-size: 20px; font-weight: bold; border: none; background: transparent;")
                lbl_ret.setAlignment(Qt.AlignmentFlag.AlignCenter)
                clayout.addWidget(lbl_ret)
            else:
                btn_return = QPushButton("↩️")
                btn_return.setFixedSize(34, 28)
                btn_return.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_return.setToolTip("Process Return")
                btn_return.setStyleSheet(f"""
                    QPushButton {{
                        background-color: rgba(255, 68, 68, 0.1);
                        color: #ff4444;
                        border: 1px solid #ff4444;
                        border-radius: 4px;
                        padding: 0px;
                        text-align: center;
                        font-size: 16px;
                    }}
                    QPushButton:hover {{
                        background-color: #ff4444;
                        color: white;
                    }}
                """)
                btn_return.clicked.connect(lambda _, inv=row[1]: self.open_return_dialog(inv))
                clayout.addWidget(btn_return)
            
            clayout.addWidget(btn_view) # View PDF always available
            # clayout.addWidget(btn_return) # Moved inside else block above
            
            self.table.setCellWidget(i, 5, container)
            
        # Update Analytics
        self.lbl_total_rev.setText(f"TOTAL REVENUE: ₹ {total_rev:,.2f}")
        self.lbl_total_count.setText(f"TOTAL INVOICES: {len(rows)}")

    def open_pdf(self, invoice_id):
        # Logic from billing logic
        # Try invoices folder
        base_dir = os.getcwd()
        pdf_path = os.path.join(base_dir, "invoices", f"{invoice_id}.pdf")
        
        if os.path.exists(pdf_path):
            try:
                os.startfile(pdf_path)
            except Exception as e:
                ProMessageBox.warning(self, "Error", f"Could not open PDF: {e}")
        else:
            ProMessageBox.warning(self, "Not Found", f"Invoice PDF not found:\n{pdf_path}")

    def open_return_dialog(self, invoice_id):
        """Open the return dialog for the selected invoice"""
        dialog = ReturnDialog(self.db_manager, invoice_id, self)
        if dialog.exec():
            # Refresh data if return was processed
            self.load_data()

    def export_to_excel(self):
        # Allow exporting the currently filtered view
        d_from = self.date_from.date().toString("yyyy-MM-dd")
        d_to = self.date_to.date().toString("yyyy-MM-dd")
        query = self.search_in.text().strip()
        
        rows = self.db_manager.get_sales_report(d_from, d_to, query)
        
        if not rows:
            ProMessageBox.information(self, "Empty", "No data to export.")
            return

        try:
            import pandas as pd
            # Columns: date, invoice_id, customer_name, items_count, total_amount, json_items, invoice_id
            data = []
            for r in rows:
                json_str = r[5]
                items_cnt = r[3]
                labour_charge = 0.0
                
                try:
                    items_data = json.loads(json_str)
                    # Support both list and dict-with-cart formats
                    cart = []
                    if isinstance(items_data, list):
                        cart = items_data
                    elif isinstance(items_data, dict):
                        cart = items_data.get('cart', [])
                    
                    # Recalculate items count if it's 0 (historical data)
                    calc_cnt = sum(item.get('qty', 0) for item in cart)
                    if items_cnt == 0:
                         items_cnt = calc_cnt
                    
                    # Calculate Labour Charge: items with 'SERVICE' or 'LABOUR' in name
                    for x in cart:
                        nm = str(x.get('name', '')).upper()
                        if "SERVICE" in nm or "LABOUR" in nm:
                            labour_charge += x.get('total', 0.0)
                            
                except:
                    pass # Fallback to original values if JSON fails
                
                data.append({
                    "Date": r[0],
                    "Invoice ID": r[1],
                    "Customer": r[2],
                    "Items Count": items_cnt,
                    "Labour Charge": labour_charge,
                    "Total Amount": r[4]
                })
            
            df = pd.DataFrame(data)
            
            fname, _ = QFileDialog.getSaveFileName(self, "Export Sales Report", f"Sales_Report_{d_from}_to_{d_to}.xlsx", "Excel Files (*.xlsx)")
            if fname:
                df.to_excel(fname, index=False)
                ProMessageBox.information(self, "Success", f"Exported {len(rows)} records to Excel.")
                
        except Exception as e:
            ProMessageBox.critical(self, "Export Error", str(e))

    def open_config_dialog(self):
        # Re-use existing config dialog logic or simplified
        # For brevity, implementing the password check and dialog open
        dialog = QDialog(self)
        # 1. Ask for Password - Securely
        text, ok = QInputDialog.getText(self, "Security Check", "Enter Admin Password:", QLineEdit.EchoMode.Password)
        
        if ok and text:
            # 2. Hash Input
            input_hash = hashlib.sha256(text.encode()).hexdigest()
            # Hash for 'Chandni@96'
            TARGET_HASH = "c08d268b730facf88cbbb892a25fc697f384a06f854114fd6310ca8f0cc6f6cd"
            
            if input_hash == TARGET_HASH:
                dlg = ShopBrandingDialog(self.db_manager, self)
                if dlg.exec():
                    self.load_data() # Refresh if needed
            else:
                ProMessageBox.warning(self, "Access Denied", "Incorrect Password!")
