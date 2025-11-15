from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from ui.left_panel import LeftPanel
from ui.middle_panel import MiddlePanel
from ui.right_panel import RightPanel
from services.storage import Storage
from services.api_client import ApiClient
from services.proxy_checker import ProxyChecker
from services.process_manager import ProcessManager

class FakeProxyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Fake proxy v1.1.1')
        self.setFixedSize(1150,680)
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
        body=QHBoxLayout()
        self.left=LeftPanel()
        self.middle=MiddlePanel(self.left)
        self.right=RightPanel(self.left)
        body.addLayout(self.left); body.addLayout(self.middle); body.addLayout(self.right)
        layout.addLayout(body)
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

        # Initial load
        self.update_proxy_list()

    def update_proxy_list(self):
        self.left.update_proxies(self.storage.get_proxies())

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = FakeProxyApp()
    window.show()
    sys.exit(app.exec())