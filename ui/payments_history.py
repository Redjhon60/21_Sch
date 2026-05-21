import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit, QHeaderView, QAbstractItemView,
    QFrame, QMessageBox)
from PySide6.QtCore import Qt
from datetime import datetime
from models.database import Payment, Receipt, Student
from themes.style import MONTHS

TABLE_STYLE = """
    QTableWidget { background: #0d1228; border: 1px solid #1e3a5f; border-radius: 8px; gridline-color: #1a2744; }
    QTableWidget::item { padding: 8px 12px; color: #c0d0e0; border-bottom: 1px solid #1a2744; }
    QTableWidget::item:selected { background: rgba(0,212,255,0.2); color: white; }
    QTableWidget::item:alternate { background: #0a1020; }
    QHeaderView::section { background: #162040; color: #00d4ff; padding: 10px 12px;
        border: none; border-right: 1px solid #1e3a5f; border-bottom: 2px solid #00d4ff;
        font-weight: bold; font-size: 11px; }
"""


class PaymentsHistoryWidget(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        toolbar = QHBoxLayout()
        title = QLabel('💳  Historique des Paiements')
        title.setStyleSheet('color: #00d4ff; font-size: 16px; font-weight: bold; background: transparent;')

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('🔍  Rechercher élève/reçu...')
        self.search_input.setFixedWidth(240)
        self.search_input.setStyleSheet('background: #0d1832; border: 1px solid #1e3a5f; border-radius: 20px; color: #e0e6f0; padding: 7px 15px;')
        self.search_input.textChanged.connect(self._filter)

        self.type_filter = QComboBox()
        self.type_filter.addItems(['Tous types', 'monthly', 'insurance', 'transport'])
        self.type_filter.setStyleSheet('background: #0d1832; border: 1px solid #1e3a5f; border-radius: 6px; color: #e0e6f0; padding: 6px 10px;')
        self.type_filter.currentTextChanged.connect(self._filter)

        self.month_filter = QComboBox()
        self.month_filter.addItem('Tous les mois')
        self.month_filter.addItems(MONTHS)
        self.month_filter.setStyleSheet('background: #0d1832; border: 1px solid #1e3a5f; border-radius: 6px; color: #e0e6f0; padding: 6px 10px;')
        self.month_filter.currentTextChanged.connect(self._filter)

        toolbar.addWidget(title); toolbar.addStretch()
        toolbar.addWidget(self.search_input); toolbar.addWidget(self.type_filter); toolbar.addWidget(self.month_filter)
        layout.addLayout(toolbar)

        # Summary strip
        summary_row = QHBoxLayout()
        self.total_lbl = QLabel()
        self.total_lbl.setStyleSheet('color: #6a8aaa; font-size: 12px; background: transparent;')
        summary_row.addWidget(self.total_lbl)
        summary_row.addStretch()
        open_receipt_btn = QPushButton('🧾  Ouvrir Reçu PDF')
        open_receipt_btn.clicked.connect(self._open_receipt)
        summary_row.addWidget(open_receipt_btn)
        layout.addLayout(summary_row)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(['N° Reçu','Élève','Classe','Type','Mois','Montant','Date','Statut'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.table)

        self.all_payments = []

    def _load_data(self):
        payments = self.session.query(Payment).order_by(Payment.payment_date.desc()).limit(500).all()
        self.all_payments = payments
        self._populate_table(payments)

    def _populate_table(self, payments):
        self.table.setRowCount(len(payments))
        total = 0
        type_labels = {'monthly': '📅 Mensualité', 'insurance': '🛡️ Assurance', 'transport': '🚌 Transport'}
        for row, p in enumerate(payments):
            student = self.session.query(Student).filter_by(id=p.student_id).first()
            name = f'{student.first_name} {student.last_name}' if student else '-'
            cls = student.class_name if student else '-'
            self.table.setItem(row, 0, QTableWidgetItem(p.receipt_number or '-'))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(cls))
            self.table.setItem(row, 3, QTableWidgetItem(type_labels.get(p.payment_type, p.payment_type or '')))
            self.table.setItem(row, 4, QTableWidgetItem(f'{p.month or ""} {p.year or ""}'))
            self.table.setItem(row, 5, QTableWidgetItem(f'{p.amount:.2f} MAD'))
            self.table.setItem(row, 6, QTableWidgetItem(p.payment_date.strftime('%d/%m/%Y %H:%M') if p.payment_date else ''))
            self.table.setItem(row, 7, QTableWidgetItem('✅ Payé'))
            self.table.setRowHeight(row, 36)
            total += p.amount or 0
        count = len(payments)
        self.total_lbl.setText(f'{count} paiements  |  Total: {total:.2f} MAD')

    def _filter(self):
        search = self.search_input.text().lower()
        pay_type = self.type_filter.currentText()
        month = self.month_filter.currentText()
        filtered = []
        for p in self.all_payments:
            student = self.session.query(Student).filter_by(id=p.student_id).first()
            name = f'{(student.first_name or "")} {(student.last_name or "")}'.lower() if student else ''
            rec = (p.receipt_number or '').lower()
            if search and search not in name and search not in rec:
                continue
            if pay_type != 'Tous types' and p.payment_type != pay_type:
                continue
            if month != 'Tous les mois' and p.month != month:
                continue
            filtered.append(p)
        self._populate_table(filtered)

    def _open_receipt(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, 'Info', 'Sélectionnez un paiement.')
            return
        rec_num = self.table.item(row, 0).text()
        receipt = self.session.query(Receipt).filter_by(receipt_number=rec_num).first()
        if receipt and receipt.pdf_path and os.path.exists(receipt.pdf_path):
            import subprocess, platform
            if platform.system() == 'Linux':
                subprocess.Popen(['xdg-open', receipt.pdf_path])
            elif platform.system() == 'Darwin':
                subprocess.Popen(['open', receipt.pdf_path])
            else:
                os.startfile(receipt.pdf_path)
        else:
            QMessageBox.warning(self, 'Introuvable', 'Le fichier PDF du reçu est introuvable.')
