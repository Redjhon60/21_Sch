import sys, os, hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QFrame, QGraphicsOpacityEffect, QComboBox)
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, Property
from PySide6.QtGui import QPixmap, QFont, QColor, QPainter, QLinearGradient, QBrush

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, 'assets', 'school_logo.png')


class LoginWindow(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.setWindowTitle('Le Schéma — Connexion')
        self.setFixedSize(900, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self._drag_pos = None
        self._setup_ui()
        self._setup_animations()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self._drag_pos and e.buttons() == Qt.LeftButton:
            self.move(e.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, e):
        self._drag_pos = None

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left panel — branding
        left = QFrame()
        left.setFixedWidth(420)
        left.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #001a4d, stop:0.5 #002266, stop:1 #000d33);
                border: none;
            }
        """)
        left_layout = QVBoxLayout(left)
        left_layout.setAlignment(Qt.AlignCenter)
        left_layout.setSpacing(16)

        logo_label = QLabel()
        if os.path.exists(LOGO_PATH):
            pix = QPixmap(LOGO_PATH).scaled(160, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
        logo_label.setAlignment(Qt.AlignCenter)

        school_name = QLabel('Le Schéma')
        school_name.setAlignment(Qt.AlignCenter)
        school_name.setStyleSheet('color: #00d4ff; font-size: 28px; font-weight: bold; letter-spacing: 3px; background: transparent;')

        motto = QLabel('Innover · Créer · Exceller')
        motto.setAlignment(Qt.AlignCenter)
        motto.setStyleSheet('color: #6a9cc0; font-size: 13px; font-style: italic; background: transparent;')

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFixedWidth(200)
        divider.setStyleSheet('background: #1e4080; border: none; max-height: 1px;')

        sys_label = QLabel('Système de Gestion Scolaire')
        sys_label.setAlignment(Qt.AlignCenter)
        sys_label.setStyleSheet('color: #8ab0d0; font-size: 12px; background: transparent;')

        version_label = QLabel('v1.0.0 — 2025/2026')
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet('color: #4a6a8a; font-size: 10px; background: transparent;')

        left_layout.addStretch()
        left_layout.addWidget(logo_label)
        left_layout.addWidget(school_name)
        left_layout.addWidget(motto)
        left_layout.addWidget(divider, 0, Qt.AlignCenter)
        left_layout.addWidget(sys_label)
        left_layout.addWidget(version_label)
        left_layout.addStretch()

        # Right panel — login form
        right = QFrame()
        right.setStyleSheet('QFrame { background: #0a0e1a; border: none; }')
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(60, 0, 60, 0)
        right_layout.setAlignment(Qt.AlignCenter)
        right_layout.setSpacing(16)

        # Close button
        close_btn = QPushButton('✕')
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton { background: #1e3a5f; color: #8ab0d0; border-radius: 15px; font-size: 14px; padding: 0; }
            QPushButton:hover { background: #cc2200; color: white; }
        """)
        close_btn.clicked.connect(sys.exit)
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        top_bar.addWidget(close_btn)
        right_layout.addLayout(top_bar)

        welcome = QLabel('Bienvenue')
        welcome.setStyleSheet('color: #ffffff; font-size: 26px; font-weight: bold; background: transparent;')
        welcome.setAlignment(Qt.AlignCenter)

        sub = QLabel('Connectez-vous à votre espace')
        sub.setStyleSheet('color: #6a8aaa; font-size: 13px; background: transparent;')
        sub.setAlignment(Qt.AlignCenter)

        right_layout.addStretch()
        right_layout.addWidget(welcome)
        right_layout.addWidget(sub)
        right_layout.addSpacing(20)

        # Username
        user_label = QLabel('Nom d\'utilisateur')
        user_label.setStyleSheet('color: #8a9bb0; font-size: 12px; background: transparent;')
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('admin')
        self.username_input.setFixedHeight(44)
        self.username_input.setStyleSheet("""
            QLineEdit {
                background: #0d1832; border: 1px solid #1e3a5f; border-radius: 8px;
                color: #e0e6f0; padding: 0 15px; font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #00d4ff; background: #0f1e3a; }
        """)

        # Password
        pass_label = QLabel('Mot de passe')
        pass_label.setStyleSheet('color: #8a9bb0; font-size: 12px; background: transparent;')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('••••••••')
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(44)
        self.password_input.setStyleSheet("""
            QLineEdit {
                background: #0d1832; border: 1px solid #1e3a5f; border-radius: 8px;
                color: #e0e6f0; padding: 0 15px; font-size: 14px;
            }
            QLineEdit:focus { border: 1px solid #00d4ff; background: #0f1e3a; }
        """)
        self.password_input.returnPressed.connect(self._do_login)

        # Remember + role
        options_row = QHBoxLayout()
        self.remember_cb = QCheckBox('Se souvenir de moi')
        self.remember_cb.setStyleSheet('color: #8a9bb0; background: transparent;')
        options_row.addWidget(self.remember_cb)
        options_row.addStretch()

        # Login button
        self.login_btn = QPushButton('  SE CONNECTER')
        self.login_btn.setFixedHeight(46)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0066ff,stop:1 #0033cc);
                color: white; border: none; border-radius: 8px;
                font-size: 14px; font-weight: bold; letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0080ff,stop:1 #0055dd);
            }
            QPushButton:pressed { background: #0033aa; }
        """)
        self.login_btn.clicked.connect(self._do_login)

        # Error label
        self.error_label = QLabel('')
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet('color: #ff4444; font-size: 12px; background: transparent;')

        # Default credentials hint
        hint = QLabel('Admin: admin/admin123 | Comptable: comptable/compta123')
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet('color: #3a5a7a; font-size: 10px; background: transparent;')

        right_layout.addWidget(user_label)
        right_layout.addWidget(self.username_input)
        right_layout.addWidget(pass_label)
        right_layout.addWidget(self.password_input)
        right_layout.addLayout(options_row)
        right_layout.addSpacing(8)
        right_layout.addWidget(self.login_btn)
        right_layout.addWidget(self.error_label)
        right_layout.addStretch()
        right_layout.addWidget(hint)
        right_layout.addSpacing(20)

        main_layout.addWidget(left)
        main_layout.addWidget(right)

        # Opacity for animation
        self.opacity_effect = QGraphicsOpacityEffect()
        right.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)

    def _setup_animations(self):
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b'opacity')
        self.fade_anim.setDuration(800)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        QTimer.singleShot(100, self.fade_anim.start)

    def _do_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.error_label.setText('⚠ Veuillez remplir tous les champs')
            return

        from models.database import get_session, User
        session = get_session()
        pw_hash = hashlib.sha256(password.encode()).hexdigest()
        user = session.query(User).filter_by(username=username, password=pw_hash, active=True).first()
        session.close()

        if user:
            self.error_label.setText('')
            self.on_login_success(user)
        else:
            self.error_label.setText('✕ Identifiants incorrects')
            self.password_input.clear()
            self._shake()

    def _shake(self):
        orig = self.pos()
        for i, dx in enumerate([8,-8,6,-6,4,-4,2,-2,0]):
            QTimer.singleShot(i*40, lambda x=dx: self.move(orig.x()+x, orig.y()))
