import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QGroupBox, QMessageBox, QFrame, QDoubleSpinBox)
from PySide6.QtCore import Qt
from models.database import Setting


class SettingsWidget(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(30,30,30,30); layout.setSpacing(20)

        title = QLabel('⚙️  Paramètres de l\'Application')
        title.setStyleSheet('color: #00d4ff; font-size: 18px; font-weight: bold; background: transparent;')
        layout.addWidget(title)

        FIELD_STYLE = 'background: #0d1832; border: 1px solid #1e3a5f; border-radius: 6px; color: #e0e6f0; padding: 8px 12px; font-size: 13px;'
        LABEL_STYLE = 'color: #8a9bb0; font-size: 12px; background: transparent;'
        GROUP_STYLE = 'QGroupBox { border: 1px solid #1e3a5f; border-radius: 8px; margin-top: 12px; padding-top: 8px; color: #00d4ff; font-weight: bold; } QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; color: #00d4ff; }'

        # School info
        school_group = QGroupBox('🏫  Informations de l\'École')
        school_group.setStyleSheet(GROUP_STYLE)
        school_form = QFormLayout(school_group); school_form.setSpacing(10)
        for lbl in school_form.labelForField:
            lbl.setStyleSheet(LABEL_STYLE)

        self.school_name = QLineEdit(); self.school_name.setStyleSheet(FIELD_STYLE)
        self.school_address = QLineEdit(); self.school_address.setStyleSheet(FIELD_STYLE)
        self.school_phone = QLineEdit(); self.school_phone.setStyleSheet(FIELD_STYLE)
        self.school_email = QLineEdit(); self.school_email.setStyleSheet(FIELD_STYLE)

        for lbl_text, widget in [('Nom de l\'école:', self.school_name),
                                   ('Adresse:', self.school_address),
                                   ('Téléphone:', self.school_phone),
                                   ('Email:', self.school_email)]:
            lbl = QLabel(lbl_text); lbl.setStyleSheet(LABEL_STYLE)
            school_form.addRow(lbl, widget)
        layout.addWidget(school_group)

        # Fees
        fees_group = QGroupBox('💰  Tarifs par défaut')
        fees_group.setStyleSheet(GROUP_STYLE)
        fees_form = QFormLayout(fees_group); fees_form.setSpacing(10)

        self.insurance_fee = QDoubleSpinBox()
        self.insurance_fee.setRange(0, 9999); self.insurance_fee.setSuffix(' MAD')
        self.insurance_fee.setStyleSheet(FIELD_STYLE)
        self.transport_fee = QDoubleSpinBox()
        self.transport_fee.setRange(0, 9999); self.transport_fee.setSuffix(' MAD')
        self.transport_fee.setStyleSheet(FIELD_STYLE)

        for lbl_text, widget in [('Frais assurance annuelle:', self.insurance_fee),
                                   ('Frais transport mensuel:', self.transport_fee)]:
            lbl = QLabel(lbl_text); lbl.setStyleSheet(LABEL_STYLE)
            fees_form.addRow(lbl, widget)
        layout.addWidget(fees_group)

        save_btn = QPushButton('💾  Enregistrer les paramètres')
        save_btn.setFixedHeight(44)
        save_btn.setStyleSheet("""
            QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0066ff,stop:1 #0033cc);
                color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: bold; }
            QPushButton:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #0080ff,stop:1 #0055dd); }
        """)
        save_btn.clicked.connect(self._save_settings)
        layout.addWidget(save_btn)
        layout.addStretch()

        # Version info
        info_lbl = QLabel('Le Schéma SGS v1.0.0  |  Système de Gestion Scolaire  |  © 2025')
        info_lbl.setAlignment(Qt.AlignCenter)
        info_lbl.setStyleSheet('color: #3a5a7a; font-size: 11px; background: transparent;')
        layout.addWidget(info_lbl)

    def _load_settings(self):
        def get(key, default=''):
            s = self.session.query(Setting).filter_by(key=key).first()
            return s.value if s else default

        self.school_name.setText(get('school_name', 'Le Schéma'))
        self.school_address.setText(get('school_address', ''))
        self.school_phone.setText(get('school_phone', ''))
        self.school_email.setText(get('school_email', ''))
        try: self.insurance_fee.setValue(float(get('insurance_fee', '500')))
        except: self.insurance_fee.setValue(500)
        try: self.transport_fee.setValue(float(get('transport_fee', '300')))
        except: self.transport_fee.setValue(300)

    def _save_settings(self):
        def set_val(key, value):
            s = self.session.query(Setting).filter_by(key=key).first()
            if s: s.value = value
            else: self.session.add(Setting(key=key, value=value))

        set_val('school_name', self.school_name.text())
        set_val('school_address', self.school_address.text())
        set_val('school_phone', self.school_phone.text())
        set_val('school_email', self.school_email.text())
        set_val('insurance_fee', str(self.insurance_fee.value()))
        set_val('transport_fee', str(self.transport_fee.value()))
        self.session.commit()
        QMessageBox.information(self, 'Succès', '✅ Paramètres enregistrés avec succès!')
