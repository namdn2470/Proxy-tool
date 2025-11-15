from PyQt6.QtWidgets import QVBoxLayout, QTextEdit, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QHBoxLayout
from PyQt6.QtCore import QTimer
import os
import subprocess
from functools import partial
from typing import Dict, Tuple

class MiddlePanel(QVBoxLayout):
    def __init__(self, left):
        super().__init__()
        self.left = left
        self.label = QLabel("Auto Fake IP")
        self.addWidget(self.label)

        # Select exe
        self.select_exe_button = QPushButton("Select .exe file")
        self.addWidget(self.select_exe_button)

        # Fake IP button
        self.fake_ip_button = QPushButton("Fake IP")
        self.addWidget(self.fake_ip_button)

        # Table for processes
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(5)
        self.process_table.setHorizontalHeaderLabels(["PID", "File", "Proxy", "Status", "Actions"])
        self.process_table.setMinimumHeight(300)
        self.addWidget(self.process_table)

        # Logs
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.addWidget(self.log_area)

        # Processes dict
        self.processes: Dict[int, Tuple[str, str, subprocess.Popen]] = {}

        # Timer for checking
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_processes)
        self.timer.start(5000)  # Check every 5 seconds

        # Connect signals
        self.select_exe_button.clicked.connect(self.select_exe)
        self.fake_ip_button.clicked.connect(self.fake_ip)

    def select_exe(self):
        file_path, _ = QFileDialog.getOpenFileName(None, "Select EXE File", "", "Executable Files (*.exe)")
        if file_path:
            self.selected_exe = file_path
            self.log(f"Selected EXE: {file_path}")

    def fake_ip(self):
        if hasattr(self, 'selected_exe') and self.left.table.rowCount() > 0:
            # Get selected proxy from table
            current_row = self.left.table.currentRow()
            if current_row >= 0:
                proxy_item = self.left.table.item(current_row, 1)
                if proxy_item:
                    proxy = proxy_item.text()
                    env = os.environ.copy()
                    env['HTTP_PROXY'] = f'http://{proxy}'
                    process = subprocess.Popen([self.selected_exe], env=env)
                    pid = process.pid
                    self.processes[pid] = (self.selected_exe, proxy, process)
                    self.update_table()
                    self.log(f"Faked IP for {self.selected_exe} with proxy {proxy}, PID: {pid}")

    def check_processes(self):
        to_remove = []
        for pid, (file, proxy, process) in self.processes.items():
            if process.poll() is not None:
                to_remove.append(pid)
        for pid in to_remove:
            del self.processes[pid]
        self.update_table()

    def update_table(self):
        self.process_table.setRowCount(len(self.processes))
        for row, (pid, (file, proxy, process)) in enumerate(self.processes.items()):
            self.process_table.setItem(row, 0, QTableWidgetItem(str(pid)))
            self.process_table.setItem(row, 1, QTableWidgetItem(file))
            self.process_table.setItem(row, 2, QTableWidgetItem(proxy))
            status = "Running" if process.poll() is None else "Stopped"
            self.process_table.setItem(row, 3, QTableWidgetItem(status))
            # Add kill button
            kill_button = QPushButton("Kill")
            kill_button.clicked.connect(partial(self.kill_process, pid))
            self.process_table.setCellWidget(row, 4, kill_button)

    def kill_process(self, pid: int):
        if pid in self.processes:
            _, _, process = self.processes[pid]
            process.terminate()
            self.log(f"Killed process PID: {pid}")
            del self.processes[pid]
            self.update_table()

    def log(self, message: str):
        self.log_area.append(message)
