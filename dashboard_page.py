from PyQt6.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QLabel, QFrame, QHBoxLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from styles import (COLOR_ACCENT_CYAN, COLOR_ACCENT_YELLOW, COLOR_ACCENT_GREEN, COLOR_SURFACE,
                    DIM_MARGIN_STD, DIM_SPACING_STD)
from custom_components import ReactorStatCard, LiveTerminal, TechCard, TopPerformerWidget
import datetime

# Try importing Charts, if unavailable, fallback gracefully
try:
    from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    print("Warning: PyQt6 Charts module not found. Charts will be disabled.")

class DashboardPage(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.ai_assistant = None  # Will be loaded after UI renders
        
        self.setup_ui()
        
        # Defer heavy operations so the page renders instantly
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, self._deferred_init)

    def _deferred_init(self):
        """Load AI engine and stats after the UI has rendered."""
        from ai_manager import AIAssistant
        self.ai_assistant = AIAssistant(self.db_manager)
        if hasattr(self, 'terminal'):
            self.terminal.ai_assistant = self.ai_assistant
        self.refresh_stats()

    def load_data(self):
        """Called by Main Window refresh"""
        self.refresh_stats()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(DIM_MARGIN_STD, DIM_MARGIN_STD, DIM_MARGIN_STD, DIM_MARGIN_STD)
        self.main_layout.setSpacing(DIM_SPACING_STD)

        # Header
        header = QLabel("DASHBOARD COMMAND CENTER")
        header.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLOR_ACCENT_CYAN}; letter-spacing: 2px;")
        self.main_layout.addWidget(header)

        # 1. ARC REACTOR STATS (Grid)
        self.grid = QGridLayout()
        self.main_layout.addLayout(self.grid)
        
        # Row 0: Key Inventory Stats (Reactors)
        self.card_parts = ReactorStatCard("Unique Parts", "0", COLOR_ACCENT_CYAN)
        self.card_stock = ReactorStatCard("Total Stock", "0", COLOR_ACCENT_GREEN)
        self.card_low = ReactorStatCard("Critical Alerts", "0", "#ff4444")
        self.card_value = ReactorStatCard("Total Value", "₹ 0", COLOR_ACCENT_YELLOW)
        
        self.grid.addWidget(self.card_parts, 0, 0)
        self.grid.addWidget(self.card_stock, 0, 1)
        self.grid.addWidget(self.card_low, 0, 2)
        self.grid.addWidget(self.card_value, 0, 3)

        # Row 1: Top Movers & Sales Trend
        # Left: Top Selling Parts
        self.top_parts_widget = TopPerformerWidget("TOP SELLING PARTS", "🚀")
        self.grid.addWidget(self.top_parts_widget, 1, 0, 1, 1) # Span 1 col
        
        # Center: Financial Cards (Vertical Stack or smaller grid?)
        # Let's put financials in a column
        self.fin_layout = QVBoxLayout()
        self.lbl_rev = QLabel("₹ 0")
        self.lbl_exp = QLabel("₹ 0")
        self.lbl_prof = QLabel("₹ 0")
        
        self.card_revenue = TechCard("REVENUE", self.lbl_rev, "#00ff88")
        self.card_expense = TechCard("EXPENSES", self.lbl_exp, "#ff6666")
        self.card_profit = TechCard("NET PROFIT", self.lbl_prof, "#00ccff")
        
        # We can stack these 3 tech cards in column 1
        fin_container = QWidget()
        fin_vbox = QVBoxLayout(fin_container)
        fin_vbox.setContentsMargins(0,0,0,0)
        fin_vbox.setSpacing(5)
        fin_vbox.addWidget(self.card_revenue)
        fin_vbox.addWidget(self.card_expense)
        fin_vbox.addWidget(self.card_profit)
        fin_vbox.addStretch()
        
        self.grid.addWidget(fin_container, 1, 1, 1, 1)

        # Right: Sales Trend Chart (Spanning 2 cols)
        if CHARTS_AVAILABLE:
            chart_container = QFrame()
            chart_container.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(5, 8, 15, 0.8), stop:1 rgba(2, 4, 8, 0.6)); border-radius: 12px; border: 1px solid rgba(0, 242, 255, 0.15);")
            chart_layout = QVBoxLayout(chart_container)
            
            self.chart_view = QChartView()
            self.chart_view.setRenderHint(self.chart_view.renderHints().Antialiasing)
            self.chart_view.setBackgroundBrush(QColor("#121212")) 
            self.chart_view.setStyleSheet("background-color: transparent;")
            
            chart_layout.addWidget(QLabel("SALES TREND (7 DAYS)"))
            chart_layout.addWidget(self.chart_view)
            
            self.grid.addWidget(chart_container, 1, 2, 1, 2) # Span 2 cols
        
        # 2. LIVE TERMINAL (Spanning bottom)
        self.terminal = LiveTerminal(ai_assistant=self.ai_assistant)
        self.grid.addWidget(self.terminal, 2, 0, 1, 4) # Spans all 4 columns
        
        # Stretch
        self.main_layout.addStretch()

    def refresh_stats(self):
        # 1. Inventory Stats
        inv_stats = self.db_manager.get_dashboard_stats()
        self.card_parts.set_value(str(inv_stats['total_parts']))
        self.card_stock.set_value(str(inv_stats['total_stock_qty']))
        self.card_low.set_value(str(inv_stats['low_stock_count']))
        self.card_value.set_value(f"₹ {inv_stats['total_inventory_value']:,.0f}")
        
        # 2. Financial Stats
        fin_stats = self.db_manager.get_financial_summary()
        self.lbl_rev.setText(f"₹ {fin_stats['revenue']:,.2f}")
        self.lbl_exp.setText(f"₹ {fin_stats['expenses']:,.2f}")
        self.lbl_prof.setText(f"₹ {fin_stats['net_profit']:,.2f}")

        # 3. Top Parts
        # Get date range (last 30 days for relevance)
        today = datetime.date.today()
        start = today - datetime.timedelta(days=30)
        top_parts = self.db_manager.get_top_selling_parts(start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
        
        # Format for widget: (Name, Qty + Price info)
        widget_items = []
        for p in top_parts:
            # p = (part_id, part_name, total_qty, total_revenue)
            widget_items.append((p[1], f"{p[2]} sold"))
            
        self.top_parts_widget.set_items(widget_items)

        # 4. Update Chart (Sales Trend)
        if CHARTS_AVAILABLE:
            # Get last 7 days sales
            trend_start = today - datetime.timedelta(days=6)
            trend_data = self.db_manager.get_sales_by_date_range(trend_start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"))
            self.update_chart(trend_data)

    def update_chart(self, trend_data):
        # trend_data: list of (day, total_amount, count)
        
        # Create Bar Set
        set0 = QBarSet("Sales")
        set0.setColor(QColor(COLOR_ACCENT_CYAN))
        set0.setBorderColor(QColor(COLOR_ACCENT_CYAN))
        
        categories = []
        max_val = 0
        
        for row in trend_data:
            # row[0] is 'YYYY-MM-DD'
            # Let's format to 'DD MMM'
            d_obj = datetime.datetime.strptime(row[0], "%Y-%m-%d")
            categories.append(d_obj.strftime("%d %b"))
            set0.append(row[1])
            if row[1] > max_val: max_val = row[1]
            
        series = QBarSeries()
        series.append(set0)
        series.setBarWidth(0.5)
        
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Last 7 Days Revenue")
        chart.setTitleBrush(QColor("white"))
        chart.setBackgroundBrush(QColor("#121212"))
        chart.legend().setVisible(False)
        
        # Axis X
        axisX = QBarCategoryAxis()
        axisX.append(categories)
        axisX.setLabelsColor(QColor("white"))
        chart.addAxis(axisX, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(axisX)
        
        # Axis Y
        axisY = QValueAxis()
        axisY.setRange(0, max_val * 1.1) # 10% breathing room
        axisY.setLabelsColor(QColor("white"))
        chart.addAxis(axisY, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(axisY)
        
        self.chart_view.setChart(chart)
