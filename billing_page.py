from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, 
                             QCompleter, QDialog, QScrollArea, QAbstractItemView, QFormLayout, QInputDialog,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QStringListModel, QTimer
from PyQt6.QtGui import QColor, QBrush, QStandardItemModel, QStandardItem, QDoubleValidator
from billing_animations import AnimatedLabel, PulseEffect, FlashEffect, ScalePulse
from styles import (COLOR_SURFACE, COLOR_ACCENT_CYAN, COLOR_ACCENT_GREEN, COLOR_ACCENT_YELLOW, COLOR_TEXT_PRIMARY, 
                   STYLE_GLASS_PANEL, STYLE_NEON_BUTTON, STYLE_INPUT_CYBER, STYLE_TABLE_CYBER, 
                   STYLE_LCD_DISPLAY, STYLE_DIGITAL_LABEL, STYLE_GLASS_SIDEBAR, STYLE_HEADER_ACCENT,
                   DIM_BUTTON_HEIGHT, DIM_INPUT_HEIGHT, DIM_MARGIN_STD, DIM_SPACING_STD, DIM_ICON_SIZE)
from invoice_generator import InvoiceGenerator
import datetime
from whatsapp_helper import send_invoice_msg
from custom_components import ProMessageBox, ProDialog
from logger import app_logger
import json
import os

class BillingPage(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.pdf_generator = InvoiceGenerator(db_manager)
        self.cart_items = []
        self.setup_ui()
        self.load_saved_fields()  # Restore persistent custom fields
        
    def showEvent(self, event):
        self.update_completer()
        self.search_bar.setFocus()  # Auto-focus for instant scanning
        super().showEvent(event)

    def resizeEvent(self, event):
        # Dynamic Font Scaling for Grand Total - Optimized to prevent overlap
        if hasattr(self, 'lbl_grand_total'):
             if self.width() < 1200:
                self.lbl_grand_total.setStyleSheet(f"color: {COLOR_ACCENT_GREEN}; font-size: 22pt; font-weight: 900; font-family: Segoe UI;")
             else:
                self.lbl_grand_total.setStyleSheet(f"color: {COLOR_ACCENT_GREEN}; font-size: 28pt; font-weight: 900; font-family: Segoe UI;")
        super().resizeEvent(event)

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(DIM_SPACING_STD + 10)
        main_layout.setContentsMargins(DIM_MARGIN_STD, DIM_MARGIN_STD, DIM_MARGIN_STD, DIM_MARGIN_STD)

        # --- LEFT PANEL (Glassmorphism) ---
        # --- LEFT PANEL (Glassmorphism) ---
        left_panel = QFrame()
        left_panel.setStyleSheet(STYLE_GLASS_SIDEBAR)
        left_panel.setMinimumWidth(280) # Responsive Sidebar
        
        # Main Layout for Left Panel (contains ScrollArea)
        left_main_layout = QVBoxLayout(left_panel)
        left_main_layout.setContentsMargins(0, 0, 0, 0)
        left_main_layout.setSpacing(0)

        # Scroll Area Setup
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background: transparent; border: none;") # Transparent ScrollArea
        
        # Scroll Content Widget (The actual container for widgets)
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        
        # Layout for Scroll Content
        left_layout = QVBoxLayout(scroll_content)
        left_layout.setSpacing(20)
        left_layout.setContentsMargins(25, 25, 25, 25)
        
        # --- Add Widgets to scroll_content (left_layout) ---
        
        # Part Search Header
        lbl_search = QLabel("🔍 PART SEARCH")
        lbl_search.setStyleSheet(f"color: {COLOR_ACCENT_CYAN}; font-weight: bold; font-size: 14px; letter-spacing: 1px; border: none;")
        left_layout.addWidget(lbl_search)
        
        # Scanned Accent Line
        line_search = QFrame()
        line_search.setStyleSheet(STYLE_HEADER_ACCENT)
        left_layout.addWidget(line_search)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("🔍 Scan/Type + ENTER to add instantly...")
        self.search_bar.setFixedHeight(DIM_INPUT_HEIGHT)
        self.search_bar.setStyleSheet(STYLE_INPUT_CYBER)
        self.search_bar.returnPressed.connect(self.add_to_cart_from_search)  # Auto-add on Enter
        left_layout.addWidget(self.search_bar)
        
        self.btn_add_manual = QPushButton("➕ ADD TO COCKPIT")
        self.btn_add_manual.setFixedHeight(DIM_BUTTON_HEIGHT)
        self.btn_add_manual.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_manual.setStyleSheet(STYLE_NEON_BUTTON)
        self.btn_add_manual.clicked.connect(self.add_to_cart_from_search)
        left_layout.addWidget(self.btn_add_manual)
        
        # Customer Info Header
        lbl_cust = QLabel("👤 CUSTOMER INFO")
        lbl_cust.setStyleSheet(f"color: {COLOR_ACCENT_CYAN}; font-weight: bold; font-size: 14px; border: none; margin-top: 15px;")
        left_layout.addWidget(lbl_cust)
        
        # Scanned Accent Line
        line_cust = QFrame()
        line_cust.setStyleSheet(STYLE_HEADER_ACCENT)
        left_layout.addWidget(line_cust)
        
        self.in_cust_name = QLineEdit()
        self.in_cust_name.setPlaceholderText("Customer Name")
        self.in_cust_name.setFixedHeight(DIM_INPUT_HEIGHT)
        self.in_cust_name.setStyleSheet(STYLE_INPUT_CYBER)
        left_layout.addWidget(self.in_cust_name)
        
        self.in_mobile = QLineEdit()
        self.in_mobile.setPlaceholderText("Mobile Number")
        self.in_mobile.setFixedHeight(DIM_INPUT_HEIGHT)
        self.in_mobile.setStyleSheet(STYLE_INPUT_CYBER)
        self.in_mobile.textChanged.connect(self.check_customer_history)
        left_layout.addWidget(self.in_mobile)

        # Dynamic HUD (Hidden by default)
        self.hud_container = QWidget()
        self.hud_layout = QVBoxLayout(self.hud_container)
        self.hud_layout.setContentsMargins(0, 0, 0, 0)
        self.hud_layout.setSpacing(5)
        
        self.lbl_last_visit = QLabel("")
        self.lbl_last_visit.setStyleSheet("color: #888; font-size: 11px; font-family: Consolas;")
        self.hud_layout.addWidget(self.lbl_last_visit)
        
        self.lbl_fav_part = QLabel("")
        self.lbl_fav_part.setStyleSheet("color: #888; font-size: 11px; font-family: Consolas;")
        self.hud_layout.addWidget(self.lbl_fav_part)
        
        self.hud_container.setVisible(False)
        left_layout.addWidget(self.hud_container)

        self.in_vehicle = QLineEdit()
        self.in_vehicle.setPlaceholderText("Vehicle Model")
        self.in_vehicle.setFixedHeight(DIM_INPUT_HEIGHT)
        self.in_vehicle.setStyleSheet(STYLE_INPUT_CYBER)
        left_layout.addWidget(self.in_vehicle)

        self.in_reg_no = QLineEdit()
        self.in_reg_no.setPlaceholderText("Reg No")
        self.in_reg_no.setFixedHeight(DIM_INPUT_HEIGHT)
        self.in_reg_no.setStyleSheet(STYLE_INPUT_CYBER)
        left_layout.addWidget(self.in_reg_no)
        
        # Dynamic Fields Container
        self.dynamic_fields = [] # List of (field_name, input_widget, row_widget)
        self.dynamic_container = QVBoxLayout()
        left_layout.addLayout(self.dynamic_container)
        
        # Add Detail Button
        btn_add_detail = QPushButton("➕ ADD EXTRA DETAIL")
        btn_add_detail.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_detail.setStyleSheet("background-color: transparent; color: #00e5ff; border: 1px dashed #00e5ff; padding: 5px; border-radius: 4px;")
        btn_add_detail.clicked.connect(self.add_dynamic_field)
        left_layout.addWidget(btn_add_detail)
        
        left_layout.addStretch()
        
        # Finalize Scroll Area
        scroll_area.setWidget(scroll_content)
        left_main_layout.addWidget(scroll_area)
        
        main_layout.addWidget(left_panel, 25) 

        # --- RIGHT PANEL ---
        right_panel = QFrame()
        right_panel.setStyleSheet(STYLE_GLASS_PANEL)
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(0)
        
        content_widget = QWidget()
        # Ensure inner widget has transparent background to show glass effect
        content_widget.setStyleSheet("background: transparent; border: none;") 
        right_layout = QVBoxLayout(content_widget)
        right_layout.setContentsMargins(25, 25, 25, 25)
        right_layout.setSpacing(20)
        
        # Table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(7)
        self.cart_table.setHorizontalHeaderLabels(["ID", "NAME", "PRICE", "REMAIN", "QTY", "TOTAL", "ACTION"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.horizontalHeader().setMinimumSectionSize(80) # Prevent collapse
        self.cart_table.setStyleSheet(STYLE_TABLE_CYBER)
        self.cart_table.verticalHeader().setVisible(False)
        self.cart_table.setShowGrid(True) # Explicit Grid
        right_layout.addWidget(self.cart_table)
        
        # --- SUMMARY SECTION (Card-Container Architecture) ---
        summary_container = QWidget()
        summary_layout = QVBoxLayout(summary_container)
        summary_layout.setContentsMargins(0, 10, 0, 0)
        summary_layout.setSpacing(10)
        
        # ROW 1: Cards & Grand Total
        cards_row = QHBoxLayout()
        cards_row.setContentsMargins(10, 5, 10, 5)
        cards_row.setSpacing(15)
        
        # Helper for Fluid Cards
        def create_card(title, value_widget, border_color="#333", text_color="white", bg_color="rgba(20, 20, 30, 0.6)"):
            card = QFrame()
            # Compact & Responsive Constraints
            card.setMinimumWidth(110)
            card.setMaximumWidth(180)
            card.setFixedHeight(70)
            
            # Modern Tech/Glass Styling
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {bg_color}; 
                    border: 1px solid {border_color}; 
                    border-radius: 12px;
                }}
                QFrame:hover {{
                    border: 1px solid {text_color};
                    background-color: rgba(40, 40, 60, 0.7);
                }}
            """)
            l = QVBoxLayout(card)
            l.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.setContentsMargins(5, 5, 5, 5)
            
            lbl = QLabel(title)
            lbl.setStyleSheet("color: #aaa; font-size: 9px; font-weight: bold; font-family: 'Segoe UI'; letter-spacing: 1px; text-transform: uppercase;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
            l.addWidget(lbl)
            
            # LCD/Digital Look
            value_widget.setStyleSheet(f"""
                color: {text_color}; 
                font-size: 16pt;  
                font-family: 'Segoe UI', sans-serif; 
                font-weight: bold; 
                border: none; 
                background: transparent;
            """)
            value_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            l.addWidget(value_widget)
            return card

        # Card 0: Parts Count (Purple/Magenta with Animation)
        self.lbl_parts_count = AnimatedLabel("0")
        self.card_parts = create_card("PARTS", self.lbl_parts_count, "#9C27B0", "#E1BEE7", "#1a0a1a")
        cards_row.addWidget(self.card_parts)
        
        # Card 0.5: Items Count (Orange with Animation)
        self.lbl_items_count = AnimatedLabel("0")
        self.card_items = create_card("ITEMS", self.lbl_items_count, "#FF6F00", "#FFB74D", "#1a0f00")
        cards_row.addWidget(self.card_items)

        # Card 1: Sub-Total (Deep Blue & Cyan with Animation)
        self.lbl_subtotal = AnimatedLabel("0.00")
        self.card_subtotal = create_card("SUB-TOTAL (₹)", self.lbl_subtotal, "#1A4FA1", "#00e5ff", "#08081a") 
        cards_row.addWidget(self.card_subtotal)
        
        # Card 2: Discount % (Black & Amber)
        self.in_discount_pct = QLineEdit("0")
        self.in_discount_pct.setValidator(QDoubleValidator(0.0, 100.0, 2))
        self.in_discount_pct.textChanged.connect(self.calculate_totals)
        self.in_discount_pct.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_disc = create_card("DISCOUNT (%)", self.in_discount_pct, "#f1c40f", "#f1c40f", "black") 
        cards_row.addWidget(card_disc)
        
        # Card 3: Savings (Dark Green & Pulse Green with Animation)
        self.lbl_savings = AnimatedLabel("0.00")
        self.card_savings = create_card("SAVINGS (₹)", self.lbl_savings, COLOR_ACCENT_GREEN, "#00ff41", "#051a05")
        cards_row.addWidget(self.card_savings)
        
        # Stretch Factor to push Grand Total to right
        cards_row.addStretch(1)
        
        # Grand Total Section (Far Right with Glow)
        gt_layout = QVBoxLayout()
        gt_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        lbl_gt_title = QLabel("TOTAL TO PAY")
        lbl_gt_title.setStyleSheet("color: white; font-size: 10pt; font-weight: bold; letter-spacing: 2px;")
        lbl_gt_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        gt_layout.addWidget(lbl_gt_title)
        
        self.lbl_grand_total = QLabel("₹ 0.00")
        # Optimized Glow Effect & Size
        self.lbl_grand_total.setStyleSheet(f"color: {COLOR_ACCENT_GREEN}; font-size: 28pt; font-weight: 900; font-family: Segoe UI;")
        self.lbl_grand_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        gt_glow = QGraphicsDropShadowEffect()
        gt_glow.setBlurRadius(20)
        gt_glow.setColor(QColor("#00ff00"))
        gt_glow.setOffset(0, 0)
        self.lbl_grand_total.setGraphicsEffect(gt_glow)
        
        gt_layout.addWidget(self.lbl_grand_total)
        
        cards_row.addLayout(gt_layout)
        summary_layout.addLayout(cards_row)
        
        # ROW 2: Actions
        actions_row = QHBoxLayout()
        actions_row.setSpacing(15)
        # actions_row.setAlignment(Qt.AlignmentFlag.AlignRight) # Standardize stretch?
        
        # Generate Invoice (Cyan)
        self.btn_checkout = QPushButton("GENERATE INVOICE")
        self.btn_checkout.setFixedHeight(50) # Keep large
        self.btn_checkout.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_checkout.setStyleSheet(f"""
            QPushButton {{
                 background-color: #0b0b14; 
                 color: {COLOR_ACCENT_CYAN}; 
                 font-weight: bold; 
                 border: 2px solid {COLOR_ACCENT_CYAN};
                 border-radius: 8px;
                 font-size: 14px;
            }}
            QPushButton:hover {{ 
                background-color: {COLOR_ACCENT_CYAN}; 
                color: black;
            }}
        """)
        self.btn_checkout.clicked.connect(lambda: self.generate_invoice(silent=False))
        
        # drop shadow effects cannot be shared, create new ones
        glow_c = QGraphicsDropShadowEffect()
        glow_c.setBlurRadius(25)
        glow_c.setColor(QColor(COLOR_ACCENT_CYAN))
        glow_c.setOffset(0,0)
        self.btn_checkout.setGraphicsEffect(glow_c)
        actions_row.addWidget(self.btn_checkout)
        
        # WhatsApp (Green)
        self.btn_whatsapp = QPushButton("GENERATE & WHATSAPP")
        self.btn_whatsapp.setFixedHeight(50) 
        self.btn_whatsapp.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_whatsapp.setStyleSheet(f"""
            QPushButton {{
                 background-color: #0b0b14; 
                 color: {COLOR_ACCENT_GREEN}; 
                 font-weight: bold; 
                 border: 2px solid {COLOR_ACCENT_GREEN};
                 border-radius: 8px;
                 font-size: 14px;
            }}
            QPushButton:hover {{ 
                background-color: {COLOR_ACCENT_GREEN}; 
                color: black;
            }}
        """)
        self.btn_whatsapp.clicked.connect(self.send_whatsapp)
        
        glow_g = QGraphicsDropShadowEffect()
        glow_g.setBlurRadius(25)
        glow_g.setColor(QColor(COLOR_ACCENT_GREEN))
        glow_g.setOffset(0,0)
        self.btn_whatsapp.setGraphicsEffect(glow_g)
        actions_row.addWidget(self.btn_whatsapp)
        
        summary_layout.addLayout(actions_row)
        right_layout.addWidget(summary_container)
        right_panel_layout.addWidget(content_widget)
        main_layout.addWidget(right_panel, 70) 
        
        self.setup_completer()

    def setup_completer(self):
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        
        popup = self.completer.popup()
        popup.setStyleSheet(f"""
            QAbstractItemView {{
                background-color: #121212;
                color: {COLOR_ACCENT_CYAN};
                border: 1px solid #444;
            }}
        """)
        self.search_bar.setCompleter(self.completer)

    def update_completer(self):
        try:
            parts = self.db_manager.get_all_parts()
            model = QStandardItemModel()
            
            for p in parts:
                # p[0]=id, p[1]=name, p[4]=stock
                display_text = f"{p[1]} ({p[0]})"
                item = QStandardItem(display_text)
                
                # Stock Check for Red Color
                if p[4] < 1:
                   item.setForeground(QBrush(QColor("#ff4444")))
                
                model.appendRow(item)
                
            self.completer.setModel(model)
        except Exception as e:
            app_logger.error(f"Error updating completer: {e}")

    def add_to_cart_from_search(self):
        text = self.search_bar.text().strip()
        if not text: return
        
        # Fast parsing - extract Part ID
        if "(" in text and text.endswith(")"):
            part_id = text.split("(")[-1].strip(")")
        else:
            part_id = text
            
        # REAL-TIME STOCK FETCH
        try:
            part = self.db_manager.get_part_by_id(part_id)
            if part:
                self.add_item_to_cart(part)
                self.search_bar.clear()
                self.search_bar.setFocus()  # Keep focus for rapid entry
            else:
                ProMessageBox.warning(self, "Not Found", f"Part ID '{part_id}' not found!")
                self.search_bar.selectAll()  # Select all for easy re-entry
        except Exception as e:
            app_logger.error(f"Error adding to cart from search: {e}")
            self.search_bar.selectAll()

    def add_item_to_cart(self, part):
        db_stock = part[4]
        
        found_item = None
        for item in self.cart_items:
            if item['sys_id'] == part[0]:
                found_item = item
                break
        
        current_cart_qty = found_item['qty'] if found_item else 0
        
        if db_stock <= current_cart_qty:
             ProMessageBox.warning(self, "Out of Stock", f"Only {db_stock} items available!")
             return

        if found_item:
            # DUPLICATE DETECTED - Ask for confirmation
            msg = f"'{part[1]}' is already in cart (Qty: {found_item['qty']})\n\nAdd 1 more?"
            if ProMessageBox.question(self, "⚠️ Already in Cart", msg):
                found_item['qty'] += 1
                found_item['total'] = found_item['qty'] * found_item['price']
                found_item['db_stock'] = db_stock
                self.refresh_cart()
        else:
            self.cart_items.append({
                'sys_id': part[0],
                'name': part[1],
                'price': part[3],
                'db_stock': db_stock,
                'qty': 1,
                'total': part[3]
            })
            # FLASH EFFECT for new item added!
            FlashEffect.flash(self.cart_table, "#00ff41", 1)
            self.refresh_cart()
        
    def remove_cart_item(self, index):
        if 0 <= index < len(self.cart_items):
            item_name = self.cart_items[index]['name']
            
            if ProMessageBox.question(self, "CONFIRM DELETE", f"Remove '{item_name}'?"):
                self.cart_items.pop(index)
                self.refresh_cart()

    def edit_cart_item(self, index):
        if not (0 <= index < len(self.cart_items)): return
        
        item = self.cart_items[index]
        current_qty = item['qty']
        max_stock = item['db_stock']
        
        # ProDialog for Editing
        dialog = ProDialog(self, title="EDIT QUANTITY", width=300, height=180)
        
        lbl = QLabel(f"Set Quantity for: {item['name']}")
        lbl.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        dialog.set_content(lbl)
        
        qty_in = QLineEdit(str(current_qty))
        qty_in.setStyleSheet(STYLE_INPUT_CYBER)
        qty_in.setValidator(QDoubleValidator(1, max_stock, 0))
        dialog.set_content(qty_in)
        
        btn_layout = QHBoxLayout()
        btn_save = QPushButton("UPDATE")
        btn_save.setStyleSheet(STYLE_NEON_BUTTON)
        btn_save.clicked.connect(dialog.accept)
        btn_layout.addWidget(btn_save)
        
        dialog.add_buttons(btn_layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
             try:
                 new_qty = int(float(qty_in.text()))
                 if 1 <= new_qty <= max_stock:
                     item['qty'] = new_qty
                     item['total'] = item['price'] * new_qty
                     self.refresh_cart()
                 else:
                     ProMessageBox.warning(self, "Invalid", f"Qty must be between 1 and {max_stock}")
             except ValueError:
                 pass

    def refresh_cart(self):
        self.populate_cart_table()
        self.calculate_totals()
        
    def populate_cart_table(self):
        self.cart_table.setRowCount(0)
        for i, item in enumerate(self.cart_items):
            self.cart_table.insertRow(i)
            
            def create_item(val, align=Qt.AlignmentFlag.AlignCenter):
                it = QTableWidgetItem(str(val))
                it.setTextAlignment(align)
                return it

            self.cart_table.setItem(i, 0, create_item(item['sys_id']))
            self.cart_table.setItem(i, 1, create_item(item['name'], Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter))
            self.cart_table.setItem(i, 2, create_item(f"{item['price']:.2f}"))
            
            # REMAIN STOCK
            remain = item['db_stock'] - item['qty']
            rem_item = create_item(remain)
            rem_item.setForeground(QBrush(QColor("#ff4444") if remain < 5 else QColor(COLOR_ACCENT_GREEN)))
            self.cart_table.setItem(i, 3, rem_item)
            
            self.cart_table.setItem(i, 4, create_item(item['qty']))
            self.cart_table.setItem(i, 5, create_item(f"{item['total']:.2f}"))
            
            # ACTIONS
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(10)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            btn_edit = QPushButton("✏️")
            btn_edit.setFixedSize(32, 28)
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setStyleSheet("QPushButton { background-color: #2196f3; border: none; border-radius: 4px; padding: 0px; margin: 0px; text-align: center; font-size: 16px; } QPushButton:hover { background-color: #1976d2; }")
            btn_edit.clicked.connect(lambda _, idx=i: self.edit_cart_item(idx))
            
            btn_del = QPushButton("🗑️")
            btn_del.setFixedSize(32, 28)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setStyleSheet("QPushButton { background-color: #f44336; border: none; border-radius: 4px; padding: 0px; margin: 0px; text-align: center; font-size: 16px; } QPushButton:hover { background-color: #d32f2f; }")
            btn_del.clicked.connect(lambda _, idx=i: self.remove_cart_item(idx))
            
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_del)
            
            self.cart_table.setCellWidget(i, 6, action_widget)

    def calculate_totals(self):
        sub_total = sum(item['total'] for item in self.cart_items)
        
        # Calculate counters
        parts_count = len(self.cart_items)  # Number of unique parts
        items_count = sum(item['qty'] for item in self.cart_items)  # Total quantity
        
        try:
            txt = self.in_discount_pct.text().strip()
            # Input is PERCENTAGE ONLY
            perc = float(txt) if txt else 0.0
            if perc > 100: perc = 100
        except ValueError:
            perc = 0.0
            
        savings_amt = (sub_total * perc) / 100
        grand_total = sub_total - savings_amt
        if grand_total < 0: grand_total = 0
        
        # --- ANIMATED UPDATES with PULSE EFFECTS ---
        
        # Check if values changed for pulse effects
        try:
            old_parts = int(float(self.lbl_parts_count.text())) if self.lbl_parts_count.text() else 0
            old_items = int(float(self.lbl_items_count.text())) if self.lbl_items_count.text() else 0
        except:
            old_parts = 0
            old_items = 0
        
        # Update counters with animation
        if parts_count != old_parts:
            self.lbl_parts_count.animateTo(parts_count)
            PulseEffect.pulse(self.card_parts, "#1a0a1a", "#9C27B0", 400)
        
        if items_count != old_items:
            self.lbl_items_count.animateTo(items_count)
            PulseEffect.pulse(self.card_items, "#1a0f00", "#FF6F00", 400)
        
        # Animate financial values
        self.lbl_subtotal.animateTo(sub_total)
        self.lbl_savings.animateTo(savings_amt)
        
        # Pulse savings card if discount changes
        if savings_amt > 0:
            PulseEffect.pulse(self.card_savings, "#051a05", COLOR_ACCENT_GREEN, 500)
        
        # Update Grand Total with special effect
        self.lbl_grand_total.setText(f"₹ {grand_total:.2f}")
        
        return sub_total, savings_amt, grand_total

    def check_customer_history(self):
        mobile = self.in_mobile.text().strip()
        if len(mobile) == 10 and mobile.isdigit():
            try:
                # Expected return: (Name, Model, Reg, LastVisit, FavPart)
                # If db returns only 3, we adapt.
                history = self.db_manager.get_customer_history(mobile)
                if history:
                    # Name, Model, Reg
                    self.in_cust_name.setText(history[0])
                    self.in_vehicle.setText(history[1])
                    self.in_reg_no.setText(history[2] if history[2] else "")
                    
                    # HUD Update
                    if len(history) >= 5:
                        last_visit = history[3]
                        fav_part = history[4]
                        
                        self.lbl_last_visit.setText(f"🕒 LAST VISIT: {last_visit}")
                        self.lbl_fav_part.setText(f"⭐ FAVORITE: {fav_part}")
                        self.hud_container.setVisible(True)
                        
                        # Animate HUD Entry (Simple Opacity/Slide simulation via timer if needed, but simple show is OK)
                    
                    # Visual Cue: Neon Glow
                    from PyQt6.QtWidgets import QGraphicsDropShadowEffect
                    for widget in [self.in_cust_name, self.in_vehicle, self.in_reg_no]:
                        glow = QGraphicsDropShadowEffect()
                        glow.setBlurRadius(20)
                        glow.setColor(QColor("#00e5ff"))
                        glow.setOffset(0, 0)
                        widget.setGraphicsEffect(glow)
                        
                        # Remove glow after 1.5 seconds
                        QTimer.singleShot(1500, lambda w=widget: w.setGraphicsEffect(None))
                else:
                    self.hud_container.setVisible(False)
            except Exception as e:
                app_logger.error(f"Error checking customer history: {e}")
        else:
            self.hud_container.setVisible(False)
    
    def add_dynamic_field(self):
        # Custom input dialog for Label
        dialog = QDialog(self)
        dialog.setWindowTitle("ADD DETAIL")
        dialog.setFixedSize(300, 150)
        dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(dialog)
        frame = QFrame()
        frame.setStyleSheet(f"background-color: #0b0b14; border: 1px solid {COLOR_ACCENT_CYAN}; border-radius: 8px;")
        f_layout = QVBoxLayout(frame)
        
        label_in = QLineEdit()
        label_in.setPlaceholderText("Field Name (e.g., Chassis No)")
        label_in.setStyleSheet(STYLE_INPUT_CYBER)
        f_layout.addWidget(label_in)
        
        btn_add = QPushButton("ADD")
        btn_add.setStyleSheet(STYLE_NEON_BUTTON)
        btn_add.clicked.connect(dialog.accept)
        f_layout.addWidget(btn_add)
        
        layout.addWidget(frame)
        
        if dialog.exec() == QDialog.DialogCode.Accepted and label_in.text().strip():
            field_name = label_in.text().strip()
            
            # Save to database for persistence
            if self.db_manager.add_custom_billing_field(field_name):
                self._create_field_ui(field_name)
            else:
                # Field already exists
                ProMessageBox.warning(self, "Duplicate", f"Field '{field_name}' already exists!")

    def remove_dynamic_field(self, row_widget_to_remove):
        # 1. Find and remove from list
        field_name_to_remove = None
        for i, (fname, finp, frow) in enumerate(self.dynamic_fields):
            if frow == row_widget_to_remove:
                field_name_to_remove = fname
                self.dynamic_fields.pop(i)
                break
        
        # 2. Remove from database for permanent deletion
        if field_name_to_remove:
            self.db_manager.remove_custom_billing_field(field_name_to_remove)
        
        # 3. Remove from UI
        self.dynamic_container.removeWidget(row_widget_to_remove)
        row_widget_to_remove.deleteLater()
        row_widget_to_remove = None

    def _create_field_ui(self, field_name):
        """Create UI elements for a custom field"""
        # Container for the Row (Label + Input + Remove Button)
        row_widget = QWidget()
        row_layout = QVBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 10)
        row_layout.setSpacing(5)
        
        # Label
        lbl = QLabel(f"{field_name}:")
        lbl.setStyleSheet(f"color: {COLOR_ACCENT_CYAN}; font-size: 12px;")
        row_layout.addWidget(lbl)
        
        # Input & Remove Button Horizontal Layout
        input_row_layout = QHBoxLayout()
        input_row_layout.setContentsMargins(0, 0, 0, 0)
        input_row_layout.setSpacing(5)
        
        inp = QLineEdit()
        inp.setPlaceholderText(f"Enter {field_name}")
        inp.setFixedHeight(40)
        inp.setStyleSheet(STYLE_INPUT_CYBER)
        input_row_layout.addWidget(inp)
        
        # Remove Button
        btn_remove = QPushButton("🗑️")
        btn_remove.setFixedSize(40, 40)
        btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_remove.setStyleSheet("QPushButton { background-color: #f44336; border: none; border-radius: 4px; padding: 0px; margin: 0px; text-align: center; font-size: 16px; } QPushButton:hover { background-color: #d32f2f; }")
        btn_remove.clicked.connect(lambda: self.remove_dynamic_field(row_widget))
        
        input_row_layout.addWidget(btn_remove)
        
        row_layout.addLayout(input_row_layout)
        
        self.dynamic_container.addWidget(row_widget)
        
        # Store reference: field_name, input_widget, row_widget
        self.dynamic_fields.append((field_name, inp, row_widget))

    def load_saved_fields(self):
        """Load and restore custom fields from database on startup"""
        saved_fields = self.db_manager.get_custom_billing_fields()
        for field_name in saved_fields:
            self._create_field_ui(field_name)

    def generate_invoice(self, silent=False):
        if not self.cart_items: return None, None, None
        
        sub_total, discount, grand_total = self.calculate_totals()
        
        cust_name = self.in_cust_name.text() or "Walk-in"
        mobile = self.in_mobile.text() or ""
        vehicle = self.in_vehicle.text()
        reg_no = self.in_reg_no.text()
        
        inv_id = self.db_manager.get_next_invoice_id()
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Collect Dynamic Fields
        extra_details = {}
        # field tuple is now (name, input, row_widget)
        for fname, finput, _ in self.dynamic_fields:
             val = finput.text().strip()
             if val:
                 extra_details[fname] = val
        
        final_json = {
            "cart": self.cart_items,
            "vehicle": vehicle,
            "reg_no": reg_no,
            "extra_details": extra_details
        }
        json_items_str = json.dumps(final_json)
        
        # Calculate items count (Task 20)
        items_count = sum(item['qty'] for item in self.cart_items)
        
        # Pass items_count to save_invoice
        success, msg = self.db_manager.save_invoice((inv_id, cust_name, mobile, vehicle, reg_no, grand_total, discount, date_str, json_items_str, items_count))
        
        if success:
            app_logger.info(f"Invoice generated: {inv_id} for {cust_name}")
            for item in self.cart_items:
                self.db_manager.sell_part(item['sys_id'], item['qty'], inv_id, cust_name)
            
            pdf_items = []
            for idx, i in enumerate(self.cart_items, 1):
                pdf_items.append([
                    idx, 
                    i['sys_id'], 
                    i['name'], 
                    i['qty'], 
                    f"Rs. {i['price']:.2f}", 
                    f"Rs. {i['total']:.2f}"
                ])
            
            inv_meta = {
                "invoice_id": inv_id,
                "date": date_str,
                "customer": cust_name,
                "mobile": mobile,
                "vehicle": vehicle,
                "reg_no": reg_no,
                "sub_total": sub_total,
                "discount": discount,
                "total": grand_total,
                "extra_details": extra_details
            }
                
            try:
                pdf_path = self.pdf_generator.generate_invoice_pdf(inv_meta, pdf_items)
            except Exception as e:
                app_logger.error(f"PDF Generation Failed: {e}")
                ProMessageBox.critical(self, "PDF Error", str(e))
                return None, None, None
            
            if not silent:
                 # Auto Open PDF
                 try:
                     os.startfile(pdf_path)
                 except Exception as e:
                     app_logger.error(f"Error opening PDF: {e}")
                 
                 self.reset_form()
                
            return inv_id, grand_total, pdf_path
        else:
            # Error Handling - Neon Red
            app_logger.error(f"Failed to save invoice: {msg}")
            ProMessageBox.critical(self, "Error", "Bhai, PDF nahi mil rahi!")
            return None, None, None

    def reset_form(self):
        self.cart_items = []
        self.refresh_cart()
        self.in_cust_name.clear()
        self.in_mobile.clear()
        self.in_vehicle.clear()
        self.in_reg_no.clear()
        self.in_discount_pct.setText("0")
        self.lbl_savings.setText("0.00")
        self.lbl_grand_total.setText("₹ 0.00")
        
        # Clear custom field VALUES only, not the fields themselves
        for field_name, input_widget, row_widget in self.dynamic_fields:
            input_widget.clear()

    def send_whatsapp(self):
        if not self.cart_items:
            ProMessageBox.warning(self, "Empty Cart", "Add Items first")
            return

        if not ProMessageBox.question(self, "Confirm", "Save & WhatsApp?"):
            return
            
        # Real-Time Capture
        current_name = self.in_cust_name.text().strip() or "Customer"
        current_mobile = self.in_mobile.text().strip()
        
        # Validation - Neon Red Warning
        import re
        clean_mobile = re.sub(r'\D', '', current_mobile)
        if len(clean_mobile) < 10:
             ProMessageBox.critical(self, "Error", "Bhai, mobile number sahi se check karo!")
             return
            
        # 1. Generate (Silent)
        inv_id, grand_total, pdf_path = self.generate_invoice(silent=True)
        
        if inv_id and pdf_path:
            # 2. Open PDF (Instant)
            try:
                os.startfile(pdf_path)
            except: pass
            
            # 3. Open Folder (Instant)
            try:
                folder = os.path.dirname(pdf_path)
                os.startfile(folder)
            except: pass

            # 4. Trigger WhatsApp (API)
            try:
                settings = self.db_manager.get_shop_settings()
                shop_name = settings.get("shop_name", "SpareParts Pro")
            except:
                shop_name = "SpareParts Pro"
                
            app_logger.info(f"Sending WhatsApp for {inv_id} to {current_mobile}")
            send_invoice_msg(current_mobile, current_name, inv_id, grand_total, pdf_path, shop_name)
            self.reset_form()
