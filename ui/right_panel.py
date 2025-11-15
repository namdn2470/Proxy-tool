from PyQt6.QtWidgets import QVBoxLayout, QPushButton, QLabel, QLineEdit, QSpinBox, QComboBox, QHBoxLayout
import requests

class RightPanel(QVBoxLayout):
    def __init__(self, left):
        super().__init__()
        self.left = left

        # Top row: Loại proxy cần mua + Giới thiệu
        top_row = QHBoxLayout()
        self.type_label = QLabel("<span style='color:blue;'>Loại proxy cần mua</span>")
        self.type_label.setStyleSheet("font-size: 12px;")
        top_row.addWidget(self.type_label)
        self.intro_button = QPushButton("Giới thiệu")
        self.intro_button.setStyleSheet("color: blue; background: transparent; border: none; font-size: 12px;")
        top_row.addWidget(self.intro_button)
        top_row.addStretch()
        self.addLayout(top_row)

        # Main title
        self.main_title = QLabel("Chọn loại proxy cần mua")
        self.main_title.setStyleSheet("color: red; font-size: 18px; font-weight: bold;")
        self.addWidget(self.main_title)

        # Form layout
        form_row1 = QHBoxLayout()
        self.days_spin = QSpinBox()
        self.days_spin.setRange(1, 365)
        self.days_spin.setValue(30)
        form_row1.addWidget(QLabel("Ngày mua"))
        form_row1.addWidget(self.days_spin)
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 100)
        form_row1.addWidget(QLabel("Số lượng"))
        form_row1.addWidget(self.quantity_spin)
        self.addLayout(form_row1)

        form_row2 = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("User")
        form_row2.addWidget(self.user_input)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["HTTP", "SOCKS5"])
        form_row2.addWidget(QLabel("Type"))
        form_row2.addWidget(self.type_combo)
        self.addLayout(form_row2)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.addWidget(self.password_input)

        # Price label
        self.price_label = QLabel("Lựa chọn cần: 0 VNĐ")
        self.price_label.setStyleSheet("color: green; font-size: 16px; font-weight: bold;")
        self.addWidget(self.price_label)

        # Buy button
        self.buy_button = QPushButton("Mua hàng")
        self.buy_button.setStyleSheet("background: #e0e0ff; color: blue; font-weight: bold; font-size: 14px;")
        self.addWidget(self.buy_button)

        # Connect signals
        self.quantity_spin.valueChanged.connect(self.update_price)
        self.days_spin.valueChanged.connect(self.update_price)
        self.type_combo.currentIndexChanged.connect(self.update_price)
        self.buy_button.clicked.connect(self.buy)

    def update_price(self):
        quantity = self.quantity_spin.value()
        days = self.days_spin.value()
        type_ = self.type_combo.currentText()
        # Example price logic: 10k VND per proxy per day
        price = quantity * days * 10000
        self.price_label.setText(f"Lựa chọn cần: {price} VNĐ")

    def buy(self):
        # Placeholder: just show a message
        self.price_label.setText("Đã gửi yêu cầu mua hàng!")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        # Placeholder login
        response = requests.post('https://api.example.com/login', json={'username': username, 'password': password})
        if response.status_code == 200:
            self.token = response.json()['token']
            self.price_label.setText("Logged in")
        else:
            self.price_label.setText("Login failed")

    def update_price(self):
        quantity = self.quantity_spin.value()
        # Placeholder price calculation
        price = quantity * 0.1  # $0.1 per proxy
        self.price_label.setText(f"Price: ${price}")

    def buy(self):
        if hasattr(self, 'token'):
            type_ = self.type_combo.currentText()
            quantity = self.quantity_spin.value()
            response = requests.post('https://api.example.com/buy', json={'type': type_, 'quantity': quantity}, headers={'Authorization': self.token})
            if response.status_code == 200:
                proxies = response.json()['proxies']
                for proxy in proxies:
                    self.left.proxy_list.addItem(proxy)
                self.price_label.setText("Purchase successful")
            else:
                self.price_label.setText("Purchase failed")
