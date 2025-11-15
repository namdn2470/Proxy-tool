from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSplitter
from PyQt6.QtCore import Qt
from ui.left_panel import LeftPanel
from ui.middle_panel import MiddlePanel
from ui.right_panel import RightPanel
from ui.stats_panel import StatsPanel
from services.storage import Storage
from services.api_client import ApiClient
from services.proxy_checker import ProxyChecker
from services.process_manager import ProcessManager

class FakeProxyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Fake proxy v1.1.1')
        # Allow resizable window with minimum size
        self.setMinimumSize(1350, 750)  # Minimum to show all 3 panels (increased for 8 columns)
        self.resize(1550, 850)  # Default size
        # Set style
        self.setStyleSheet("""
            QMainWindow { background-color: #f7f7f7; color: #222; }
            QLabel { color: #222; }
            QPushButton { background-color: #e0e0e0; color: #222; border: 1px solid #bbb; }
            QPushButton:hover { background-color: #d0d0d0; }
            QListWidget { background-color: #fff; color: #222; }
            QTextEdit { background-color: #fff; color: #222; }
            QLineEdit { background-color: #fff; color: #222; }
            QCheckBox { color: #222; }
            QComboBox { background-color: #e0e0e0; color: #222; }
            QTableWidget { background-color: #fff; color: #222; }
        """)
        central=QWidget(); self.setCentralWidget(central)
        layout=QVBoxLayout(central)
        
        # Stats Panel at the top
        self.stats_panel = StatsPanel()
        layout.addWidget(self.stats_panel)
        
        # Main body panels with QSplitter for resizable dividers
        self.left=LeftPanel()
        self.middle=MiddlePanel(self.left)
        self.right=RightPanel(self.left)
        
        # Create horizontal splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)  # Prevent panels from collapsing completely
        splitter.addWidget(self.left)
        splitter.addWidget(self.middle)
        splitter.addWidget(self.right)
        
        # Set initial sizes (proportions: 55%, 25%, 20%)
        splitter.setSizes([800, 350, 280])
        splitter.setStretchFactor(0, 2)  # Left panel
        splitter.setStretchFactor(1, 1)  # Middle panel
        splitter.setStretchFactor(2, 1)  # Right panel
        
        # Add splitter to layout
        layout.addWidget(splitter)
        footer=QHBoxLayout()
        footer.addWidget(QLabel('Version: v1.1.1'))
        footer.addWidget(QLabel('Changelog: Updated to v1.1.1 with full functionalities'))
        footer.addWidget(QLabel('<a href="https://proxy.com">https://proxy.com</a>'))
        footer.addWidget(QPushButton('Hướng dẫn'))
        layout.addLayout(footer)

        # Services
        self.storage = Storage()
        self.api_client = ApiClient()
        self.proxy_checker = ProxyChecker()
        self.process_manager = ProcessManager()

        # Connect services to left panel
        self.left.set_proxy_checker(self.proxy_checker)
        self.left.set_storage(self.storage)
        self.left.set_refresh_callback(self.update_proxy_list)
        self.left.set_stats_callback(self.update_stats)

        # Initial load
        self.update_proxy_list()

    def update_proxy_list(self):
        self.left.update_proxies(self.storage.get_proxies())
        self.update_stats()
    
    def update_stats(self):
        """Update statistics panel"""
        proxies = self.storage.get_proxies()
        
        total = len(proxies)
        live = 0
        dead = 0
        total_speed = 0
        speed_count = 0
        
        for proxy in proxies:
            if isinstance(proxy, dict):
                status = proxy.get('status', 'Unknown')
                if status == 'LIVE':
                    live += 1
                    # Collect speed if available
                    response_time = proxy.get('response_time', 0)
                    if response_time and response_time > 0:
                        total_speed += response_time
                        speed_count += 1
                elif status in ['DIE', 'TIMEOUT']:
                    dead += 1
        
        # Calculate average speed
        avg_speed = total_speed / speed_count if speed_count > 0 else 0
        
        # Update stats panel
        self.stats_panel.update_stats(total, live, dead, avg_speed)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = FakeProxyApp()
    window.show()
    sys.exit(app.exec())