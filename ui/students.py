import os, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit, QComboBox, QCheckBox,
    QDateEdit, QTextEdit, QMessageBox, QFileDialog, QFrame, QScrollArea, QDoubleSpinBox,
    QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QPixmap, QIcon
from datetime import datetime, date

from models.database import get_session, Student
from themes.style import CLASSES


class StudentDialog(QDialog):
    def __init__(self, parent=None, student=None):
        super().__init__(parent)
        self.student = student
        self.photo_path = student.photo if student and student.photo else None
        self.setWindowTitle('Modifier élève' if student else 'Nouvel élève')
        self.setFixedSize(700, 650)
        self.setStyleSheet("""
            QDialog { background: #0a0e1a; }
            QLabel { color: #c0d0e0; font-size: 12px; background: transparent; }
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox {
                background: #0d1832; border: 1px solid #1e3a5f; border-radius: 6px;
                color: #e0e6f0; padding: 6px 10px; font-size: 13px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border-color: #00d4ff;
            }
            QComboBox QAbstractItemView { background: #0d1832; color: #e0e6f0; }
            QCheckBox { color: #c0d0e0; }
        """)
        self._setup_ui()
        if student:
            self._populate(student)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel('👤  Fiche Élève')
        title.setStyleSheet('color: #00d4ff; font-size: 16px; font-weight: bold; background: transparent;')
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')
        content = QWidget()
        content.setStyleSheet('background: transparent;')
        form = QFormLayout(content)
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        def field(placeholder='', widget=None):
            if widget is None:
                w = QLineEdit()
                w.setPlaceholderText(placeholder)
            else:
                w = widget
            return w

        self.first_name = field('Prénom')
        self.last_name = field('Nom de famille')
        self.gender = QComboBox(); self.gender.addItems(['Masculin', 'Féminin'])
        self.birth_date = QDateEdit(); self.birth_date.setCalendarPopup(True)
        self.birth_date.setDate(QDate(2010, 1, 1))
        self.class_name = QComboBox(); self.class_name.addItems(CLASSES)
        self.address = QTextEdit(); self.address.setMaximumHeight(60)
        self.parent_name = field('Nom du parent/tuteur')
        self.parent_phone = field('Téléphone parent')
        self.emergency_phone = field('Téléphone urgence')
        self.monthly_fee = QDoubleSpinBox()
        self.monthly_fee.setRange(0, 99999); self.monthly_fee.setSuffix(' MAD')
        self.transport_cb = QCheckBox('Inscrit au transport')
        self.insurance_cb = QCheckBox('Assurance payée')
        self.notes = QTextEdit(); self.notes.setMaximumHeight(60)

        # Photo
        photo_row = QHBoxLayout()
        self.photo_preview = QLabel()
        self.photo_preview.setFixedSize(80, 80)
        self.photo_preview.setStyleSheet('border: 1px solid #1e3a5f; border-radius: 40px; background: #0d1832;')
        self.photo_preview.setAlignment(Qt.AlignCenter)
        self.photo_preview.setText('📷')
        pick_photo = QPushButton('Choisir photo')
        pick_photo.clicked.connect(self._pick_photo)
        photo_row.addWidget(self.photo_preview)
        photo_row.addWidget(pick_photo)
        photo_row.addStretch()

        form.addRow('Prénom *:', self.first_name)
        form.addRow('Nom *:', self.last_name)
        form.addRow('Sexe:', self.gender)
        form.addRow('Date de naissance:', self.birth_date)
        form.addRow('Classe:', self.class_name)
        form.addRow('Adresse:', self.address)
        form.addRow('Parent/Tuteur:', self.parent_name)
        form.addRow('Tél. parent:', self.parent_phone)
        form.addRow('Tél. urgence:', self.emergency_phone)
        form.addRow('Frais mensuel:', self.monthly_fee)
        form.addRow('', self.transport_cb)
        form.addRow('', self.insurance_cb)
        form.addRow('Notes:', self.notes)
        form.addRow('Photo:', photo_row)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Buttons
        btn_row = QHBoxLayout()
        cancel_btn = QPushButton('Annuler')
        cancel_btn.setStyleSheet('background: #1e3a5f; color: #c0d0e0;')
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton('💾  Enregistrer')
        save_btn.clicked.connect(self._save)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _pick_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Choisir une photo', '', 'Images (*.png *.jpg *.jpeg *.bmp)')
        if path:
            self.photo_path = path
            pix = QPixmap(path).scaled(80, 80, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.photo_preview.setPixmap(pix)

    def _populate(self, s):
        self.first_name.setText(s.first_name or '')
        self.last_name.setText(s.last_name or '')
        if s.gender: self.gender.setCurrentText(s.gender)
        if s.birth_date: self.birth_date.setDate(QDate(s.birth_date.year, s.birth_date.month, s.birth_date.day))
        if s.class_name: self.class_name.setCurrentText(s.class_name)
        self.address.setText(s.address or '')
        self.parent_name.setText(s.parent_name or '')
        self.parent_phone.setText(s.parent_phone or '')
        self.emergency_phone.setText(s.emergency_phone or '')
        self.monthly_fee.setValue(s.monthly_fee or 0)
        self.transport_cb.setChecked(s.transport or False)
        self.insurance_cb.setChecked(s.insurance_paid or False)
        self.notes.setText(s.notes or '')
        if s.photo and os.path.exists(s.photo):
            pix = QPixmap(s.photo).scaled(80, 80, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            self.photo_preview.setPixmap(pix)

    def _save(self):
        if not self.first_name.text().strip() or not self.last_name.text().strip():
            QMessageBox.warning(self, 'Erreur', 'Prénom et nom sont obligatoires.')
            return
        self.accept()

    def get_data(self):
        bd = self.birth_date.date()
        return {
            'first_name': self.first_name.text().strip(),
            'last_name': self.last_name.text().strip(),
            'gender': self.gender.currentText(),
            'birth_date': date(bd.year(), bd.month(), bd.day()),
            'class_name': self.class_name.currentText(),
            'address': self.address.toPlainText(),
            'parent_name': self.parent_name.text().strip(),
            'parent_phone': self.parent_phone.text().strip(),
            'emergency_phone': self.emergency_phone.text().strip(),
            'monthly_fee': self.monthly_fee.value(),
            'transport': self.transport_cb.isChecked(),
            'insurance_paid': self.insurance_cb.isChecked(),
            'notes': self.notes.toPlainText(),
            'photo': self.photo_path,
        }


class StudentsWidget(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self._setup_ui()
        self._load_students()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Toolbar
        toolbar = QHBoxLayout()
        title = QLabel('🎓  Gestion des Élèves')
        title.setStyleSheet('color: #00d4ff; font-size: 16px; font-weight: bold; background: transparent;')

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('🔍  Rechercher un élève...')
        self.search_input.setFixedWidth(280)
        self.search_input.setStyleSheet("""
            QLineEdit { background: #0d1832; border: 1px solid #1e3a5f; border-radius: 20px;
                color: #e0e6f0; padding: 7px 15px; font-size: 13px; }
            QLineEdit:focus { border-color: #00d4ff; }
        """)
        self.search_input.textChanged.connect(self._filter)

        self.class_filter = QComboBox()
        self.class_filter.addItem('Toutes les classes')
        self.class_filter.addItems(CLASSES)
        self.class_filter.currentTextChanged.connect(self._filter)

        add_btn = QPushButton('➕  Ajouter élève')
        add_btn.clicked.connect(self._add_student)

        toolbar.addWidget(title)
        toolbar.addStretch()
        toolbar.addWidget(self.search_input)
        toolbar.addWidget(self.class_filter)
        toolbar.addWidget(add_btn)
        layout.addLayout(toolbar)

        # Stats strip
        self.stats_lbl = QLabel()
        self.stats_lbl.setStyleSheet('color: #6a8aaa; font-size: 11px; background: transparent;')
        layout.addWidget(self.stats_lbl)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(['Code','Prénom','Nom','Classe','Parent','Téléphone','Transport','Assurance','Frais/Mois'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet("""
            QTableWidget { background: #0d1228; border: 1px solid #1e3a5f; border-radius: 8px; gridline-color: #1a2744; }
            QTableWidget::item { padding: 8px 12px; color: #c0d0e0; border-bottom: 1px solid #1a2744; }
            QTableWidget::item:selected { background: rgba(0,212,255,0.2); color: white; }
            QTableWidget::item:alternate { background: #0a1020; }
            QHeaderView::section { background: #162040; color: #00d4ff; padding: 10px 12px;
                border: none; border-right: 1px solid #1e3a5f; border-bottom: 2px solid #00d4ff;
                font-weight: bold; font-size: 11px; }
        """)
        self.table.doubleClicked.connect(self._edit_student)
        layout.addWidget(self.table)

        # Action buttons
        action_row = QHBoxLayout()
        edit_btn = QPushButton('✏️  Modifier')
        edit_btn.clicked.connect(self._edit_student)
        del_btn = QPushButton('🗑️  Supprimer')
        del_btn.setObjectName('btn_danger')
        del_btn.setStyleSheet('background: #aa1100; color: white; border-radius: 6px; padding: 8px 18px;')
        del_btn.clicked.connect(self._delete_student)
        pay_btn = QPushButton('💳  Paiement')
        pay_btn.setObjectName('btn_success')
        pay_btn.setStyleSheet('background: #006633; color: white; border-radius: 6px; padding: 8px 18px;')
        pay_btn.clicked.connect(self._open_payment)

        action_row.addStretch()
        action_row.addWidget(edit_btn)
        action_row.addWidget(del_btn)
        action_row.addWidget(pay_btn)
        layout.addLayout(action_row)

        self.all_students = []

    def _generate_code(self):
        year = datetime.now().year
        count = self.session.query(Student).count()
        return f'STU-{year}-{count+1:04d}'

    def _load_students(self):
        self.all_students = self.session.query(Student).filter_by(active=True).all()
        self._populate_table(self.all_students)
        total = len(self.all_students)
        transport = sum(1 for s in self.all_students if s.transport)
        self.stats_lbl.setText(f'Total: {total} élèves  |  Transport: {transport}  |  Double-cliquez pour modifier')

    def _populate_table(self, students):
        self.table.setRowCount(len(students))
        for row, s in enumerate(students):
            self.table.setItem(row, 0, QTableWidgetItem(s.code or ''))
            self.table.setItem(row, 1, QTableWidgetItem(s.first_name or ''))
            self.table.setItem(row, 2, QTableWidgetItem(s.last_name or ''))
            self.table.setItem(row, 3, QTableWidgetItem(s.class_name or ''))
            self.table.setItem(row, 4, QTableWidgetItem(s.parent_name or ''))
            self.table.setItem(row, 5, QTableWidgetItem(s.parent_phone or ''))
            self.table.setItem(row, 6, QTableWidgetItem('✅' if s.transport else '❌'))
            self.table.setItem(row, 7, QTableWidgetItem('✅' if s.insurance_paid else '❌'))
            self.table.setItem(row, 8, QTableWidgetItem(f'{s.monthly_fee:.0f} MAD'))
            self.table.setRowHeight(row, 38)

    def _filter(self):
        search = self.search_input.text().lower()
        cls_filter = self.class_filter.currentText()
        filtered = [s for s in self.all_students
                    if (search in (s.first_name or '').lower() or
                        search in (s.last_name or '').lower() or
                        search in (s.code or '').lower() or
                        search in (s.parent_name or '').lower())
                    and (cls_filter == 'Toutes les classes' or s.class_name == cls_filter)]
        self._populate_table(filtered)

    def _get_selected_student(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, 'Info', 'Veuillez sélectionner un élève.')
            return None
        code = self.table.item(row, 0).text()
        return self.session.query(Student).filter_by(code=code).first()

    def _add_student(self):
        dlg = StudentDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            s = Student(**data)
            s.code = self._generate_code()
            s.registration_date = date.today()
            self.session.add(s)
            self.session.commit()
            self._load_students()
            QMessageBox.information(self, 'Succès', f'Élève ajouté avec succès!\nCode: {s.code}')

    def _edit_student(self):
        s = self._get_selected_student()
        if not s: return
        dlg = StudentDialog(self, s)
        if dlg.exec():
            data = dlg.get_data()
            for k, v in data.items():
                setattr(s, k, v)
            self.session.commit()
            self._load_students()

    def _delete_student(self):
        s = self._get_selected_student()
        if not s: return
        reply = QMessageBox.question(self, 'Confirmation',
            f'Supprimer l\'élève {s.first_name} {s.last_name}?',
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            s.active = False
            self.session.commit()
            self._load_students()

    def _open_payment(self):
        s = self._get_selected_student()
        if not s: return
        dlg = PaymentDialog(self, s, self.session)
        dlg.exec()
        self._load_students()


class PaymentDialog(QDialog):
    def __init__(self, parent, student, session):
        super().__init__(parent)
        self.student = student
        self.session = session
        self.setWindowTitle(f'Paiement — {student.first_name} {student.last_name}')
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog { background: #0a0e1a; }
            QLabel { color: #c0d0e0; font-size: 13px; background: transparent; }
            QLineEdit, QComboBox, QDoubleSpinBox {
                background: #0d1832; border: 1px solid #1e3a5f; border-radius: 6px;
                color: #e0e6f0; padding: 7px 10px; font-size: 13px;
            }
            QComboBox QAbstractItemView { background: #0d1832; color: #e0e6f0; }
        """)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(14)

        title = QLabel(f'💳  Enregistrer un Paiement')
        title.setStyleSheet('color: #00d4ff; font-size: 16px; font-weight: bold; background: transparent;')
        layout.addWidget(title)

        info = QLabel(f'Élève: {self.student.first_name} {self.student.last_name}  |  Classe: {self.student.class_name}  |  Code: {self.student.code}')
        info.setStyleSheet('color: #8a9bb0; font-size: 11px; background: transparent;')
        layout.addWidget(info)

        form = QFormLayout()
        form.setSpacing(10)
        self.pay_type = QComboBox()
        self.pay_type.addItems(['Mensualité', 'Assurance', 'Transport'])
        self.pay_type.currentTextChanged.connect(self._update_amount)

        from themes.style import MONTHS
        self.month_combo = QComboBox()
        self.month_combo.addItems(MONTHS)
        self.month_combo.setCurrentIndex(datetime.now().month - 1 if datetime.now().month <= 8 else 0)

        self.year_input = QLineEdit(str(datetime.now().year))
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 99999)
        self.amount_input.setSuffix(' MAD')
        self.amount_input.setValue(self.student.monthly_fee or 0)

        form.addRow('Type de paiement:', self.pay_type)
        form.addRow('Mois:', self.month_combo)
        form.addRow('Année:', self.year_input)
        form.addRow('Montant:', self.amount_input)
        layout.addLayout(form)

        # Receipt info
        self.receipt_lbl = QLabel()
        self.receipt_lbl.setStyleSheet('color: #6a8aaa; font-size: 11px; background: transparent;')
        layout.addWidget(self.receipt_lbl)
        layout.addStretch()

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton('Annuler')
        cancel_btn.setStyleSheet('background: #1e3a5f; color: #c0d0e0;')
        cancel_btn.clicked.connect(self.reject)
        pay_btn = QPushButton('💾  Enregistrer & Générer Reçu')
        pay_btn.clicked.connect(self._save_payment)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(pay_btn)
        layout.addLayout(btn_row)

    def _update_amount(self, pay_type):
        from models.database import get_session, Setting
        s = get_session()
        if pay_type == 'Mensualité':
            self.amount_input.setValue(self.student.monthly_fee or 0)
        elif pay_type == 'Assurance':
            ins = s.query(Setting).filter_by(key='insurance_fee').first()
            self.amount_input.setValue(float(ins.value) if ins else 500)
        elif pay_type == 'Transport':
            tr = s.query(Setting).filter_by(key='transport_fee').first()
            self.amount_input.setValue(float(tr.value) if tr else 300)
        s.close()

    def _save_payment(self):
        from models.database import Payment, Receipt
        from services.receipt_service import generate_receipt_pdf

        pay_type_map = {'Mensualité': 'monthly', 'Assurance': 'insurance', 'Transport': 'transport'}
        pay_type_label = self.pay_type.currentText()
        pay_type = pay_type_map.get(pay_type_label, 'monthly')

        payment = Payment(
            student_id=self.student.id,
            payment_type=pay_type,
            amount=self.amount_input.value(),
            month=self.month_combo.currentText(),
            year=int(self.year_input.text() or datetime.now().year),
            payment_date=datetime.now(),
        )
        self.session.add(payment)
        self.session.flush()

        try:
            filepath, rec_num = generate_receipt_pdf(self.session, self.student, payment, pay_type_label)
            payment.receipt_number = rec_num
            receipt = Receipt(
                receipt_number=rec_num,
                student_id=self.student.id,
                payment_id=payment.id,
                amount=payment.amount,
                payment_type=pay_type,
                pdf_path=filepath,
            )
            self.session.add(receipt)
            self.session.commit()

            reply = QMessageBox.question(self, 'Reçu Généré',
                f'✅ Paiement enregistré!\nReçu: {rec_num}\nFichier: {filepath}\n\nOuvrir le reçu PDF?',
                QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                import subprocess, platform
                if platform.system() == 'Linux':
                    subprocess.Popen(['xdg-open', filepath])
                elif platform.system() == 'Darwin':
                    subprocess.Popen(['open', filepath])
                else:
                    os.startfile(filepath)
            self.accept()
        except Exception as e:
            self.session.commit()
            QMessageBox.information(self, 'Paiement enregistré', f'Paiement enregistré.\nErreur reçu PDF: {e}')
            self.accept()
