from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class StatCard(QWidget):
    """Single stat card with icon, number, and label"""
    
    def __init__(self, icon, title, bg_color, icon_color, parent=None):
        super().__init__(parent)
        self.icon = icon
        self.title = title
        self.bg_color = bg_color
        self.icon_color = icon_color
        
        self.setFixedHeight(70)
        self.setMinimumWidth(140)
        self.setMaximumWidth(200)
        
        # Setup UI
        self._setup_ui()
        
        # Apply styling
        self._apply_style()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(2)
        
        # Icon
        self.icon_label = QLabel(self.icon)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(16)
        self.icon_label.setFont(icon_font)
        layout.addWidget(self.icon_label)
        
        # Number
        self.number_label = QLabel("0")
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        number_font = QFont()
        number_font.setPointSize(16)
        number_font.setBold(True)
        self.number_label.setFont(number_font)
        layout.addWidget(self.number_label)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(8)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
    
    def _apply_style(self):
        # Modern flat design with good contrast
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {self.bg_color};
                border-radius: 6px;
                border: none;
            }}
        """)
        
        # Style labels with dark text for better readability
        self.icon_label.setStyleSheet(f"color: {self.icon_color}; background: transparent;")
        self.number_label.setStyleSheet("color: #2c3e50; background: transparent; font-weight: bold;")
        self.title_label.setStyleSheet("color: #95a5a6; background: transparent;")
        
        # Very subtle shadow effect
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(6)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 1)
        self.setGraphicsEffect(shadow)
    
    def update_value(self, value, suffix=""):
        """Update the displayed value"""
        self.number_label.setText(f"{value}{suffix}")
    
    def enterEvent(self, event):
        """Mouse enter - subtle highlight"""
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {self.bg_color};
                border-radius: 6px;
                border: 1px solid {self.icon_color};
            }}
        """)
        # Re-apply label styles
        self.icon_label.setStyleSheet(f"color: {self.icon_color}; background: transparent;")
        self.number_label.setStyleSheet("color: #2c3e50; background: transparent; font-weight: bold;")
        self.title_label.setStyleSheet("color: #95a5a6; background: transparent;")
    
    def leaveEvent(self, event):
        """Mouse leave - back to normal"""
        self.setStyleSheet(f"""
            StatCard {{
                background-color: {self.bg_color};
                border-radius: 6px;
                border: none;
            }}
        """)
        # Re-apply label styles
        self.icon_label.setStyleSheet(f"color: {self.icon_color}; background: transparent;")
        self.number_label.setStyleSheet("color: #2c3e50; background: transparent; font-weight: bold;")
        self.title_label.setStyleSheet("color: #95a5a6; background: transparent;")


class StatsPanel(QWidget):
    """Statistics panel with 4 cards"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(90)
        self.setMaximumHeight(90)
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Card 1: Total Proxies - Blue theme
        self.total_card = StatCard(
            "📦", 
            "Tổng số Proxy",
            "#e8eaf6",  # Lighter blue background
            "#3f51b5"   # Indigo icon
        )
        layout.addWidget(self.total_card)
        
        # Card 2: Live Proxies - Green theme
        self.live_card = StatCard(
            "✅", 
            "Proxy Live",
            "#e8f5e9",  # Light green background
            "#4caf50"   # Green icon
        )
        layout.addWidget(self.live_card)
        
        # Card 3: Dead Proxies - Red theme
        self.dead_card = StatCard(
            "❌", 
            "Proxy Dead",
            "#ffebee",  # Light red background
            "#f44336"   # Red icon
        )
        layout.addWidget(self.dead_card)
        
        # Card 4: Average Speed - Orange theme
        self.speed_card = StatCard(
            "⚡", 
            "Tốc độ TB",
            "#fff3e0",  # Light orange background
            "#ff9800"   # Orange icon
        )
        layout.addWidget(self.speed_card)
        
        # Add stretch to fill remaining space
        layout.addStretch()
    
    def update_stats(self, total, live, dead, avg_speed):
        """Update all statistics"""
        self.total_card.update_value(total)
        
        # Calculate percentages
        if total > 0:
            live_percent = int((live / total * 100))
            dead_percent = int((dead / total * 100))
            self.live_card.update_value(f"{live} ({live_percent}%)")
            self.dead_card.update_value(f"{dead} ({dead_percent}%)")
        else:
            self.live_card.update_value("0")
            self.dead_card.update_value("0")
        
        # Speed in seconds
        if avg_speed > 0:
            self.speed_card.update_value(f"{avg_speed:.2f}s")
        else:
            self.speed_card.update_value("N/A")
    
    def reset_stats(self):
        """Reset all stats to zero"""
        self.update_stats(0, 0, 0, 0)

