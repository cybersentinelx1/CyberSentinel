import sys
from PyQt5.QtWidgets import QApplication
from app_scanner import AppScanner
from gui import PrivacyGuardUI
from logger_config import setup_logging

def main():
    setup_logging()
    app = QApplication(sys.argv)
    scanner = AppScanner()
    window = PrivacyGuardUI(scanner)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
