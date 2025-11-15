from app import FakeProxyApp
from PyQt6.QtWidgets import QApplication
import sys

if __name__=='__main__':
    app=QApplication(sys.argv)
    w=FakeProxyApp()
    w.show()
    sys.exit(app.exec())