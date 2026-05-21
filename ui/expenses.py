import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QTextEdit, QMessageBox, QDoubleSpinBox, QHeaderView, QAbstractItemView, QFrame)
from PySide6.QtCore import Qt, QDate
from datetime import datetime, date
from models.database import Expense
from themes.style import EXPENSE_CATEGORIES

TABLE_STYLE = """
    QTableWidget { background: #0d1228; border: 1px solid #1e3a5f; border-radius: 8px; gridline-color: #1a2744; }
    QTableWidget::item { padding: 8px 12px; color: #c0d0e0; border-bottom: 1px solid #1a2744; }
    QTableWidget::item:selected { background: rgba(0,212,255,0.2); color: white; }
    QTableWidget::item:alternate { background: #0a1020; }
    QHeaderView::section { background: #162040; color: #00d4ff; padding: 10px 12px;
        border: none; border-right: 1px solid #1e3a5f; border-bottom: 2px solid #00d4ff;
        font-weight: bold; font-size: 11px; }
"""


class ExpenseDialog(QDialog):
    def __init__(self, parent=None, expense=None):
        super().__init__(parent)
        self.expense = expense
        self.setWindowTitle('Modifier dépense' if expense else 'Nouvelle dépense')
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog { background: #0a0e1a; }
            QLabel { color: #c0d0e0; font-size: 12px; background: transparent; }
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QDoubleSpinBox {
                background: #0d1832; border: 1px solid #1e3a5f; border-radius: 6px;
                color: #e0e6f0; padding: 6px 10px; font-size: 13px; }
            QLineEdit:focus, QComboBox:focus { border-color: #00d4ff; }
            QComboBox QAbstractItemView { background: #0d1832; color: #e0e6f0; }
        """)
        self._setup_ui()
        if expense:
            self._populate(expense)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)
        title = QLabel('💸  Enregistrer une Dépense')
        title.setStyleSheet('color: #00d4ff; font-size: 15px; font-weight: bold; background: transparent;')
        layout.addWidget(title)

        form = QFormLayout(); form.setSpacing(10)
        self.category = QComboBox(); self.category.addItems(EXPENSE_CATEGORIES); self.category.setEditable(True)
        self.exp_type = QComboBox(); self.exp_type.addItems(['fixed', 'variable'])
        self.description = QLineEdit(); self.description.setPlaceholderText('Description de la dépense')
        self.amount = QDoubleSpinBox(); self.amount.setRange(0, 999999); self.amount.setSuffix(' MAD')
        self.exp_date = QDateEdit(); self.exp_date.setCalendarPopup(True); self.exp_date.setDate(QDate.currentDate())
        self.paid_by = QLineEdit(); self.paid_by.setPlaceholderText('Payé par')
        self.notes = QTextEdit(); self.notes.setMaximumHeight(60)

        form.addRow('Catégorie:', self.category)
        form.addRow('Type:', self.exp_type)
        form.addRow('Description:', self.description)
        form.addRow('Montant:', self.amount)
        form.addRow('Date:', self.exp_date)
        form.addRow('Payé par:', self.paid_by)
        form.addRow('Notes:', self.notes)
        layout.addLayout(form)
        layout.addStretch()

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton('Annuler')
        cancel_btn.setStyleSheet('background: #1e3a5f; color: #c0d0e0;')
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton('💾  Enregistrer')
        save_btn.clicked.connect(lambda: self.accept())
        btn_row.addStretch(); btn_row.addWidget(cancel_btn); btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _populate(self, e):
        if e.category: self.category.setCurrentText(e.category)
        if e.expense_type: self.exp_type.setCurrentText(e.expense_type)
        self.description.setText(e.description or '')
        self.amount.setValue(e.amount or 0)
        if e.date: self.exp_date.setDate(QDate(e.date.year, e.date.month, e.date.day))
        self.paid_by.setText(e.paid_by or '')
        self.notes.setText(e.notes or '')

    def get_data(self):
        d = self.exp_date.date()
        return {
            'category': self.category.currentText(),
            'expense_type': self.exp_type.currentText(),
            'description': self.description.text().strip(),
            'amount': self.amount.value(),
            'date': date(d.year(), d.month(), d.day()),
            'paid_by': self.paid_by.text().strip(),
            'notes': self.notes.toPlainText(),
        }


class ExpensesWidget(QWidget):
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
        title = QLabel('💸  Gestion des Dépenses')
        title.setStyleSheet('color: #00d4ff; font-size: 16px; font-weight: bold; background: transparent;')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('🔍  Rechercher...')
        self.search_input.setFixedWidth(220)
        self.search_input.setStyleSheet('background: #0d1832; border: 1px solid #1e3a5f; border-radius: 20px; color: #e0e6f0; padding: 7px 15px;')
        self.search_input.textChanged.connect(self._filter)
        self.cat_filter = QComboBox()
        self.cat_filter.addItem('Toutes catégories')
        self.cat_filter.addItems(EXPENSE_CATEGORIES)
        self.cat_filter.setStyleSheet('background: #0d1832; border: 1px solid #1e3a5f; border-radius: 6px; color: #e0e6f0; padding: 6px 10px;')
        self.cat_filter.currentTextChanged.connect(self._filter)
        add_btn = QPushButton('➕  Ajouter dépense')
        add_btn.clicked.connect(self._add_expense)
        toolbar.addWidget(title); toolbar.addStretch()
        toolbar.addWidget(self.search_input); toolbar.addWidget(self.cat_filter); toolbar.addWidget(add_btn)
        layout.addLayout(toolbar)

        # Summary cards
        self.summary_row = QHBoxLayout()
        self.total_card = self._make_mini_card('Total dépenses', '0 MAD', '#ff6644')
        self.fixed_card = self._make_mini_card('Dépenses fixes', '0 MAD', '#ffaa00')
        self.var_card = self._make_mini_card('Dépenses variables', '0 MAD', '#8866ff')
        self.month_card = self._make_mini_card('Ce mois-ci', '0 MAD', '#00d4ff')
        self.summary_row.addWidget(self.total_card)
        self.summary_row.addWidget(self.fixed_card)
        self.summary_row.addWidget(self.var_card)
        self.summary_row.addWidget(self.month_card)
        layout.addLayout(self.summary_row)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['Catégorie', 'Type', 'Description', 'Montant', 'Date', 'Payé par', 'Notes'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.table)

        action_row = QHBoxLayout()
        edit_btn = QPushButton('✏️  Modifier')
        edit_btn.clicked.connect(self._edit_expense)
        del_btn = QPushButton('🗑️  Supprimer')
        del_btn.setStyleSheet('background: #aa1100; color: white; border-radius: 6px; padding: 8px 18px;')
        del_btn.clicked.connect(self._delete_expense)
        action_row.addStretch(); action_row.addWidget(edit_btn); action_row.addWidget(del_btn)
        layout.addLayout(action_row)

        self.all_expenses = []

    def _make_mini_card(self, label, value, color):
        card = QFrame()
        card.setStyleSheet(f'QFrame {{ background: #0d1832; border: 1px solid #1e3a5f; border-radius: 10px; border-left: 3px solid {color}; }}')
        card.setFixedHeight(72)
        cl = QVBoxLayout(card); cl.setContentsMargins(14, 10, 14, 10)
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f'color: {color}; font-size: 18px; font-weight: bold; background: transparent;')
        lbl = QLabel(label)
        lbl.setStyleSheet('color: #6a8aaa; font-size: 11px; background: transparent;')
        cl.addWidget(val_lbl); cl.addWidget(lbl)
        card._val = val_lbl
        return card

    def _load_data(self):
        self.all_expenses = self.session.query(Expense).order_by(Expense.date.desc()).all()
        self._populate_table(self.all_expenses)
        self._update_summary(self.all_expenses)

    def _populate_table(self, expenses):
        self.table.setRowCount(len(expenses))
        for row, e in enumerate(expenses):
            type_labels = {'fixed': '🔒 Fixe', 'variable': '📊 Variable'}
            self.table.setItem(row, 0, QTableWidgetItem(e.category or ''))
            self.table.setItem(row, 1, QTableWidgetItem(type_labels.get(e.expense_type, e.expense_type or '')))
            self.table.setItem(row, 2, QTableWidgetItem(e.description or ''))
            self.table.setItem(row, 3, QTableWidgetItem(f'{e.amount:.2f} MAD'))
            self.table.setItem(row, 4, QTableWidgetItem(str(e.date) if e.date else ''))
            self.table.setItem(row, 5, QTableWidgetItem(e.paid_by or ''))
            self.table.setItem(row, 6, QTableWidgetItem(e.notes or ''))
            self.table.setRowHeight(row, 36)

    def _update_summary(self, expenses):
        year = datetime.now().year; month = datetime.now().month
        total = sum(e.amount for e in expenses)
        fixed = sum(e.amount for e in expenses if e.expense_type == 'fixed')
        var = sum(e.amount for e in expenses if e.expense_type == 'variable')
        this_month = sum(e.amount for e in expenses if e.date and e.date.month == month and e.date.year == year)
        self.total_card._val.setText(f'{total:.0f} MAD')
        self.fixed_card._val.setText(f'{fixed:.0f} MAD')
        self.var_card._val.setText(f'{var:.0f} MAD')
        self.month_card._val.setText(f'{this_month:.0f} MAD')

    def _filter(self):
        search = self.search_input.text().lower()
        cat = self.cat_filter.currentText()
        filtered = [e for e in self.all_expenses
                    if (search in (e.description or '').lower() or search in (e.category or '').lower())
                    and (cat == 'Toutes catégories' or e.category == cat)]
        self._populate_table(filtered)
        self._update_summary(filtered)

    def _get_selected(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, 'Info', 'Veuillez sélectionner une dépense.')
            return None
        return self.all_expenses[row] if row < len(self.all_expenses) else None

    def _add_expense(self):
        dlg = ExpenseDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            exp = Expense(**data)
            self.session.add(exp); self.session.commit()
            self._load_data()

    def _edit_expense(self):
        e = self._get_selected()
        if not e: return
        dlg = ExpenseDialog(self, e)
        if dlg.exec():
            data = dlg.get_data()
            for k, v in data.items(): setattr(e, k, v)
            self.session.commit(); self._load_data()

    def _delete_expense(self):
        e = self._get_selected()
        if not e: return
        reply = QMessageBox.question(self, 'Confirmation', f'Supprimer cette dépense ({e.amount:.2f} MAD)?',
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.session.delete(e); self.session.commit(); self._load_data()
