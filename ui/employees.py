import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QTextEdit, QMessageBox, QDoubleSpinBox, QHeaderView, QAbstractItemView,
    QTabWidget, QScrollArea, QCheckBox, QFrame)
from PySide6.QtCore import Qt, QDate
from datetime import datetime, date

from models.database import get_session, Employee, Salary


DIALOG_STYLE = """
    QDialog { background: #0a0e1a; }
    QLabel { color: #c0d0e0; font-size: 12px; background: transparent; }
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox {
        background: #0d1832; border: 1px solid #1e3a5f; border-radius: 6px;
        color: #e0e6f0; padding: 6px 10px; font-size: 13px;
    }
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus { border-color: #00d4ff; }
    QComboBox QAbstractItemView { background: #0d1832; color: #e0e6f0; }
"""
TABLE_STYLE = """
    QTableWidget { background: #0d1228; border: 1px solid #1e3a5f; border-radius: 8px; gridline-color: #1a2744; }
    QTableWidget::item { padding: 8px 12px; color: #c0d0e0; border-bottom: 1px solid #1a2744; }
    QTableWidget::item:selected { background: rgba(0,212,255,0.2); color: white; }
    QTableWidget::item:alternate { background: #0a1020; }
    QHeaderView::section { background: #162040; color: #00d4ff; padding: 10px 12px;
        border: none; border-right: 1px solid #1e3a5f; border-bottom: 2px solid #00d4ff;
        font-weight: bold; font-size: 11px; }
"""


class EmployeeDialog(QDialog):
    def __init__(self, parent=None, employee=None):
        super().__init__(parent)
        self.employee = employee
        self.setWindowTitle('Modifier' if employee else 'Nouvel employé')
        self.setFixedSize(560, 520)
        self.setStyleSheet(DIALOG_STYLE)
        self._setup_ui()
        if employee:
            self._populate(employee)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel('👤  Fiche Employé / Enseignant')
        title.setStyleSheet('color: #00d4ff; font-size: 16px; font-weight: bold; background: transparent;')
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')
        content = QWidget()
        content.setStyleSheet('background: transparent;')
        form = QFormLayout(content)
        form.setSpacing(10)

        self.first_name = QLineEdit(); self.first_name.setPlaceholderText('Prénom')
        self.last_name = QLineEdit(); self.last_name.setPlaceholderText('Nom')
        self.role = QComboBox()
        self.role.addItems(['teacher', 'staff', 'driver', 'admin', 'maintenance'])
        self.phone = QLineEdit(); self.phone.setPlaceholderText('0600000000')
        self.email = QLineEdit(); self.email.setPlaceholderText('email@example.com')
        self.address = QTextEdit(); self.address.setMaximumHeight(60)
        self.hire_date = QDateEdit(); self.hire_date.setCalendarPopup(True)
        self.hire_date.setDate(QDate.currentDate())
        self.base_salary = QDoubleSpinBox()
        self.base_salary.setRange(0, 99999); self.base_salary.setSuffix(' MAD')

        form.addRow('Prénom *:', self.first_name)
        form.addRow('Nom *:', self.last_name)
        form.addRow('Poste:', self.role)
        form.addRow('Téléphone:', self.phone)
        form.addRow('Email:', self.email)
        form.addRow('Adresse:', self.address)
        form.addRow('Date embauche:', self.hire_date)
        form.addRow('Salaire de base:', self.base_salary)

        scroll.setWidget(content)
        layout.addWidget(scroll)

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

    def _populate(self, e):
        self.first_name.setText(e.first_name or '')
        self.last_name.setText(e.last_name or '')
        if e.role: self.role.setCurrentText(e.role)
        self.phone.setText(e.phone or '')
        self.email.setText(e.email or '')
        self.address.setText(e.address or '')
        if e.hire_date:
            self.hire_date.setDate(QDate(e.hire_date.year, e.hire_date.month, e.hire_date.day))
        self.base_salary.setValue(e.base_salary or 0)

    def _save(self):
        if not self.first_name.text().strip() or not self.last_name.text().strip():
            QMessageBox.warning(self, 'Erreur', 'Prénom et nom sont obligatoires.')
            return
        self.accept()

    def get_data(self):
        hd = self.hire_date.date()
        return {
            'first_name': self.first_name.text().strip(),
            'last_name': self.last_name.text().strip(),
            'role': self.role.currentText(),
            'phone': self.phone.text().strip(),
            'email': self.email.text().strip(),
            'address': self.address.toPlainText(),
            'hire_date': date(hd.year(), hd.month(), hd.day()),
            'base_salary': self.base_salary.value(),
        }


class SalaryDialog(QDialog):
    def __init__(self, parent, employee, session):
        super().__init__(parent)
        self.employee = employee
        self.session = session
        self.setWindowTitle(f'Salaire — {employee.first_name} {employee.last_name}')
        self.setFixedSize(460, 380)
        self.setStyleSheet(DIALOG_STYLE)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel(f'💰  Paiement Salaire — {self.employee.first_name} {self.employee.last_name}')
        title.setStyleSheet('color: #00d4ff; font-size: 14px; font-weight: bold; background: transparent;')
        layout.addWidget(title)

        from themes.style import MONTHS
        form = QFormLayout()
        form.setSpacing(10)

        self.month_combo = QComboBox(); self.month_combo.addItems(MONTHS)
        self.year_input = QLineEdit(str(datetime.now().year))
        self.base_amt = QDoubleSpinBox()
        self.base_amt.setRange(0, 99999); self.base_amt.setSuffix(' MAD')
        self.base_amt.setValue(self.employee.base_salary or 0)
        self.bonus = QDoubleSpinBox()
        self.bonus.setRange(0, 99999); self.bonus.setSuffix(' MAD')
        self.bonus.valueChanged.connect(self._update_total)
        self.base_amt.valueChanged.connect(self._update_total)
        self.total_lbl = QLabel(f'{self.employee.base_salary or 0:.2f} MAD')
        self.total_lbl.setStyleSheet('color: #00ff88; font-size: 16px; font-weight: bold; background: transparent;')
        self.notes = QLineEdit()

        form.addRow('Mois:', self.month_combo)
        form.addRow('Année:', self.year_input)
        form.addRow('Salaire de base:', self.base_amt)
        form.addRow('Prime / Bonus:', self.bonus)
        form.addRow('TOTAL:', self.total_lbl)
        form.addRow('Notes:', self.notes)
        layout.addLayout(form)
        layout.addStretch()

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton('Annuler')
        cancel_btn.setStyleSheet('background: #1e3a5f; color: #c0d0e0;')
        cancel_btn.clicked.connect(self.reject)
        pay_btn = QPushButton('✅  Valider le paiement')
        pay_btn.setStyleSheet('background: #006633; color: white; border-radius: 6px; padding: 8px 18px; font-weight: bold;')
        pay_btn.clicked.connect(self._save)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(pay_btn)
        layout.addLayout(btn_row)

    def _update_total(self):
        total = self.base_amt.value() + self.bonus.value()
        self.total_lbl.setText(f'{total:.2f} MAD')

    def _save(self):
        total = self.base_amt.value() + self.bonus.value()
        sal = Salary(
            employee_id=self.employee.id,
            month=self.month_combo.currentText(),
            year=int(self.year_input.text() or datetime.now().year),
            base_amount=self.base_amt.value(),
            bonus=self.bonus.value(),
            total=total,
            paid=True,
            paid_date=datetime.now(),
            notes=self.notes.text(),
        )
        self.session.add(sal)
        self.session.commit()
        QMessageBox.information(self, 'Succès', f'Salaire de {self.employee.first_name} enregistré: {total:.2f} MAD')
        self.accept()


class EmployeesWidget(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #1e3a5f; border-radius: 8px; background: #0a0e1a; }
            QTabBar::tab { background: #0d1228; color: #6a8aaa; border: 1px solid #1e3a5f;
                padding: 8px 20px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
            QTabBar::tab:selected { background: rgba(0,212,255,0.15); color: #00d4ff; border-bottom: 2px solid #00d4ff; }
        """)

        # --- Employees tab ---
        emp_tab = QWidget()
        emp_layout = QVBoxLayout(emp_tab)
        emp_layout.setContentsMargins(16, 16, 16, 16)
        emp_layout.setSpacing(10)

        toolbar = QHBoxLayout()
        self.search_emp = QLineEdit()
        self.search_emp.setPlaceholderText('🔍  Rechercher...')
        self.search_emp.setFixedWidth(240)
        self.search_emp.setStyleSheet('background: #0d1832; border: 1px solid #1e3a5f; border-radius: 20px; color: #e0e6f0; padding: 7px 15px;')
        self.search_emp.textChanged.connect(self._filter_employees)
        self.role_filter = QComboBox()
        self.role_filter.addItems(['Tous', 'teacher', 'staff', 'driver', 'admin', 'maintenance'])
        self.role_filter.currentTextChanged.connect(self._filter_employees)
        self.role_filter.setStyleSheet('background: #0d1832; border: 1px solid #1e3a5f; border-radius: 6px; color: #e0e6f0; padding: 6px 10px;')
        add_emp_btn = QPushButton('➕  Ajouter')
        add_emp_btn.clicked.connect(self._add_employee)
        toolbar.addWidget(self.search_emp)
        toolbar.addWidget(self.role_filter)
        toolbar.addStretch()
        toolbar.addWidget(add_emp_btn)
        emp_layout.addLayout(toolbar)

        self.emp_table = QTableWidget()
        self.emp_table.setColumnCount(7)
        self.emp_table.setHorizontalHeaderLabels(['Prénom', 'Nom', 'Poste', 'Téléphone', 'Email', 'Date embauche', 'Salaire de base'])
        self.emp_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.emp_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.emp_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.emp_table.setAlternatingRowColors(True)
        self.emp_table.verticalHeader().setVisible(False)
        self.emp_table.setStyleSheet(TABLE_STYLE)
        emp_layout.addWidget(self.emp_table)

        emp_actions = QHBoxLayout()
        edit_btn = QPushButton('✏️  Modifier')
        edit_btn.clicked.connect(self._edit_employee)
        del_btn = QPushButton('🗑️  Supprimer')
        del_btn.setStyleSheet('background: #aa1100; color: white; border-radius: 6px; padding: 8px 18px;')
        del_btn.clicked.connect(self._delete_employee)
        sal_btn = QPushButton('💰  Payer salaire')
        sal_btn.setStyleSheet('background: #006633; color: white; border-radius: 6px; padding: 8px 18px; font-weight: bold;')
        sal_btn.clicked.connect(self._pay_salary)
        emp_actions.addStretch()
        emp_actions.addWidget(edit_btn)
        emp_actions.addWidget(del_btn)
        emp_actions.addWidget(sal_btn)
        emp_layout.addLayout(emp_actions)

        # --- Salary history tab ---
        sal_tab = QWidget()
        sal_layout = QVBoxLayout(sal_tab)
        sal_layout.setContentsMargins(16, 16, 16, 16)
        sal_layout.setSpacing(10)

        sal_toolbar = QHBoxLayout()
        sal_label = QLabel('Historique des Salaires')
        sal_label.setStyleSheet('color: #00d4ff; font-size: 15px; font-weight: bold; background: transparent;')
        refresh_btn = QPushButton('🔄  Actualiser')
        refresh_btn.clicked.connect(self._load_salary_history)
        sal_toolbar.addWidget(sal_label)
        sal_toolbar.addStretch()
        sal_toolbar.addWidget(refresh_btn)
        sal_layout.addLayout(sal_toolbar)

        self.sal_table = QTableWidget()
        self.sal_table.setColumnCount(7)
        self.sal_table.setHorizontalHeaderLabels(['Employé', 'Poste', 'Mois', 'Année', 'Salaire', 'Bonus', 'Total'])
        self.sal_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sal_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sal_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sal_table.setAlternatingRowColors(True)
        self.sal_table.verticalHeader().setVisible(False)
        self.sal_table.setStyleSheet(TABLE_STYLE)
        sal_layout.addWidget(self.sal_table)

        self.sal_total_lbl = QLabel()
        self.sal_total_lbl.setStyleSheet('color: #6a8aaa; font-size: 12px; background: transparent;')
        sal_layout.addWidget(self.sal_total_lbl)

        tabs.addTab(emp_tab, '👥  Employés & Enseignants')
        tabs.addTab(sal_tab, '💰  Historique Salaires')
        layout.addWidget(tabs)
        self.tabs = tabs

    def _load_data(self):
        self.all_employees = self.session.query(Employee).filter_by(active=True).all()
        self._populate_emp_table(self.all_employees)
        self._load_salary_history()

    def _populate_emp_table(self, employees):
        self.emp_table.setRowCount(len(employees))
        for row, e in enumerate(employees):
            role_labels = {'teacher': '👨‍🏫 Enseignant', 'staff': '👔 Personnel', 'driver': '🚌 Chauffeur',
                           'admin': '⚙️ Admin', 'maintenance': '🔧 Maintenance'}
            self.emp_table.setItem(row, 0, QTableWidgetItem(e.first_name or ''))
            self.emp_table.setItem(row, 1, QTableWidgetItem(e.last_name or ''))
            self.emp_table.setItem(row, 2, QTableWidgetItem(role_labels.get(e.role, e.role or '')))
            self.emp_table.setItem(row, 3, QTableWidgetItem(e.phone or ''))
            self.emp_table.setItem(row, 4, QTableWidgetItem(e.email or ''))
            self.emp_table.setItem(row, 5, QTableWidgetItem(str(e.hire_date) if e.hire_date else ''))
            self.emp_table.setItem(row, 6, QTableWidgetItem(f'{e.base_salary:.0f} MAD'))
            self.emp_table.setRowHeight(row, 38)

    def _filter_employees(self):
        search = self.search_emp.text().lower()
        role = self.role_filter.currentText()
        filtered = [e for e in self.all_employees
                    if (search in (e.first_name or '').lower() or search in (e.last_name or '').lower())
                    and (role == 'Tous' or e.role == role)]
        self._populate_emp_table(filtered)

    def _load_salary_history(self):
        salaries = self.session.query(Salary).order_by(Salary.year.desc(), Salary.id.desc()).limit(200).all()
        self.sal_table.setRowCount(len(salaries))
        total = 0
        for row, s in enumerate(salaries):
            emp = self.session.query(Employee).filter_by(id=s.employee_id).first()
            name = f'{emp.first_name} {emp.last_name}' if emp else '-'
            role = emp.role if emp else '-'
            self.sal_table.setItem(row, 0, QTableWidgetItem(name))
            self.sal_table.setItem(row, 1, QTableWidgetItem(role))
            self.sal_table.setItem(row, 2, QTableWidgetItem(s.month or ''))
            self.sal_table.setItem(row, 3, QTableWidgetItem(str(s.year or '')))
            self.sal_table.setItem(row, 4, QTableWidgetItem(f'{s.base_amount:.0f} MAD'))
            self.sal_table.setItem(row, 5, QTableWidgetItem(f'{s.bonus:.0f} MAD'))
            self.sal_table.setItem(row, 6, QTableWidgetItem(f'{s.total:.0f} MAD'))
            self.sal_table.setRowHeight(row, 38)
            total += s.total or 0
        self.sal_total_lbl.setText(f'Total versé: {total:.2f} MAD  |  {len(salaries)} entrées')

    def _get_selected_employee(self):
        row = self.emp_table.currentRow()
        if row < 0:
            QMessageBox.information(self, 'Info', 'Veuillez sélectionner un employé.')
            return None
        return self.all_employees[row] if row < len(self.all_employees) else None

    def _add_employee(self):
        dlg = EmployeeDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            emp = Employee(**data)
            self.session.add(emp)
            self.session.commit()
            self._load_data()

    def _edit_employee(self):
        e = self._get_selected_employee()
        if not e: return
        dlg = EmployeeDialog(self, e)
        if dlg.exec():
            data = dlg.get_data()
            for k, v in data.items():
                setattr(e, k, v)
            self.session.commit()
            self._load_data()

    def _delete_employee(self):
        e = self._get_selected_employee()
        if not e: return
        reply = QMessageBox.question(self, 'Confirmation', f'Supprimer {e.first_name} {e.last_name}?',
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            e.active = False
            self.session.commit()
            self._load_data()

    def _pay_salary(self):
        e = self._get_selected_employee()
        if not e: return
        dlg = SalaryDialog(self, e, self.session)
        dlg.exec()
        self._load_salary_history()
