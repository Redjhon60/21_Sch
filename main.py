import sys
import os

# Add project root to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Ensure dirs exist
for d in ['database', 'receipts', 'backups', 'documents', 'assets']:
    os.makedirs(os.path.join(BASE_DIR, d), exist_ok=True)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from models.database import init_db


def on_login_success(user):
    login_win.close()
    from ui.main_window import MainWindow
    global main_win
    main_win = MainWindow(user)
    main_win.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('Le Schéma SGS')
    app.setApplicationVersion('1.0.0')
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    # App icon
    icon_path = os.path.join(BASE_DIR, 'assets', 'school_logo.ico')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Init database
    init_db()

    # Show login
    from ui.login_window import LoginWindow
    login_win = LoginWindow(on_login_success)
    login_win.show()

    sys.exit(app.exec())
