from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QWidget, QSizePolicy, QGraphicsDropShadowEffect, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF, QPoint, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QBrush, QPolygonF, QConicalGradient, QRadialGradient
import math
import time
from styles import COLOR_ACCENT_CYAN, COLOR_BACKGROUND, STYLE_NEON_BUTTON, COLOR_ACCENT_RED

class TechCard(QFrame):
    """
    A custom frame with 'Clipped Corners' and Neon Glow.
    Simulates the 'Mechanical' HUD look.
    """
    def __init__(self, title, value_widget, glow_color=COLOR_ACCENT_CYAN, parent=None):
        super().__init__(parent)
        self.glow_color = QColor(glow_color)
        self.title = title
        self.value_widget = value_widget
        self.setFixedHeight(100)
        
        # Setup Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(25, 15, 25, 15)
        self.layout.setSpacing(5)
        
        # Title
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet(f"color: #8899aa; font-size: 11px; font-weight: 700; letter-spacing: 1px; font-family: 'Segoe UI'; border: none; background: transparent;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.lbl_title)
        
        # Value (Passed Widget)
        # Ensure value widget styling
        self.value_widget.setStyleSheet(f"color: white; font-size: 28px; font-weight: bold; border: none; background: transparent; font-family: 'Segoe UI';")
        self.value_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.value_widget)
        
        # Drop Shadow for Neon Glow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(self.glow_color)
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = QRectF(self.rect())
        # Adjust for shadow margin if needed, but here we paint full rect
        # Tech Shape: Clip Top-Left and Bottom-Right corners
        clip_size = 15.0
        
        path = QPainterPath()
        # Start Top-Left (shifted)
        path.moveTo(rect.left() + clip_size, rect.top())
        # Top-Right
        path.lineTo(rect.right(), rect.top())
        # Bottom-Right (shifted)
        path.lineTo(rect.right(), rect.bottom() - clip_size)
        # Bottom-Right Corner Cut
        path.lineTo(rect.right() - clip_size, rect.bottom())
        # Bottom-Left
        path.lineTo(rect.left(), rect.bottom())
        # Top-Left Corner Cut
        path.lineTo(rect.left(), rect.top() + clip_size)
        path.closeSubpath()
        
        # Draw Background (Glassmorphism Gradient)
        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0, QColor(5, 8, 15, 200))
        grad.setColorAt(1, QColor(2, 4, 8, 150))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)
        
        # Draw Border
        pen = QPen(self.glow_color)
        pen.setWidthF(1.5)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # Draw Tech Accents (Little deco lines)
        # Top Left Pattern
        painter.setPen(QPen(self.glow_color, 3))
        painter.drawLine(int(rect.left()), int(rect.top() + clip_size), int(rect.left() + clip_size), int(rect.top()))

        # Bottom Right Pattern
        painter.drawLine(int(rect.right()), int(rect.bottom() - clip_size), int(rect.right() - clip_size), int(rect.bottom()))


class ProDialog(QDialog):
    """Base class for all custom dialogs in the app"""
    def __init__(self, parent=None, title="Dialog", width=400, height=200):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Main Frame with Border
        self.frame = QFrame()
        self.frame.setStyleSheet(f"""
            QFrame {{
                background-color: #0b0b14; 
                border: 1px solid {COLOR_ACCENT_CYAN}; 
                border-radius: 8px;
            }}
        """)
        self.frame_layout = QVBoxLayout(self.frame)
        self.frame_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        self.lbl_title = QLabel(title.upper())
        self.lbl_title.setStyleSheet(f"color: {COLOR_ACCENT_CYAN}; font-weight: bold; font-size: 14px; border: none; margin-bottom: 10px;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frame_layout.addWidget(self.lbl_title)
        
        self.layout.addWidget(self.frame)

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()
        
        parent = self.parent()
        if parent:
            try:
                # Calculate Parent Center in Global Screen Coordinates
                if isinstance(parent, QWidget):
                    # Get the window (top-level) of the parent to be sure
                    target = parent.window()
                    
                    # Top-left of target in screen coords
                    parent_pos = target.mapToGlobal(QPoint(0, 0))
                    parent_width = target.width()
                    parent_height = target.height()
                    
                    center_x = parent_pos.x() + (parent_width // 2)
                    center_y = parent_pos.y() + (parent_height // 2)
                    
                    # My Dimensions
                    my_w = self.width()
                    my_h = self.height()
                    
                    # Top-Left for Me
                    new_x = center_x - (my_w // 2)
                    new_y = center_y - (my_h // 2)
                    
                    self.move(new_x, new_y)
            except Exception:
                pass # Fallback to default

    def set_content(self, widget):
        """Add content widget to the dialog"""
        self.frame_layout.addWidget(widget)

    def add_buttons(self, buttons_layout):
        """Add button layout to the bottom"""
        self.frame_layout.addLayout(buttons_layout)


class ProMessageBox(ProDialog):
    """Custom replacement for QMessageBox"""
    def __init__(self, parent, title, message, mode="INFO", yes_no=False):
        # Adjust height based on content approx
        super().__init__(parent, title, width=350, height=180)
        
        # Message Label
        self.lbl_msg = QLabel(message)
        self.lbl_msg.setStyleSheet("color: white; font-size: 13px; border: none;")
        self.lbl_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_msg.setWordWrap(True)
        self.frame_layout.addWidget(self.lbl_msg)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        # Center the buttons
        btn_layout.addStretch()
        
        if yes_no:
            self.result_val = False
            
            btn_yes = QPushButton("YES")
            btn_yes.setCursor(Qt.CursorShape.PointingHandCursor)
            # Red for delete/critical, Cyan otherwise? Let's stick to standard Neon for Yes or specific colors
            if mode == "DELETE":
                 btn_yes.setStyleSheet("background-color: #f44336; color: white; border: none; border-radius: 4px; padding: 8px; font-weight: bold;")
            else:
                 btn_yes.setStyleSheet(STYLE_NEON_BUTTON)
            
            btn_yes.clicked.connect(self.accept_yes)
            
            btn_no = QPushButton("NO")
            btn_no.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_no.setStyleSheet("background-color: #333; color: white; border: 1px solid #555; border-radius: 4px; padding: 8px;")
            btn_no.clicked.connect(self.reject)
            
            btn_layout.addWidget(btn_yes)
            btn_layout.addWidget(btn_no)
            
        else: # OK Only
            btn_ok = QPushButton("OK")
            btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_ok.setStyleSheet(STYLE_NEON_BUTTON)
            btn_ok.clicked.connect(self.accept)
            btn_layout.addWidget(btn_ok)
            
        btn_layout.addStretch()
        self.frame_layout.addLayout(btn_layout)
        
    def accept_yes(self):
        self.result_val = True
        self.accept()

    @staticmethod
    def information(parent, title, message):
        dlg = ProMessageBox(parent, title, message, mode="INFO")
        dlg.exec()

    @staticmethod
    def warning(parent, title, message):
        dlg = ProMessageBox(parent, title, message, mode="WARNING")
        dlg.exec()

    @staticmethod
    def critical(parent, title, message):
        dlg = ProMessageBox(parent, title, message, mode="CRITICAL")
        dlg.exec()
        
    @staticmethod
    def question(parent, title, message):
        """Returns True for Yes, False for No"""
        dlg = ProMessageBox(parent, title, message, mode="QUESTION", yes_no=True)
        return dlg.exec() == QDialog.DialogCode.Accepted

class CyberSidebarButton(QWidget):
    """
    A futuristic sidebar button with a 'Reactor Box' icon container.
    Structure:
      - Reactor Box (QFrame)
        - Icon Label
      - Text Label (Bottom)
    """
    clicked = pyqtSignal()
    
    def __init__(self, text, icon_text, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(90, 85)
        
        self.is_active = False
        self.is_hovered = False
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 1. Reactor Box (Container for Icon)
        self.reactor_box = QFrame()
        self.reactor_box.setFixedSize(48, 48)
        
        # Icon inside Box
        self.lbl_icon = QLabel(icon_text, self.reactor_box)
        self.lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_icon.setGeometry(0, 0, 48, 48)

        # Effect for Pulse
        self.reactor_eff = QGraphicsOpacityEffect(self.reactor_box)
        self.reactor_eff.setOpacity(1.0)
        self.reactor_box.setGraphicsEffect(self.reactor_eff)
        
        layout.addWidget(self.reactor_box)
        
        # 2. Label (Bottom)
        self.lbl_text = QLabel(text)
        self.lbl_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_text)
        
        self.update_style()

    def setChecked(self, checked):
        self.is_active = checked
        self.update_style()
        
    def enterEvent(self, event):
        self.is_hovered = True
        self.update_style()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.is_hovered = False
        self.update_style()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def click(self):
        """Simulate a click"""
        self.clicked.emit()
        
    def showEvent(self, event):
        super().showEvent(event)
        # Start Pulse Animation
        self.pulse_anim = QPropertyAnimation(self.reactor_eff, b"opacity")
        self.pulse_anim.setDuration(1500)
        self.pulse_anim.setStartValue(0.7)
        self.pulse_anim.setEndValue(1.0)
        self.pulse_anim.setLoopCount(-1) # Infinite
        self.pulse_anim.setEasingCurve(QEasingCurve.Type.CosineCurve)
        self.pulse_anim.start()
            
    def update_style(self):
        lbl_style_base = "background: transparent; border: none; font-family: 'Segoe UI';"
        
        # Cyber Shape: Asymmetric Corners
        shape_style = "border-top-left-radius: 12px; border-bottom-right-radius: 12px; border-top-right-radius: 2px; border-bottom-left-radius: 2px;"
        
        if self.is_active:
            # Active State: HIDDEN REACTOR GLOW (Intense)
            self.reactor_box.setStyleSheet(f"""
                QFrame {{
                    background-color: qradialgradient(cx:0.5, cy:0.5, radius: 1.0, fx:0.5, fy:0.5, stop:0 rgba(0, 242, 255, 0.4), stop:1 transparent);
                    border: 2px solid {COLOR_ACCENT_CYAN};
                    {shape_style}
                    border-left: 3px solid {COLOR_ACCENT_CYAN}; /* Solid Cyan Bar (Spec Update) */
                }}
            """)
            self.lbl_icon.setStyleSheet(f"color: #fff; font-size: 24px; {lbl_style_base}")
            self.lbl_text.setStyleSheet(f"color: {COLOR_ACCENT_CYAN}; font-size: 10px; font-weight: 800; letter-spacing: 2px; {lbl_style_base}")
            
            # Add Shadow (Simulated via graphics effect on box if possible, but stylesheet is safer for now)
            
        elif self.is_hovered:
             self.reactor_box.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(0, 242, 255, 0.1);
                    border: 1px solid {COLOR_ACCENT_CYAN};
                    {shape_style}
                }}
            """)
             self.lbl_icon.setStyleSheet(f"color: {COLOR_ACCENT_CYAN}; font-size: 24px; {lbl_style_base}")
             self.lbl_text.setStyleSheet(f"color: white; font-size: 10px; font-weight: bold; letter-spacing: 1.5px; {lbl_style_base}")
            
        else:
            # Inactive State: Dim, Faint Tech
            self.reactor_box.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(10, 20, 30, 0.6);
                    border: 1px solid rgba(0, 242, 255, 0.15);
                    {shape_style}
                }}
            """)
            self.lbl_icon.setStyleSheet(f"color: #445566; font-size: 24px; {lbl_style_base}")
            self.lbl_text.setStyleSheet(f"color: #445566; font-size: 10px; font-weight: bold; letter-spacing: 1px; {lbl_style_base}")

from PyQt6.QtWidgets import QSplashScreen, QApplication
from PyQt6.QtCore import QTimer, Qt, QRectF, QPointF
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QFont, QLinearGradient, QRadialGradient
from styles import COLOR_ACCENT_CYAN

class SciFiSplashScreen(QSplashScreen):
    """
    Sifi Countdown Splash Screen.
    Cellphone Battery Filling Animation.
    """
    finished = pyqtSignal()
    
    def __init__(self):
        # Create a transparent pixmap
        pixmap = QPixmap(500, 300)
        pixmap.fill(Qt.GlobalColor.transparent)
        super().__init__(pixmap)
        
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Center
        if QApplication.primaryScreen():
            screen_geometry = QApplication.primaryScreen().geometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

        # Animation states
        self.start_time = time.time()
        self.duration = 4.0 # Time to charge
        self.charge_val = 0.0 # 0 to 100
        
        self.loading_text = "CHARGING SYSTEM..."
        self.is_finished = False
        
        # Pulse for charging effect
        self.pulse_alpha = 0
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16) # 60 FPS

    def update_animation(self):
        if self.is_finished: return

        elapsed = time.time() - self.start_time
        progress = min(1.0, elapsed / self.duration)
        
        self.charge_val = progress * 100.0
        
        # Pulse logic
        self.pulse_alpha = (math.sin(elapsed * 10) + 1) / 2 # 0 to 1 oscillating
        
        if progress >= 1.0:
            self.is_finished = True
            self.charge_val = 100.0
            self.loading_text = "FULLY CHARGED"
            self.update()
            
            # Start Fade Out
            QTimer.singleShot(200, self.start_fade_out)
        
        self.update()
        
    def start_fade_out(self):
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(500)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.finished.connect(self.close_and_notify)
        self.fade_anim.start()
        
    def close_and_notify(self):
        self.close()
        self.finished.emit()
        
        self.update()
            
    def update_progress(self, val, text=None):
        if text: self.loading_text = text.upper()
        # Only process events if we aren't overwhelming the loop
        if not hasattr(self, '_last_evt_time'): self._last_evt_time = 0
        now = time.time()
        if now - self._last_evt_time > 0.032: # 30 FPS throttle for events
            QApplication.processEvents()
            self._last_evt_time = now
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        cx, cy = rect.width() / 2, rect.height() / 2
        painter.translate(cx, cy)
        
        # Battery Dimensions
        bat_w = 200
        bat_h = 100
        nub_w = 15
        nub_h = 40
        
        # Determine Color based on charge
        if self.charge_val < 20:
            c_charge = QColor(255, 50, 50) # Red
        elif self.charge_val < 60:
            c_charge = QColor(255, 200, 0) # Yellow
        else:
            c_charge = QColor(0, 255, 100) # Green
            
        # Draw Battery Body Outline
        painter.setPen(QPen(QColor(255, 255, 255), 4))
        painter.setBrush(QColor(0, 0, 0, 150))
        body_rect = QRectF(-bat_w/2, -bat_h/2, bat_w, bat_h)
        painter.drawRoundedRect(body_rect, 10, 10)
        
        # Draw Positive Terminal Nub
        nub_rect = QRectF(bat_w/2, -nub_h/2, nub_w, nub_h)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRoundedRect(nub_rect, 4, 4)
        
        # Draw Charge Fill
        # Inner padding
        pad = 8
        fill_max_w = bat_w - (pad * 2)
        fill_h = bat_h - (pad * 2)
        
        current_fill_w = fill_max_w * (self.charge_val / 100.0)
        
        fill_rect = QRectF(-bat_w/2 + pad, -bat_h/2 + pad, current_fill_w, fill_h)
        
        # Gradient for the fill (making it look like liquid/energy)
        grad = QLinearGradient(fill_rect.topLeft(), fill_rect.bottomLeft())
        grad.setColorAt(0, c_charge.lighter(130))
        grad.setColorAt(0.5, c_charge)
        grad.setColorAt(1, c_charge.darker(110))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(grad)
        painter.drawRoundedRect(fill_rect, 4, 4)
        
        # Draw Lightning Bolt or Charging Icon inside if charging
        if not self.finished:
             # Pulsing overlay
             c_pulse = QColor(255, 255, 255, int(50 * self.pulse_alpha))
             painter.setBrush(c_pulse)
             painter.drawRoundedRect(fill_rect, 4, 4)
        
        # Text Percentage
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        painter.setFont(font)
        
        txt = f"{int(self.charge_val)}%"
        painter.drawText(body_rect, Qt.AlignmentFlag.AlignCenter, txt)
        
        # Status Text below
        font_sub = QFont("Consolas", 10)
        painter.setFont(font_sub)
        painter.setPen(QColor(200, 200, 200))
        painter.drawText(QRectF(-bat_w, bat_h/2 + 10, bat_w*2, 30), Qt.AlignmentFlag.AlignCenter, self.loading_text)


class ReactorStatCard(QWidget):
    """
    A futuristic Stat Card with a rotating 'Arc Reactor' ring around the value.
    Replaces static stat cards with something alive.
    """
    def __init__(self, title, value, color=COLOR_ACCENT_CYAN, parent=None, small=False):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.color = QColor(color)
        self.small = small
        
        # Dimensions
        self.setFixedSize(160, 160) if not small else self.setFixedSize(120, 100)
        
        # Animation State
        self.angle_outer = 0
        self.angle_inner = 0
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(50) # 20 FPS is enough for ambient
        
    def update_animation(self):
        self.angle_outer = (self.angle_outer + 2) % 360
        self.angle_inner = (self.angle_inner - 3) % 360
        self.update() # Trigger paint
        
    def set_value(self, val):
        self.value = str(val)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        center = QPointF(cx, cy)
        
        # Adjust size based on mode
        r_outer = 60 if not self.small else 35
        r_inner = 45 if not self.small else 25
        
        # 1. Background Glow (Subtle)
        radial = QRadialGradient(center, r_outer + 20)
        radial.setColorAt(0, QColor(0,0,0,0))
        c_trans = QColor(self.color)
        c_trans.setAlpha(30)
        radial.setColorAt(1, c_trans)
        painter.setBrush(QBrush(radial))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, r_outer+10, r_outer+10)

        # 2. Outer Rotating Ring
        painter.save()
        painter.translate(center)
        painter.rotate(self.angle_outer)
        
        pen = QPen(self.color)
        pen.setWidth(3 if not self.small else 2)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Draw 2 arcs
        painter.drawArc(int(-r_outer), int(-r_outer), int(r_outer*2), int(r_outer*2), 0*16, 100*16)
        painter.drawArc(int(-r_outer), int(-r_outer), int(r_outer*2), int(r_outer*2), 180*16, 100*16)
        
        painter.restore()
        
        # 3. Inner Rotating Ring (Reverse)
        painter.save()
        painter.translate(center)
        painter.rotate(self.angle_inner)
        
        pen.setWidth(2 if not self.small else 1)
        pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)
        
        painter.drawEllipse(int(-r_inner), int(-r_inner), int(r_inner*2), int(r_inner*2))
        
        painter.restore()
        
        # 4. Central Value
        painter.setPen(QColor("white"))
        f_size = 18 if not self.small else 14
        font = QFont("Segoe UI", f_size, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Draw Value Centered
        val_rect = QRectF(0, cy - 15, w, 30)
        painter.drawText(val_rect, Qt.AlignmentFlag.AlignCenter, str(self.value))
        
        # 5. Label (Bottom)
        painter.setPen(QColor("#8899aa"))
        font.setPointSize(9 if not self.small else 8)
        font.setWeight(QFont.Weight.Normal)
        painter.setFont(font)
        
        lbl_rect = QRectF(0, h - 25, w, 20)
        painter.drawText(lbl_rect, Qt.AlignmentFlag.AlignCenter, self.title.upper())

from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QLabel, QLineEdit, QTextEdit)
from PyQt6.QtCore import Qt, QTimer, QPointF, pyqtSignal

class LiveTerminal(QFrame):
    """
    High-End AI Command Terminal with holographic effects and premium design.
    """
    def __init__(self, ai_assistant=None, parent=None):
        super().__init__(parent)
        self.ai_assistant = ai_assistant
        self.setFixedHeight(200)
        
        # Animation state for border glow
        self.glow_intensity = 0
        self.glow_direction = 1
        
        # Premium Styling with gradient border effect
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(5, 10, 20, 0.95),
                    stop:0.5 rgba(10, 15, 30, 0.98),
                    stop:1 rgba(5, 10, 20, 0.95));
                border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00f2ff,
                    stop:0.5 #bc13fe,
                    stop:1 #00f2ff);
                border-radius: 12px;
            }
        """)
        
        # Add glow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 242, 255, 120))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 12, 15, 12)
        self.layout.setSpacing(8)
        
        # === PREMIUM HEADER ===
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        # AI Icon with animation
        self.ai_icon = QLabel("◈")
        self.ai_icon.setStyleSheet("""
            color: #00f2ff;
            font-size: 20px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        header_layout.addWidget(self.ai_icon)
        
        # Title with premium typography
        lbl_title = QLabel("AI NEXUS COMMAND INTERFACE")
        lbl_title.setStyleSheet("""
            color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #00f2ff,
                stop:0.5 #ffffff,
                stop:1 #bc13fe);
            font-family: 'Segoe UI', 'Arial';
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 3px;
            background: transparent;
            border: none;
        """)
        header_layout.addWidget(lbl_title)
        
        header_layout.addStretch()
        
        # Status Indicator
        self.status_indicator = QLabel("● ONLINE")
        self.status_indicator.setStyleSheet("""
            color: #00ff88;
            font-family: 'Consolas';
            font-size: 9px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        header_layout.addWidget(self.status_indicator)
        
        self.layout.addLayout(header_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFixedHeight(1)
        separator.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 transparent,
                stop:0.5 rgba(0, 242, 255, 0.5),
                stop:1 transparent);
            border: none;
        """)
        self.layout.addWidget(separator)
        
        # === LOG DISPLAY AREA ===
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("""
            QTextEdit {
                background-color: rgba(0, 0, 0, 0.7);
                color: #00ff88;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
                border: 1px solid rgba(0, 242, 255, 0.2);
                border-radius: 6px;
                padding: 8px;
                selection-background-color: rgba(0, 242, 255, 0.3);
            }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 0.3);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 242, 255, 0.5);
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 242, 255, 0.8);
            }
        """)
        self.layout.addWidget(self.log_area)
        
        # === COMMAND INPUT ===
        input_container = QHBoxLayout()
        input_container.setSpacing(8)
        
        # Prompt symbol
        prompt_label = QLabel("▶")
        prompt_label.setStyleSheet("""
            color: #00f2ff;
            font-size: 14px;
            font-weight: bold;
            background: transparent;
            border: none;
        """)
        input_container.addWidget(prompt_label)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(">_")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(0, 242, 255, 0.05);
                color: #ffffff;
                font-family: 'Consolas', 'Courier New';
                font-size: 12px;
                border: none;
                border-bottom: 2px solid rgba(0, 242, 255, 0.3);
                padding: 6px 10px;
                border-radius: 4px;
            }
            QLineEdit:focus {
                background-color: rgba(0, 242, 255, 0.1);
                border-bottom: 2px solid #00f2ff;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.3);
                font-style: italic;
            }
        """)
        self.input_field.returnPressed.connect(self.handle_input)
        input_container.addWidget(self.input_field)
        
        self.layout.addLayout(input_container)
        
        # Data
        self.logs = []
        self.max_logs = 8
        
        # Animation Timer
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animations)
        self.anim_timer.start(100)  # 10 FPS for subtle animations
        
        # Auto-Add Logs Timer (disabled by default for cleaner look)
        # Uncomment if you want ambient logs
        # self.log_timer = QTimer(self)
        # self.log_timer.timeout.connect(self.add_random_log)
        # self.log_timer.start(5000)  # Every 5s
        
        # Initial Welcome Message
        self.add_log("AI NEXUS initialized successfully", "SYSTEM")
        self.add_log("Neural pathways active. Ready for commands.", "SYSTEM")
        
    def update_animations(self):
        """Animate the AI icon and glow effects"""
        # Rotate AI icon symbol
        symbols = ["◈", "◇", "◆", "◈"]
        import random
        if random.random() < 0.1:  # 10% chance to change
            self.ai_icon.setText(random.choice(symbols))
    
    def add_log(self, text, log_type="INFO"):
        """Add a log entry with timestamp and type"""
        from datetime import datetime
        now = datetime.now().strftime("%H:%M:%S")
        
        # Color coding based on log type
        if log_type == "USER":
            color = "#00f2ff"
            prefix = "USER"
        elif log_type == "AI":
            color = "#bc13fe"
            prefix = "AI"
        elif log_type == "SYSTEM":
            color = "#ffaa00"
            prefix = "SYS"
        elif log_type == "ERROR":
            color = "#ff4444"
            prefix = "ERR"
        else:
            color = "#00ff88"
            prefix = "LOG"
        
        # Format with HTML for colored output
        formatted_log = f'<span style="color: #666;">[{now}]</span> <span style="color: {color}; font-weight: bold;">[{prefix}]</span> <span style="color: #00ff88;">{text}</span>'
        self.log_area.append(formatted_log)
        
    def add_random_log(self):
        """Add ambient system logs (optional)"""
        import random
        msgs = [
            "Neural network optimization complete",
            "Quantum cache synchronized",
            "Predictive algorithms running",
            "Database integrity verified",
            "Encryption layer active",
            "Memory allocation optimized"
        ]
        self.add_log(random.choice(msgs), "SYSTEM")

    def handle_input(self):
        """Process user input through AI"""
        text = self.input_field.text().strip()
        if not text:
            return
        
        # Display user command
        self.add_log(text, "USER")
        self.input_field.clear()
        
        # Process via AI
        if self.ai_assistant:
            try:
                response = self.ai_assistant.process_query(text)
                # Split multi-line responses for better formatting
                for line in response.split('\n'):
                    if line.strip():
                        self.add_log(line.strip(), "AI")
            except Exception as e:
                self.add_log(f"Processing error: {str(e)}", "ERROR")
        else:
            self.add_log("AI core not initialized", "ERROR")

class AINexusNode(QFrame):
    """
    Predictive Engine Display.
    Cycles through smart insights generated from real data.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(70)
        self.setStyleSheet("""
            background-color: rgba(140, 0, 255, 0.1); 
            border: 1px solid #bc13fe; 
            border-radius: 8px;
        """)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(15, 5, 15, 5)
        self.layout.setSpacing(15)
        
        # Icon / Brain Graphic
        lbl_icon = QLabel("🧠")
        lbl_icon.setStyleSheet("font-size: 24px; background: transparent; border: none;")
        self.layout.addWidget(lbl_icon)
        
        # Content Area
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        lbl_title = QLabel("AI NEXUS // PREDICTIVE ENGINE")
        lbl_title.setStyleSheet("color: #bc13fe; font-size: 10px; font-weight: bold; letter-spacing: 1px; background: transparent; border: none;")
        content_layout.addWidget(lbl_title)
        
        self.lbl_insight = QLabel("Initializing neural pathways...")
        self.lbl_insight.setStyleSheet("color: white; font-size: 13px; font-style: italic; background: transparent; border: none;")
        content_layout.addWidget(self.lbl_insight)
        
        self.layout.addLayout(content_layout)
        self.layout.addStretch()
        
        # Data
        self.insights = ["System Standby..."]
        self.current_idx = 0
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cycle_insight)
        self.timer.start(5000) # 5s cycle
        
    def set_insights(self, insights_list):
        if insights_list:
            self.insights = insights_list
            self.current_idx = 0
            self.update_display()
            
    def cycle_insight(self):
        if not self.insights: return
        self.current_idx = (self.current_idx + 1) % len(self.insights)
        self.update_display()
        
    def update_display(self):
        text = self.insights[self.current_idx]
        self.lbl_insight.setText(text)

class TopPerformerWidget(QFrame):
    """
    Displays a list of top performing items (e.g. Top Sales, Top Parts).
    """
    def __init__(self, title, icon_emoji="🏆", parent=None):
        super().__init__(parent)
        self.setFixedWidth(280) 
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(5, 8, 15, 0.8), stop:1 rgba(2, 4, 8, 0.6));
                border: 1px solid rgba(0, 242, 255, 0.15);
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        lbl_icon = QLabel(icon_emoji)
        lbl_icon.setStyleSheet("font-size: 18px; background: transparent; border: none;")
        
        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet("color: #00f2ff; font-weight: bold; font-family: 'Segoe UI'; font-size: 12px; letter-spacing: 1px; background: transparent; border: none;")
        
        header_layout.addWidget(lbl_icon)
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # List Container
        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(5)
        layout.addLayout(self.list_layout)
        layout.addStretch()
        
    def set_items(self, items):
        """
        items: list of tuples (name, value_display, optional_extra)
        """
        # Clear existing
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        if not items:
            lbl_empty = QLabel("No Data Available")
            lbl_empty.setStyleSheet("color: #666; font-style: italic; padding: 10px; background: transparent; border: none;")
            lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_layout.addWidget(lbl_empty)
            return

        for idx, item in enumerate(items[:5]): # Max 5
            name, value = item[0], item[1]
            
            row = QFrame()
            row.setStyleSheet("background: transparent; border: none;")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0,0,0,0)
            
            # Rank
            lbl_rank = QLabel(f"#{idx+1}")
            lbl_rank.setFixedWidth(30)
            lbl_rank.setStyleSheet(f"color: {'#ffaa00' if idx==0 else '#888'}; font-weight: bold;")
            
            # Name
            lbl_name = QLabel(str(name))
            lbl_name.setStyleSheet("color: white; font-size: 11px;")
            # Elide if too long
            
            # Value
            lbl_val = QLabel(str(value))
            lbl_val.setStyleSheet("color: #00ff88; font-weight: bold; font-family: 'Consolas';")
            
            row_layout.addWidget(lbl_rank)
            row_layout.addWidget(lbl_name, stretch=1)
            row_layout.addWidget(lbl_val)
            
            self.list_layout.addWidget(row)

