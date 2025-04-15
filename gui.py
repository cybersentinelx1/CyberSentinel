from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QListWidget, 
    QLabel, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
import json
import os

class PrivacyGuardUI(QMainWindow):
    def __init__(self, app_scanner):
        super().__init__()
        self.app_scanner = app_scanner
        self.privacy_db = self._load_privacy_db()
        self.setWindowTitle("PrivacyGuard Advisor")
        self.setGeometry(300, 300, 600, 400)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🔒 PrivacyGuard Advisor")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Scan Button
        self.scan_button = QPushButton("Scan Installed Apps")
        self.scan_button.clicked.connect(self.run_scan)
        layout.addWidget(self.scan_button)
        
        # App List
        self.app_list = QListWidget()
        self.app_list.itemDoubleClicked.connect(self.show_recommendation)
        layout.addWidget(self.app_list)
        
        # Status Bar
        self.statusBar().showMessage("Ready to scan.")
        central_widget.setLayout(layout)
    
    def _load_privacy_db(self):
        with open("privacy_db.json", "r") as f:
            return json.load(f)
    
    def run_scan(self):
        self.app_list.clear()
        self.statusBar().showMessage("Scanning...")
        QApplication.processEvents()  # Force UI update
        
        apps = self.app_scanner.scan_installed_apps()
        for app in apps:
            app_name = app["name"]
            if app_name in self.privacy_db:
                self.app_list.addItem(f"⚠️ {app_name} - {self.privacy_db[app_name]['risk']} risk")
            else:
                self.app_list.addItem(f"✅ {app_name} - No known issues")
        
        self.statusBar().showMessage(f"Scan complete. Found {len(apps)} apps.")
    
    def show_recommendation(self, item):
        app_name = item.text().split(" - ")[0].replace("⚠️ ", "").strip()
        if app_name in self.privacy_db:
            data = self.privacy_db[app_name]
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle(f"Privacy Risk: {app_name}")
            msg.setText(f"""
                <b>{app_name}</b> has a <b>{data['risk']}</b> privacy risk.<br><br>
                <b>Reason:</b> {data['reason']}<br><br>
                <b>Recommendation:</b> Switch to <b>{data['alternative']}</b>.
            """)
            
            # Add "Install" button
            install_btn = msg.addButton("Install Alternative", QMessageBox.ActionRole)
            install_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(data['alternative_url'])))
            
            msg.addButton(QMessageBox.Close)
            msg.exec_()
