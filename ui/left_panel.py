from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox
)
from PyQt6.QtCore import Qt

class LeftPanel(QVBoxLayout):
    def update_proxies(self, proxies):
        self.table.setRowCount(len(proxies))
        for row, proxy in enumerate(proxies):
            stt = QTableWidgetItem(str(row + 1))
            stt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            proxy_item = QTableWidgetItem(proxy)
            proxy_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            col_type = QTableWidgetItem("Unknown")
            col_type.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status = QTableWidgetItem("Unknown")
            status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            pid = QTableWidgetItem("")
            pid.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            btn = QPushButton("Check")
            self.table.setItem(row, 0, stt)
            self.table.setItem(row, 1, proxy_item)
            self.table.setItem(row, 2, col_type)
            self.table.setItem(row, 3, status)
            self.table.setItem(row, 4, pid)
            self.table.setCellWidget(row, 5, btn)

    def __init__(self):
        super().__init__()

        # ============================
        # Thanh điều khiển phía trên
        # ============================
        top = QHBoxLayout()

        self.cb_filter = QComboBox()
        self.cb_filter.addItems(["ALL", "HTTP", "SOCKS5"])
        self.cb_filter.setFixedWidth(100)
        top.addWidget(self.cb_filter)

        btn_open = QPushButton("Mở list proxy hiện tại")
        btn_open.setFixedWidth(150)
        top.addWidget(btn_open)

        lbl_list = QPushButton("List ×")
        lbl_list.setEnabled(False)
        lbl_list.setStyleSheet("color: black; background: transparent; border: none; font-weight: bold;")
        top.addWidget(lbl_list)

        self.spin_list = QSpinBox()
        self.spin_list.setFixedWidth(50)
        self.spin_list.setValue(1)
        top.addWidget(self.spin_list)

        btn_fetch = QPushButton("Tải về list đã mua")
        btn_fetch.setFixedWidth(140)
        top.addWidget(btn_fetch)

        top.addStretch()
        self.addLayout(top)

        # ============================
        # BẢNG CHÍNH
        # ============================
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["stt", "Proxy", "Type", "Status", "PID", "Check"])

        # Kích thước cột đúng theo ảnh
        self.table.setColumnWidth(0, 50)   # stt
        self.table.setColumnWidth(1, 300)  # Proxy
        self.table.setColumnWidth(2, 80)   # Type
        self.table.setColumnWidth(3, 80)   # Status
        self.table.setColumnWidth(4, 80)   # PID
        self.table.setColumnWidth(5, 80)   # Check

        # Phong cách bảng giống ảnh
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                gridline-color: #d0d0d0;
                font-size: 12px;
            }
            QHeaderView::section {
                background: #f7f7f7;
                padding: 4px;
                border: 1px solid #c0c0c0;
                font-weight: bold;
            }
        """)

        # Disable edit (giống tool thật)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Nhiều dòng trắng giống trong ảnh
        self.table.setRowCount(20)
        for r in range(20):
            for c in range(6):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(r, c, item)

        self.addWidget(self.table)

        # ============================
        # Thanh refresh
        # ============================
        bottom = QHBoxLayout()

        btn_refresh = QPushButton("Làm mới list")
        btn_refresh.setFixedWidth(120)
        bottom.addWidget(btn_refresh)

        self.spin_threads = QSpinBox()
        self.spin_threads.setValue(1)
        self.spin_threads.setFixedWidth(50)
        bottom.addWidget(self.spin_threads)

        bottom.addStretch()
        self.addLayout(bottom)


    # ============================
    # HÀM THÊM PROXY VÀO BẢNG
    # ============================

    def add_proxy(self, proxy_string, ptype):
        row = self.table.rowCount()
        self.table.insertRow(row)

        stt = QTableWidgetItem(str(row + 1))
        stt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        proxy = QTableWidgetItem(proxy_string)
        proxy.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        col_type = QTableWidgetItem(ptype)
        col_type.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        status = QTableWidgetItem("Unknown")
        status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        pid = QTableWidgetItem("")
        pid.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        btn = QPushButton("Check")

        self.table.setItem(row, 0, stt)
        self.table.setItem(row, 1, proxy)
        self.table.setItem(row, 2, col_type)
        self.table.setItem(row, 3, status)
        self.table.setItem(row, 4, pid)
        self.table.setCellWidget(row, 5, btn)
