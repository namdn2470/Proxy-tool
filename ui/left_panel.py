from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QProgressBar, QLabel, QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QColor

class ProxyCheckThread(QThread):
    """Thread for checking proxy to avoid blocking UI"""
    finished = pyqtSignal(int, str, str, str, float)  # row, type, status, ip, response_time
    
    def __init__(self, row, proxy, checker):
        super().__init__()
        self.row = row
        self.proxy = proxy
        self.checker = checker
    
    def run(self):
        proxy_type, status, response_time, ip = self.checker.check_proxy(self.proxy)
        ip_str = ip if ip else "N/A"
        time_val = response_time if response_time else 0.0
        self.finished.emit(self.row, proxy_type, status, ip_str, time_val)

class BatchProxyCheckThread(QThread):
    """Thread for checking multiple proxies"""
    progress = pyqtSignal(int, int)  # current, total
    single_finished = pyqtSignal(int, str, str, str, float)  # row, type, status, ip, time
    all_finished = pyqtSignal()
    
    def __init__(self, proxies, checker):
        super().__init__()
        self.proxies = proxies  # List of (row, proxy_string)
        self.checker = checker
    
    def run(self):
        total = len(self.proxies)
        for idx, (row, proxy) in enumerate(self.proxies, 1):
            proxy_type, status, response_time, ip = self.checker.check_proxy(proxy)
            ip_str = ip if ip else "N/A"
            time_val = response_time if response_time else 0.0
            self.single_finished.emit(row, proxy_type, status, ip_str, time_val)
            self.progress.emit(idx, total)
        self.all_finished.emit()

class LeftPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.proxy_checker = None  # Will be set by app.py
        self.storage = None  # Will be set by app.py
        self.refresh_callback = None  # Callback to refresh from parent
        self.stats_callback = None  # Callback to update stats
        
        # Pagination variables
        self.current_page = 1
        self.items_per_page = 999999  # Default to "Tất cả"
        self.total_items = 0
        self.all_proxies = []
        # filtered_proxies will be set when filter is applied
        # Track which proxies are checked (by full proxy string)
        self.checked_proxies = set()
        # Track pending filter to apply after check completes
        self.pending_filter = None
        
        # Resizable width with minimum (enough for all 8 columns)
        self.setMinimumWidth(700)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # ============================
        # Thanh điều khiển phía trên
        # ============================
        top = QHBoxLayout()

        self.cb_filter = QComboBox()
        self.cb_filter.addItems(["ALL", "HTTP", "HTTPS", "SOCKS5", "Unknown", "LIVE", "DIE", "TIMEOUT"])
        self.cb_filter.setFixedWidth(120)
        self.cb_filter.currentTextChanged.connect(self.apply_filter)
        self.cb_filter.setStyleSheet("""
            QComboBox {
                padding: 5px 25px 5px 10px;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: white;
                color: #333;
                font-size: 12px;
            }
            QComboBox:hover {
                border: 1px solid #2196F3;
            }
            QComboBox:focus {
                border: 1px solid #2196F3;
                outline: none;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #d0d0d0;
                background: transparent;
            }
            QComboBox::drop-down:hover {
                background-color: #e3f2fd;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #666;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #2196F3;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                border: 1px solid #d0d0d0;
                selection-background-color: #2196F3;
                selection-color: white;
                outline: none;
                padding: 2px;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 10px;
                min-height: 20px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e3f2fd;
                color: #333;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #2196F3;
                color: white;
            }
        """)
        top.addWidget(self.cb_filter)

        # Filter info label
        self.filter_info_label = QLabel("")
        self.filter_info_label.setStyleSheet("""
            QLabel {
                color: #555;
                font-size: 11px;
                padding: 2px 5px;
            }
        """)
        top.addWidget(self.filter_info_label)

        top.addStretch()
        layout.addLayout(top)

        # ============================
        # BẢNG CHÍNH
        # ============================
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["☐", "STT", "Proxy", "Type", "Status", "Real IP", "PID", "Check"])
        
        # Hide vertical header (row numbers) since we have STT column
        self.table.verticalHeader().setVisible(False)
        
        # Connect header click to toggle all checkboxes
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        self.all_checked = False  # Track state for header
        
        # Kích thước cột
        self.table.setColumnWidth(0, 40)   # Checkbox
        self.table.setColumnWidth(1, 50)   # STT
        self.table.setColumnWidth(2, 250)  # Proxy
        self.table.setColumnWidth(3, 80)   # Type
        self.table.setColumnWidth(4, 80)   # Status
        self.table.setColumnWidth(5, 120)  # Real IP
        self.table.setColumnWidth(6, 80)   # PID
        self.table.setColumnWidth(7, 80)   # Check

        # Phong cách bảng giống ảnh
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                gridline-color: #e0e0e0;
                font-size: 12px;
                selection-background-color: #2196F3;
                selection-color: white;
            }
            QHeaderView::section {
                background: #f5f5f5;
                padding: 6px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
                font-size: 14px;
                color: #424242;
            }
            QHeaderView::section:first {
                cursor: pointer;
                font-size: 16px;
            }
            QHeaderView::section:first:hover {
                background: #e3f2fd;
            }
            QTableWidget::item {
                padding: 4px;
            }
        """)

        # Disable edit (giống tool thật)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Enable selection
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Nhiều dòng trắng giống trong ảnh
        self.table.setRowCount(20)
        for r in range(20):
            # Add checkbox in first column
            checkbox = QCheckBox()
            checkbox.setStyleSheet("QCheckBox { margin-left: 10px; }")
            self.table.setCellWidget(r, 0, checkbox)
            
            # Add empty items for other columns
            for c in range(1, 8):
                if c != 7:  # Skip column 7 as it will have Check button
                    item = QTableWidgetItem("")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.table.setItem(r, c, item)

        layout.addWidget(self.table)

        # ============================
        # Thanh refresh và check all
        # ============================
        bottom = QHBoxLayout()

        self.btn_refresh = QPushButton("Làm mới list")
        self.btn_refresh.setFixedWidth(120)
        self.btn_refresh.clicked.connect(self.refresh_proxy_list)
        bottom.addWidget(self.btn_refresh)
        
        self.btn_check_all = QPushButton("Check All")
        self.btn_check_all.setFixedWidth(100)
        self.btn_check_all.clicked.connect(self.check_all_proxies)
        self.btn_check_all.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        bottom.addWidget(self.btn_check_all)
        
        self.btn_delete_selected = QPushButton("Xóa đã chọn")
        self.btn_delete_selected.setFixedWidth(120)
        self.btn_delete_selected.clicked.connect(self.delete_selected_proxies)
        self.btn_delete_selected.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        bottom.addWidget(self.btn_delete_selected)

        self.spin_threads = QSpinBox()
        self.spin_threads.setValue(1)
        self.spin_threads.setFixedWidth(50)
        bottom.addWidget(self.spin_threads)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(20)
        bottom.addWidget(self.progress_bar)

        # Refresh status label
        self.refresh_status_label = QLabel("")
        self.refresh_status_label.setStyleSheet("""
            QLabel {
                color: #2ecc71;
                font-size: 11px;
                font-weight: normal;
                padding: 2px 5px;
            }
        """)
        self.refresh_status_label.setVisible(False)
        bottom.addWidget(self.refresh_status_label)

        bottom.addStretch()
        layout.addLayout(bottom)
        
        # ============================
        # Pagination Controls
        # ============================
        pagination = QHBoxLayout()
        
        # Items per page selector
        pagination.addWidget(QLabel("Hiển thị:"))
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["50", "100", "1000", "Tất cả"])
        self.page_size_combo.setCurrentText("Tất cả")  # Default to "Tất cả"
        self.page_size_combo.setFixedWidth(80)
        self.page_size_combo.currentTextChanged.connect(self.on_page_size_changed)
        self.page_size_combo.setStyleSheet("""
            QComboBox {
                padding: 3px 8px;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                background-color: white;
            }
        """)
        pagination.addWidget(self.page_size_combo)
        pagination.addWidget(QLabel("items/trang"))
        
        pagination.addSpacing(20)
        
        # Page info
        self.page_info_label = QLabel("Showing 0-0 of 0")
        self.page_info_label.setStyleSheet("color: #555; font-size: 12px;")
        pagination.addWidget(self.page_info_label)
        
        pagination.addStretch()
        
        # Previous button
        self.btn_prev_page = QPushButton("◀ Trước")
        self.btn_prev_page.setFixedWidth(80)
        self.btn_prev_page.clicked.connect(self.previous_page)
        self.btn_prev_page.setEnabled(False)
        self.btn_prev_page.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                padding: 4px;
            }
            QPushButton:hover:enabled {
                background-color: #e3f2fd;
                border-color: #2196F3;
            }
            QPushButton:disabled {
                color: #ccc;
            }
        """)
        pagination.addWidget(self.btn_prev_page)
        
        # Page numbers container
        self.page_numbers_widget = QWidget()
        self.page_numbers_layout = QHBoxLayout(self.page_numbers_widget)
        self.page_numbers_layout.setContentsMargins(5, 0, 5, 0)
        self.page_numbers_layout.setSpacing(3)
        pagination.addWidget(self.page_numbers_widget)
        
        # Next button
        self.btn_next_page = QPushButton("Sau ▶")
        self.btn_next_page.setFixedWidth(80)
        self.btn_next_page.clicked.connect(self.next_page)
        self.btn_next_page.setEnabled(False)
        self.btn_next_page.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                padding: 4px;
            }
            QPushButton:hover:enabled {
                background-color: #e3f2fd;
                border-color: #2196F3;
            }
            QPushButton:disabled {
                color: #ccc;
            }
        """)
        pagination.addWidget(self.btn_next_page)
        
        layout.addLayout(pagination)

    def set_proxy_checker(self, checker):
        """Set proxy checker instance"""
        self.proxy_checker = checker
    
    def set_storage(self, storage):
        """Set storage instance"""
        self.storage = storage
    
    def set_refresh_callback(self, callback):
        """Set callback function to refresh from parent"""
        self.refresh_callback = callback
    
    def set_stats_callback(self, callback):
        """Set callback function to update stats"""
        self.stats_callback = callback
    
    def _on_checkbox_changed(self, proxy, state):
        """Handle checkbox state change"""
        if state == 2:  # Checked
            self.checked_proxies.add(proxy)
        else:  # Unchecked
            self.checked_proxies.discard(proxy)
        
        # Update header checkbox icon
        self._update_header_checkbox()
    
    def _update_header_checkbox(self):
        """Update header checkbox icon based on checked state"""
        # Get current data source
        if hasattr(self, 'filtered_proxies') and len(self.filtered_proxies) > 0:
            data_source = self.filtered_proxies
        else:
            data_source = self.all_proxies
        
        # Check if all proxies are checked
        all_checked = True
        for proxy_data in data_source:
            if isinstance(proxy_data, dict):
                proxy = proxy_data.get('proxy', '')
            else:
                proxy = proxy_data
            
            if proxy and proxy not in self.checked_proxies:
                all_checked = False
                break
        
        # Update header icon
        if all_checked and len(data_source) > 0:
            self.table.horizontalHeaderItem(0).setText("☑")
        else:
            self.table.horizontalHeaderItem(0).setText("☐")
    
    def on_header_clicked(self, column):
        """Handle header click - toggle all checkboxes when column 0 is clicked"""
        if column == 0:  # Only for checkbox column
            # Get current data source
            if hasattr(self, 'filtered_proxies') and len(self.filtered_proxies) > 0:
                data_source = self.filtered_proxies
            else:
                data_source = self.all_proxies
            
            # Check if any proxy is checked
            any_checked = False
            for proxy_data in data_source:
                if isinstance(proxy_data, dict):
                    proxy = proxy_data.get('proxy', '')
                else:
                    proxy = proxy_data
                
                if proxy in self.checked_proxies:
                    any_checked = True
                    break
            
            # If any checked, uncheck all. Otherwise, check all
            new_state = not any_checked
            
            # Update checked_proxies set for ALL proxies in data source
            for proxy_data in data_source:
                if isinstance(proxy_data, dict):
                    proxy = proxy_data.get('proxy', '')
                else:
                    proxy = proxy_data
                
                if proxy:
                    if new_state:
                        self.checked_proxies.add(proxy)
                    else:
                        self.checked_proxies.discard(proxy)
            
            # Update all visible checkboxes on current page
            for row in range(self.table.rowCount()):
                checkbox = self.table.cellWidget(row, 0)
                proxy_item = self.table.item(row, 2)
                if checkbox and isinstance(checkbox, QCheckBox) and proxy_item:
                    full_proxy = proxy_item.data(Qt.ItemDataRole.UserRole)
                    if full_proxy and full_proxy in self.checked_proxies:
                        checkbox.setChecked(True)
                    else:
                        checkbox.setChecked(False)
            
            # Update header icon
            self._update_header_checkbox()

    def refresh_proxy_list(self):
        """Refresh proxy list from storage"""
        if not self.storage:
            print("⚠️ Storage not set!")
            return
        
        # Reload proxies from files
        self.storage.proxies = self.storage.load_proxies()
        
        # Update display
        if self.refresh_callback:
            self.refresh_callback()
        else:
            self.update_proxies(self.storage.get_proxies())
        
        # Show refresh status
        proxy_count = len(self.storage.get_proxies())
        self.refresh_status_label.setText(f"✓ Đã làm mới ({proxy_count} proxy)")
        self.refresh_status_label.setVisible(True)
        
        # Auto hide after 3 seconds
        QTimer.singleShot(3000, lambda: self.refresh_status_label.setVisible(False))
        
        print(f"✅ Refreshed proxy list: {proxy_count} proxies loaded")
    
    def _has_checked_proxies(self):
        """Check if any proxy has been checked (has status other than Unknown)"""
        if not hasattr(self, 'all_proxies') or not self.all_proxies:
            return False
        
        for proxy_data in self.all_proxies:
            if isinstance(proxy_data, dict):
                status = proxy_data.get('status', 'Unknown')
                if status != 'Unknown':
                    return True
        return False
    
    def apply_filter(self, filter_type):
        """Apply filter to displayed proxies"""
        if not hasattr(self, 'all_proxies'):
            return
        
        # Check if filtering by type/status and no proxies have been checked yet
        filters_requiring_check = ["HTTP", "HTTPS", "SOCKS5", "LIVE", "DIE", "TIMEOUT"]
        if filter_type in filters_requiring_check and not self._has_checked_proxies():
            # Store the filter type to apply after check completes
            self.pending_filter = filter_type
            # Start checking all proxies
            print(f"⏳ Bắt đầu check proxy để lọc theo '{filter_type}'...")
            self.check_all_proxies()
            return
        
        if filter_type == "ALL":
            filtered = self.all_proxies
        # Filter by proxy type
        elif filter_type == "HTTP":
            filtered = [p for p in self.all_proxies 
                       if isinstance(p, dict) and p.get('type') == 'HTTP']
        elif filter_type == "HTTPS":
            filtered = [p for p in self.all_proxies 
                       if isinstance(p, dict) and p.get('type') == 'HTTPS']
        elif filter_type == "SOCKS5":
            filtered = [p for p in self.all_proxies 
                       if isinstance(p, dict) and p.get('type') == 'SOCKS5']
        elif filter_type == "Unknown":
            filtered = [p for p in self.all_proxies 
                       if isinstance(p, dict) and p.get('type') == 'Unknown']
        # Filter by status
        elif filter_type == "LIVE":
            filtered = [p for p in self.all_proxies 
                       if isinstance(p, dict) and p.get('status') == 'LIVE']
        elif filter_type == "DIE":
            filtered = [p for p in self.all_proxies 
                       if isinstance(p, dict) and p.get('status') == 'DIE']
        elif filter_type == "TIMEOUT":
            filtered = [p for p in self.all_proxies 
                       if isinstance(p, dict) and p.get('status') == 'TIMEOUT']
        else:
            filtered = self.all_proxies
        
        # Store filtered proxies
        self.filtered_proxies = filtered
        self.total_items = len(filtered)
        self.current_page = 1  # Reset to first page
        
        # Display filtered proxies with pagination
        self._display_current_page()
        
        # Update filter label with count
        self._update_filter_label(filter_type, len(filtered), len(self.all_proxies))
        
        # Update pagination controls
        self.update_pagination_controls()
    
    def _update_filter_label(self, filter_type, filtered_count, total_count):
        """Update filter info label"""
        if filter_type == "ALL":
            self.filter_info_label.setText(f"({total_count} proxy)")
        else:
            self.filter_info_label.setText(f"({filtered_count}/{total_count} proxy)")

    def update_proxies(self, proxies):
        """Update proxies and store for filtering"""
        # Store all proxies for filtering
        self.all_proxies = proxies
        self.total_items = len(proxies)
        self.current_page = 1  # Reset to first page
        # Clear any existing filter
        if hasattr(self, 'filtered_proxies'):
            delattr(self, 'filtered_proxies')
        # Display them with pagination
        self._display_current_page()
        # Update filter label
        self._update_filter_label("ALL", len(proxies), len(proxies))
        # Update pagination controls
        self.update_pagination_controls()
    
    def _display_proxies(self, proxies):
        """Internal method to display proxies without changing all_proxies"""
        self.table.setRowCount(len(proxies))
        
        # Calculate STT offset based on current page
        stt_offset = (self.current_page - 1) * self.items_per_page
        
        for row, proxy_data in enumerate(proxies):
            # Handle both dict and string formats
            if isinstance(proxy_data, dict):
                proxy = proxy_data.get('proxy', '')
                proxy_type = proxy_data.get('type', 'Unknown')
                status = proxy_data.get('status', 'Unknown')
                real_ip = proxy_data.get('external_ip', '')
            else:
                proxy = proxy_data
                proxy_type = 'Unknown'
                status = 'Unknown'
                real_ip = ''
            
            # Display only ip:port (hide credentials)
            parts = proxy.split(':')
            display_proxy = f"{parts[0]}:{parts[1]}" if len(parts) >= 2 else proxy
            
            # Add checkbox in first column
            checkbox = QCheckBox()
            checkbox.setStyleSheet("QCheckBox { margin-left: 10px; }")
            # Set checked state based on stored state
            if proxy in self.checked_proxies:
                checkbox.setChecked(True)
            # Connect checkbox to update checked_proxies set
            checkbox.stateChanged.connect(lambda state, p=proxy: self._on_checkbox_changed(p, state))
            self.table.setCellWidget(row, 0, checkbox)
            
            # Add STT (số thứ tự) in second column with offset
            stt_item = QTableWidgetItem(str(stt_offset + row + 1))
            stt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, stt_item)
            
            proxy_item = QTableWidgetItem(display_proxy)
            proxy_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            proxy_item.setData(Qt.ItemDataRole.UserRole, proxy)  # Store full proxy
            col_type = QTableWidgetItem(proxy_type)
            col_type.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            real_ip_item = QTableWidgetItem(real_ip if real_ip else "")
            real_ip_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            pid = QTableWidgetItem("")
            pid.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            btn = QPushButton("Check")
            btn.clicked.connect(lambda checked, r=row: self.check_proxy_row(r))
            
            self.table.setItem(row, 2, proxy_item)
            self.table.setItem(row, 3, col_type)
            self.table.setItem(row, 4, status_item)
            self.table.setItem(row, 5, real_ip_item)
            self.table.setItem(row, 6, pid)
            self.table.setCellWidget(row, 7, btn)
    
    def check_proxy_row(self, row):
        """Check proxy at specific row"""
        if not self.proxy_checker:
            return
        
        proxy_item = self.table.item(row, 2)  # Column 2 is now Proxy
        if not proxy_item:
            return
        
        # Get full proxy from hidden data
        full_proxy = proxy_item.data(Qt.ItemDataRole.UserRole)
        if not full_proxy:
            full_proxy = proxy_item.text()
        
        # Update status to "Checking..."
        status_item = self.table.item(row, 4)  # Column 4 is now Status
        status_item.setText("Checking...")
        status_item.setBackground(QColor(255, 255, 200))  # Light yellow
        
        # Run check in thread
        self.check_thread = ProxyCheckThread(row, full_proxy, self.proxy_checker)
        self.check_thread.finished.connect(self.on_check_finished)
        self.check_thread.start()
    
    def check_all_proxies(self):
        """Check all proxies in data source (not just visible ones)"""
        if not self.proxy_checker:
            return
        
        # Get data source (filtered or all)
        if hasattr(self, 'filtered_proxies') and len(self.filtered_proxies) > 0:
            data_source = self.filtered_proxies
        else:
            data_source = self.all_proxies
        
        if not data_source:
            return
        
        # Create proxy map for updating later
        self.proxy_check_map = {}
        
        # Get all proxies from data source
        proxies_to_check = []
        for idx, proxy_data in enumerate(data_source):
            if isinstance(proxy_data, dict):
                proxy = proxy_data.get('proxy', '')
            else:
                proxy = proxy_data
            
            if proxy:
                proxies_to_check.append((idx, proxy))
                self.proxy_check_map[proxy] = idx
        
        if not proxies_to_check:
            return
        
        # Set all visible rows to "Checking..."
        for row in range(self.table.rowCount()):
            status_item = self.table.item(row, 4)
            if status_item:
                status_item.setText("Checking...")
                status_item.setBackground(QColor(255, 255, 200))
        
        # Disable check all button
        self.btn_check_all.setEnabled(False)
        self.btn_check_all.setText("Checking...")
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(proxies_to_check))
        self.progress_bar.setValue(0)
        
        # Run batch check in thread
        self.batch_check_thread = BatchProxyCheckThread(proxies_to_check, self.proxy_checker)
        self.batch_check_thread.single_finished.connect(self.on_check_finished_batch)
        self.batch_check_thread.progress.connect(self.on_check_progress)
        self.batch_check_thread.all_finished.connect(self.on_all_checks_finished)
        self.batch_check_thread.start()
    
    def on_check_progress(self, current, total):
        """Update progress bar"""
        self.progress_bar.setValue(current)
        self.btn_check_all.setText(f"Checking {current}/{total}")
    
    def on_check_finished_batch(self, idx, proxy_type, status, ip, response_time):
        """Update data after batch check is complete"""
        # Get data source
        if hasattr(self, 'filtered_proxies') and len(self.filtered_proxies) > 0:
            data_source = self.filtered_proxies
        else:
            data_source = self.all_proxies
        
        # Update data in data source
        if idx < len(data_source):
            if isinstance(data_source[idx], dict):
                data_source[idx]['type'] = proxy_type
                data_source[idx]['status'] = status
                data_source[idx]['response_time'] = response_time
                if ip and ip != "N/A":
                    data_source[idx]['external_ip'] = ip
                
                proxy_str = data_source[idx].get('proxy', '')
            else:
                proxy_str = data_source[idx]
            
            # Also update in all_proxies if using filtered view
            if hasattr(self, 'filtered_proxies') and len(self.filtered_proxies) > 0:
                # Find and update in all_proxies
                for all_idx, proxy_data in enumerate(self.all_proxies):
                    if isinstance(proxy_data, dict):
                        if proxy_data.get('proxy', '') == proxy_str:
                            self.all_proxies[all_idx]['type'] = proxy_type
                            self.all_proxies[all_idx]['status'] = status
                            self.all_proxies[all_idx]['response_time'] = response_time
                            if ip and ip != "N/A":
                                self.all_proxies[all_idx]['external_ip'] = ip
                            break
        
        # Refresh current page to show updated data
        self._display_current_page()
        
        # Update stats after each check
        if self.stats_callback:
            self.stats_callback()
    
    def on_all_checks_finished(self):
        """Called when all checks are complete"""
        self.btn_check_all.setEnabled(True)
        self.btn_check_all.setText("Check All")
        self.progress_bar.setVisible(False)
        
        # Count live/die proxies from all proxies
        live_count = 0
        die_count = 0
        
        for proxy_data in self.all_proxies:
            if isinstance(proxy_data, dict):
                status = proxy_data.get('status', 'Unknown')
                if status == "LIVE":
                    live_count += 1
                elif status == "DIE" or status == "TIMEOUT":
                    die_count += 1
        
        print(f"✅ Check completed: {live_count} LIVE, {die_count} DIE")
        
        # Update stats panel
        if self.stats_callback:
            self.stats_callback()
        
        # Apply pending filter if exists
        if hasattr(self, 'pending_filter') and self.pending_filter:
            filter_to_apply = self.pending_filter
            self.pending_filter = None  # Clear pending filter
            print(f"✅ Áp dụng filter '{filter_to_apply}' sau khi check xong")
            self.cb_filter.setCurrentText(filter_to_apply)  # This will trigger apply_filter
        else:
            # Refresh display to show final results
            self._display_current_page()
    
    def on_check_finished(self, row, proxy_type, status, ip, response_time):
        """Update table after check is complete"""
        type_item = self.table.item(row, 3)  # Column 3 is now Type
        status_item = self.table.item(row, 4)  # Column 4 is now Status
        real_ip_item = self.table.item(row, 5)  # Column 5 is now Real IP
        
        if type_item:
            type_item.setText(proxy_type)
        
        if status_item:
            status_item.setText(status)
            
            # Set color based on status
            if status == "LIVE":
                # Green for LIVE
                status_item.setBackground(QColor(144, 238, 144))  # Light green
                status_item.setForeground(QColor(0, 100, 0))  # Dark green text
            elif status == "DIE":
                # Red for DIE
                status_item.setBackground(QColor(255, 182, 193))  # Light red
                status_item.setForeground(QColor(139, 0, 0))  # Dark red text
            elif status == "TIMEOUT":
                # Orange for TIMEOUT
                status_item.setBackground(QColor(255, 200, 124))  # Light orange
                status_item.setForeground(QColor(139, 69, 0))  # Dark orange text
            else:
                # Gray for Unknown
                status_item.setBackground(QColor(220, 220, 220))  # Light gray
                status_item.setForeground(QColor(80, 80, 80))  # Dark gray text
        
        # Update Real IP
        if real_ip_item:
            if status == "LIVE" and ip and ip != "N/A":
                real_ip_item.setText(ip)
                real_ip_item.setForeground(QColor(0, 100, 0))  # Dark green
            else:
                real_ip_item.setText("")
                real_ip_item.setForeground(QColor(150, 150, 150))  # Gray
        
        # Update all_proxies data with checked info
        if hasattr(self, 'all_proxies') and row < len(self.all_proxies):
            if isinstance(self.all_proxies[row], dict):
                self.all_proxies[row]['type'] = proxy_type
                self.all_proxies[row]['status'] = status
                self.all_proxies[row]['response_time'] = response_time
                if ip and ip != "N/A":
                    self.all_proxies[row]['external_ip'] = ip
        
        # Update stats after each check
        if self.stats_callback:
            self.stats_callback()

    def delete_selected_proxies(self):
        """Delete selected proxies from table and storage"""
        if not self.storage:
            print("⚠️ Storage not set!")
            return
        
        # Get proxies from checked_proxies set
        if not self.checked_proxies:
            print("⚠️ No proxies selected!")
            return
        
        # Convert set to list
        proxies_to_delete = list(self.checked_proxies)
        
        # Delete from storage
        deleted_count = self.storage.remove_proxies(proxies_to_delete)
        
        # Clear checked_proxies set
        self.checked_proxies.clear()
        
        # Refresh display
        if self.refresh_callback:
            self.refresh_callback()
        else:
            self.update_proxies(self.storage.get_proxies())
        
        print(f"✅ Deleted {deleted_count} proxies")
    
    # ============================
    # HÀM THÊM PROXY VÀO BẢNG
    # ============================

    def add_proxy(self, proxy_string, ptype):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Add checkbox in first column
        checkbox = QCheckBox()
        checkbox.setStyleSheet("QCheckBox { margin-left: 10px; }")
        self.table.setCellWidget(row, 0, checkbox)
        
        # Add STT in second column
        stt = QTableWidgetItem(str(row + 1))
        stt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 1, stt)

        proxy = QTableWidgetItem(proxy_string)
        proxy.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        col_type = QTableWidgetItem(ptype)
        col_type.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        status = QTableWidgetItem("Unknown")
        status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        real_ip = QTableWidgetItem("")
        real_ip.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        pid = QTableWidgetItem("")
        pid.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        btn = QPushButton("Check")

        self.table.setItem(row, 2, proxy)
        self.table.setItem(row, 3, col_type)
        self.table.setItem(row, 4, status)
        self.table.setItem(row, 5, real_ip)
        self.table.setItem(row, 6, pid)
        self.table.setCellWidget(row, 7, btn)
    
    # ============================
    # PAGINATION FUNCTIONS
    # ============================
    
    def _display_current_page(self):
        """Display proxies for current page"""
        if not hasattr(self, 'all_proxies'):
            return
        
        # Get data to display (filtered or all)
        if hasattr(self, 'filtered_proxies') and len(self.filtered_proxies) > 0:
            data_source = self.filtered_proxies
        else:
            data_source = self.all_proxies
        
        # Calculate start and end indices
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        
        # Get page data
        page_data = data_source[start_idx:end_idx]
        
        # Display the page data
        self._display_proxies(page_data)
    
    def on_page_size_changed(self, size_text):
        """Handle page size change"""
        if size_text == "Tất cả":
            # Display all items
            self.items_per_page = max(self.total_items, 1)
        else:
            self.items_per_page = int(size_text)
        self.current_page = 1  # Reset to first page
        self._display_current_page()
        self.update_pagination_controls()
    
    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self._display_current_page()
            self.update_pagination_controls()
    
    def next_page(self):
        """Go to next page"""
        total_pages = self.get_total_pages()
        if self.current_page < total_pages:
            self.current_page += 1
            self._display_current_page()
            self.update_pagination_controls()
    
    def go_to_page(self, page_number):
        """Go to specific page"""
        total_pages = self.get_total_pages()
        if 1 <= page_number <= total_pages:
            self.current_page = page_number
            self._display_current_page()
            self.update_pagination_controls()
    
    def get_total_pages(self):
        """Calculate total number of pages"""
        if self.total_items == 0:
            return 1
        return (self.total_items + self.items_per_page - 1) // self.items_per_page
    
    def update_pagination_controls(self):
        """Update pagination UI controls"""
        total_pages = self.get_total_pages()
        
        # Update prev/next buttons
        self.btn_prev_page.setEnabled(self.current_page > 1)
        self.btn_next_page.setEnabled(self.current_page < total_pages)
        
        # Update page info
        start_item = (self.current_page - 1) * self.items_per_page + 1
        end_item = min(self.current_page * self.items_per_page, self.total_items)
        if self.total_items == 0:
            start_item = 0
            end_item = 0
        self.page_info_label.setText(f"Showing {start_item}-{end_item} of {self.total_items}")
        
        # Update page number buttons
        self._create_page_buttons()
    
    def _create_page_buttons(self):
        """Create page number buttons"""
        # Clear existing buttons
        while self.page_numbers_layout.count():
            child = self.page_numbers_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        total_pages = self.get_total_pages()
        
        # Show max 7 page buttons
        if total_pages <= 7:
            # Show all pages
            for page in range(1, total_pages + 1):
                self._add_page_button(page)
        else:
            # Show smart pagination
            if self.current_page <= 4:
                # Show: 1 2 3 4 5 ... last
                for page in range(1, 6):
                    self._add_page_button(page)
                self.page_numbers_layout.addWidget(QLabel("..."))
                self._add_page_button(total_pages)
            elif self.current_page >= total_pages - 3:
                # Show: 1 ... last-4 last-3 last-2 last-1 last
                self._add_page_button(1)
                self.page_numbers_layout.addWidget(QLabel("..."))
                for page in range(total_pages - 4, total_pages + 1):
                    self._add_page_button(page)
            else:
                # Show: 1 ... current-1 current current+1 ... last
                self._add_page_button(1)
                self.page_numbers_layout.addWidget(QLabel("..."))
                for page in range(self.current_page - 1, self.current_page + 2):
                    self._add_page_button(page)
                self.page_numbers_layout.addWidget(QLabel("..."))
                self._add_page_button(total_pages)
    
    def _add_page_button(self, page_number):
        """Add a single page number button"""
        btn = QPushButton(str(page_number))
        btn.setFixedSize(35, 30)
        btn.clicked.connect(lambda: self.go_to_page(page_number))
        
        if page_number == self.current_page:
            # Current page - highlighted
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: 1px solid #2196F3;
                    border-radius: 3px;
                    font-weight: bold;
                }
            """)
        else:
            # Other pages
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #333;
                    border: 1px solid #d0d0d0;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #e3f2fd;
                    border-color: #2196F3;
                }
            """)
        
        self.page_numbers_layout.addWidget(btn)
