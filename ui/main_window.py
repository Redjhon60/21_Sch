import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QSizePolicy, QScrollArea)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QPixmap, QIcon, QFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, 'assets', 'school_logo.png')
ICON_PATH = os.path.join(BASE_DIR, 'assets', 'school_logo.ico')


class SidebarButton(QPushButton):
    def __init__(self, icon, text, parent=None):
        super().__init__(f'  {icon}  {text}', parent)
        self.setObjectName('nav_btn')
        self.setCheckable(True)
        self.setFixedHeight(46)
        self.setStyleSheet("""
            QPushButton#nav_btn {
                background: transparent; border: none; color: #8a9bb0;
                text-align: left; padding: 0 16px;
                border-radius: 0; font-size: 13px;
                border-left: 3px solid transparent;
            }
            QPushButton#nav_btn:hover { background: rgba(0,212,255,0.08); color: #00d4ff; border-left-color: #00d4ff; }
            QPushButton#nav_btn:checked { background: rgba(0,212,255,0.15); color: #00d4ff;
                border-left: 3px solid #00d4ff; font-weight: bold; }
        """)


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle('Le Schéma — Système de Gestion Scolaire')
        self.setMinimumSize(1280, 780)
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        from models.database import get_session
        self.session = get_session()

        self._init_ui()
        self._navigate(0)

    def closeEvent(self, event):
        self.session.close()
        super().closeEvent(event)

    def _init_ui(self):
        from themes.style import DARK_THEME
        self.setStyleSheet(DARK_THEME)

        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Sidebar ──────────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setObjectName('sidebar')
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo header
        logo_frame = QFrame()
        logo_frame.setStyleSheet('background: transparent; border-bottom: 1px solid #1e3a5f;')
        logo_frame.setFixedHeight(90)
        logo_layout = QHBoxLayout(logo_frame)
        logo_layout.setContentsMargins(12, 10, 12, 10)

        logo_lbl = QLabel()
        if os.path.exists(LOGO_PATH):
            pix = QPixmap(LOGO_PATH).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_lbl.setPixmap(pix)
        logo_lbl.setFixedSize(54, 54)

        logo_text = QVBoxLayout()
        school_lbl = QLabel('Le Schéma')
        school_lbl.setStyleSheet('color: #00d4ff; font-size: 13px; font-weight: bold; background: transparent;')
        sub_lbl = QLabel('Gestion Scolaire')
        sub_lbl.setStyleSheet('color: #4a6a8a; font-size: 10px; background: transparent;')
        logo_text.addWidget(school_lbl)
        logo_text.addWidget(sub_lbl)

        logo_layout.addWidget(logo_lbl)
        logo_layout.addLayout(logo_text)
        sidebar_layout.addWidget(logo_frame)

        # Nav section label
        def section_sep(text):
            lbl = QLabel(f'  {text}')
            lbl.setStyleSheet('color: #2a4a6a; font-size: 10px; font-weight: bold; letter-spacing: 1px; padding: 10px 0 4px 16px; background: transparent;')
            return lbl

        nav_items = [
            ('🏠', 'Tableau de Bord'),
            ('🎓', 'Élèves'),
            ('💳', 'Paiements'),
            ('👥', 'Personnel'),
            ('💸', 'Dépenses'),
            ('🚌', 'Transport'),
            ('📅', 'Emploi du Temps'),
            ('📊', 'Rapports'),
            ('⚙️', 'Paramètres'),
        ]

        sidebar_layout.addWidget(section_sep('NAVIGATION'))

        self.nav_buttons = []
        for idx, (icon, text) in enumerate(nav_items):
            btn = SidebarButton(icon, text)
            btn.clicked.connect(lambda checked, i=idx: self._navigate(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()

        # User info at bottom
        user_frame = QFrame()
        user_frame.setStyleSheet('background: #070b18; border-top: 1px solid #1e3a5f;')
        user_frame.setFixedHeight(70)
        user_layout = QVBoxLayout(user_frame)
        user_layout.setContentsMargins(14, 8, 14, 8)

        role_icons = {'admin': '👑', 'comptable': '💼', 'secretaire': '📋'}
        role_icon = role_icons.get(self.user.role, '👤')
        user_name_lbl = QLabel(f'{role_icon}  {self.user.full_name or self.user.username}')
        user_name_lbl.setStyleSheet('color: #c0d0e0; font-size: 12px; font-weight: bold; background: transparent;')
        user_role_lbl = QLabel(self.user.role.capitalize())
        user_role_lbl.setStyleSheet('color: #4a6a8a; font-size: 10px; background: transparent;')

        logout_btn = QPushButton('Déconnexion')
        logout_btn.setFixedHeight(22)
        logout_btn.setStyleSheet('background: transparent; color: #ff4444; border: none; font-size: 10px; text-align: left; padding: 0;')
        logout_btn.clicked.connect(self._logout)

        user_layout.addWidget(user_name_lbl)
        user_layout.addWidget(user_role_lbl)
        user_layout.addWidget(logout_btn)
        sidebar_layout.addWidget(user_frame)

        # ── Main content area ─────────────────────────────────────
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Top navbar
        topbar = QFrame()
        topbar.setObjectName('topbar')
        topbar.setFixedHeight(55)
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(20, 0, 20, 0)

        self.page_title_lbl = QLabel('Tableau de Bord')
        self.page_title_lbl.setStyleSheet('color: #ffffff; font-size: 17px; font-weight: bold; background: transparent;')

        from datetime import datetime
        date_lbl = QLabel(datetime.now().strftime('%A %d %B %Y'))
        date_lbl.setStyleSheet('color: #4a6a8a; font-size: 12px; background: transparent;')

        topbar_layout.addWidget(self.page_title_lbl)
        topbar_layout.addStretch()
        topbar_layout.addWidget(date_lbl)

        # Stacked pages
        self.stack = QStackedWidget()
        self.stack.setStyleSheet('background: #0a0e1a;')

        self._pages = {}
        content_layout.addWidget(topbar)
        content_layout.addWidget(self.stack, 1)

        root_layout.addWidget(sidebar)
        root_layout.addWidget(content_area, 1)

    def _get_page(self, idx):
        if idx in self._pages:
            return self._pages[idx]

        page_titles = ['Tableau de Bord', 'Gestion des Élèves', 'Historique Paiements',
                       'Personnel & Enseignants', 'Dépenses', 'Transport',
                       'Emploi du Temps', 'Rapports & Exports', 'Paramètres']

        if idx == 0:
            from ui.dashboard import DashboardWidget
            widget = DashboardWidget(self.session)
        elif idx == 1:
            from ui.students import StudentsWidget
            widget = StudentsWidget(self.session)
        elif idx == 2:
            from ui.payments_history import PaymentsHistoryWidget
            widget = PaymentsHistoryWidget(self.session)
        elif idx == 3:
            from ui.employees import EmployeesWidget
            widget = EmployeesWidget(self.session)
        elif idx == 4:
            from ui.expenses import ExpensesWidget
            widget = ExpensesWidget(self.session)
        elif idx == 5:
            from ui.transport import TransportWidget
            widget = TransportWidget(self.session)
        elif idx == 6:
            from ui.timetable import TimetableWidget
            widget = TimetableWidget(self.session)
        elif idx == 7:
            from ui.reports import ReportsWidget
            widget = ReportsWidget(self.session)
        elif idx == 8:
            from ui.settings_widget import SettingsWidget
            widget = SettingsWidget(self.session)
        else:
            widget = QLabel(f'Page {idx}')

        self.stack.addWidget(widget)
        self._pages[idx] = widget
        return widget

    def _navigate(self, idx):
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == idx)

        page_titles = ['Tableau de Bord', 'Gestion des Élèves', 'Historique Paiements',
                       'Personnel & Enseignants', 'Dépenses', 'Transport',
                       'Emploi du Temps', 'Rapports & Exports', 'Paramètres']
        self.page_title_lbl.setText(page_titles[idx] if idx < len(page_titles) else '')

        widget = self._get_page(idx)
        self.stack.setCurrentWidget(widget)

    def _logout(self):
        self.session.close()
        self.close()
        from ui.login_window import LoginWindow
        self._login = LoginWindow(self._on_relogin)
        self._login.show()

    def _on_relogin(self, user):
        self._login.close()
        from models.database import get_session
        self.session = get_session()
        self.user = user
        self._pages.clear()
        while self.stack.count():
            w = self.stack.widget(0)
            self.stack.removeWidget(w)
        self._navigate(0)
        self.show()
