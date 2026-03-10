from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QLineEdit, QSpinBox, QComboBox, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt
import requests

class RightPanel(QWidget):
    def __init__(self, left):
        super().__init__()
        self.left = left
        self.setMinimumWidth(320)
        self.setMaximumWidth(450)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Container frame for better aesthetic
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #dcdde1;
            }
            QLabel {
                border: none;
                background: transparent;
            }
        """)
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(15)

        # Top row links
        top_row = QHBoxLayout()
        self.type_label = QLabel("Loại proxy cần mua")
        self.type_label.setStyleSheet("color: #0097e6; font-size: 13px; font-weight: bold;")
        
        self.intro_button = QPushButton("Giới thiệu")
        self.intro_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.intro_button.setStyleSheet("""
            QPushButton {
                color: #0097e6; background: transparent; 
                border: none; font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { text-decoration: underline; }
        """)
        top_row.addWidget(self.type_label)
        top_row.addStretch()
        top_row.addWidget(self.intro_button)
        frame_layout.addLayout(top_row)

        # Divider line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("border: 1px solid #f5f6fa; background: none;")
        frame_layout.addWidget(line)

        # Main title
        self.main_title = QLabel("Chọn loại proxy cần mua")
        self.main_title.setStyleSheet("color: #e84118; font-size: 16px; font-weight: bold;")
        frame_layout.addWidget(self.main_title)

        # Grid for form
        grid = QGridLayout()
        grid.setVerticalSpacing(8)
        grid.setHorizontalSpacing(15)
        
        # Common line edit style
        input_style = """
            QSpinBox, QLineEdit, QComboBox {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 4px 8px;
                background: #fdfdfd;
                font-size: 13px;
                min-height: 26px;
                color: #2f3640;
            }
            QSpinBox {
                min-width: 65px;
            }
            QSpinBox:focus, QLineEdit:focus, QComboBox:focus {
                border: 2px solid #82b1ff; /* light blue border like macOS */
                background: #ffffff;
            }
            QComboBox::drop-down {
                border: 0px;
                width: 24px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 24px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f0f0f0);
                border-left: 1px solid #c0c0c0;
            }
            QSpinBox:focus::up-button, QSpinBox:focus::down-button {
                border-left: 1px solid #82b1ff;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #e0e0e0);
            }
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
                background: #dcdde1;
            }
            QSpinBox::up-button {
                border-bottom: 1px solid #c0c0c0;
                border-top-right-radius: 3px;
            }
            QSpinBox:focus::up-button {
                border-bottom: 1px solid #82b1ff;
            }
            QSpinBox::down-button {
                border-bottom-right-radius: 3px;
            }
            QSpinBox::up-arrow {
                image: url("ui/up_arrow.svg");
                width: 10px;
                height: 10px;
            }
            QSpinBox::down-arrow {
                image: url("ui/down_arrow.svg");
                width: 10px;
                height: 10px;
            }
        """

        # Labels row 1
        lbl_days = QLabel("Ngày mua")
        lbl_days.setStyleSheet("font-weight: bold; font-size: 13px; color: #2f3640;")
        lbl_qty = QLabel("Số lượng")
        lbl_qty.setStyleSheet("font-weight: bold; font-size: 13px; color: #2f3640;")

        # Inputs row 1
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(30)
        self.days_spin.setStyleSheet(input_style)
        
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(0, 1000)
        self.quantity_spin.setValue(0)
        self.quantity_spin.setStyleSheet(input_style)

        grid.addWidget(lbl_days, 0, 0)
        grid.addWidget(lbl_qty, 0, 1)
        grid.addWidget(self.days_spin, 1, 0)
        grid.addWidget(self.quantity_spin, 1, 1)

        # Labels row 2
        lbl_user = QLabel("User auth (tùy chọn)")
        lbl_user.setStyleSheet("font-weight: bold; font-size: 13px; color: #2f3640;")
        lbl_type = QLabel("Giao thức")
        lbl_type.setStyleSheet("font-weight: bold; font-size: 13px; color: #2f3640;")

        # Inputs row 2
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Nhập user...")
        self.user_input.setStyleSheet(input_style)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["HTTP", "SOCKS5"])
        self.type_combo.setStyleSheet(input_style)

        grid.addWidget(lbl_user, 2, 0)
        grid.addWidget(lbl_type, 2, 1)
        grid.addWidget(self.user_input, 3, 0)
        grid.addWidget(self.type_combo, 3, 1)

        # Labels row 3
        lbl_pass = QLabel("Password auth (tùy chọn)")
        lbl_pass.setStyleSheet("font-weight: bold; font-size: 13px; color: #2f3640;")

        # Input row 3
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Nhập password...")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet(input_style)

        grid.addWidget(lbl_pass, 4, 0, 1, 2)
        grid.addWidget(self.password_input, 5, 0, 1, 2)

        frame_layout.addLayout(grid)

        # Price label
        self.price_label = QLabel("Lựa chọn cần: 0 VNĐ")
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.price_label.setStyleSheet("""
            color: #44bd32; 
            font-size: 16px; 
            font-weight: bold; 
            margin-top: 15px;
            margin-bottom: 5px;
        """)
        frame_layout.addWidget(self.price_label)

        # Buy button
        self.buy_button = QPushButton("Mua hàng")
        self.buy_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.buy_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0ff; 
                color: #0000ff; 
                font-weight: bold; 
                font-size: 14px;
                border: 1px solid #a4b0be;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #d1d8e0;
            }
            QPushButton:pressed {
                background-color: #a4b0be;
            }
        """)
        frame_layout.addWidget(self.buy_button)
        
        layout.addWidget(frame)
        layout.addStretch()

        # Connect signals
        self.quantity_spin.valueChanged.connect(self.update_price)
        self.days_spin.valueChanged.connect(self.update_price)
        self.buy_button.clicked.connect(self.buy)
        
        # Init price
        self.update_price()

    def update_price(self):
        quantity = self.quantity_spin.value()
        days = self.days_spin.value()
        
        if quantity == 0:
            price_text = "0 VNĐ"
        else:
            # Example price: 10k VND per proxy per day
            price = quantity * days * 10000
            price_text = f"{price:,} VNĐ"
            
        self.price_label.setText(f"Lựa chọn cần: {price_text}")

    def buy(self):
        quantity = self.quantity_spin.value()
        if quantity <= 0:
            self.price_label.setText("Vui lòng chọn số lượng!")
            self.price_label.setStyleSheet("color: #e84118; font-size: 16px; font-weight: bold; margin-top: 15px; margin-bottom: 5px;")
            return
            
        self.price_label.setText("Đã gửi yêu cầu mua hàng!")
        self.price_label.setStyleSheet("color: #e1b12c; font-size: 16px; font-weight: bold; margin-top: 15px; margin-bottom: 5px;")

