import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QMessageBox, QSpinBox, QHeaderView, QAbstractItemView, QTabWidget)
from PySide6.QtCore import Qt
from models.database import Bus, Employee, Student

TABLE_STYLE = """
    QTableWidget { background: #0d1228; border: 1px solid #1e3a5f; border-radius: 8px; gridline-color: #1a2744; }
    QTableWidget::item { padding: 8px 12px; color: #c0d0e0; border-bottom: 1px solid #1a2744; }
    QTableWidget::item:selected { background: rgba(0,212,255,0.2); color: white; }
    QTableWidget::item:alternate { background: #0a1020; }
    QHeaderView::section { background: #162040; color: #00d4ff; padding: 10px 12px;
        border: none; border-right: 1px solid #1e3a5f; border-bottom: 2px solid #00d4ff;
        font-weight: bold; font-size: 11px; }
"""


class BusDialog(QDialog):
    def __init__(self, parent=None, bus=None, session=None):
        super().__init__(parent)
        self.bus = bus
        self.session = session
        self.setWindowTitle('Modifier bus' if bus else 'Nouveau bus')
        self.setFixedSize(460, 360)
        self.setStyleSheet("""
            QDialog { background: #0a0e1a; }
            QLabel { color: #c0d0e0; font-size: 12px; background: transparent; }
            QLineEdit, QComboBox, QTextEdit, QSpinBox {
                background: #0d1832; border: 1px solid #1e3a5f; border-radius: 6px;
                color: #e0e6f0; padding: 6px 10px; font-size: 13px; }
            QComboBox QAbstractItemView { background: #0d1832; color: #e0e6f0; }
        """)
        self._setup_ui()
        if bus: self._populate(bus)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)
        title = QLabel('🚌  Fiche Bus / Véhicule')
        title.setStyleSheet('color: #00d4ff; font-size: 15px; font-weight: bold; background: transparent;')
        layout.addWidget(title)

        form = QFormLayout(); form.setSpacing(10)
        self.name = QLineEdit(); self.name.setPlaceholderText('Nom / Numéro du bus')
        self.plate = QLineEdit(); self.plate.setPlaceholderText('Plaque d\'immatriculation')
        self.capacity = QSpinBox(); self.capacity.setRange(1, 100); self.capacity.setValue(30)
        self.driver_combo = QComboBox()
        self.driver_combo.addItem('-- Aucun --', None)
        if self.session:
            drivers = self.session.query(Employee).filter_by(role='driver', active=True).all()
            for d in drivers:
                self.driver_combo.addItem(f'{d.first_name} {d.last_name}', d.id)
        self.route = QTextEdit(); self.route.setMaximumHeight(60)
        self.route.setPlaceholderText('Description de la route / arrêts')

        form.addRow('Nom du bus:', self.name)
        form.addRow('Immatriculation:', self.plate)
        form.addRow('Capacité:', self.capacity)
        form.addRow('Chauffeur:', self.driver_combo)
        form.addRow('Route:', self.route)
        layout.addLayout(form)
        layout.addStretch()

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton('Annuler')
        cancel_btn.setStyleSheet('background: #1e3a5f; color: #c0d0e0;')
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton('💾  Enregistrer')
        save_btn.clicked.connect(self.accept)
        btn_row.addStretch(); btn_row.addWidget(cancel_btn); btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _populate(self, b):
        self.name.setText(b.name or '')
        self.plate.setText(b.plate or '')
        self.capacity.setValue(b.capacity or 30)
        self.route.setText(b.route or '')
        if b.driver_id:
            idx = self.driver_combo.findData(b.driver_id)
            if idx >= 0: self.driver_combo.setCurrentIndex(idx)

    def get_data(self):
        return {
            'name': self.name.text().strip(),
            'plate': self.plate.text().strip(),
            'capacity': self.capacity.value(),
            'driver_id': self.driver_combo.currentData(),
            'route': self.route.toPlainText(),
        }


class TransportWidget(QWidget):
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

        # --- Buses tab ---
        bus_tab = QWidget()
        bl = QVBoxLayout(bus_tab); bl.setContentsMargins(16,16,16,16); bl.setSpacing(10)
        bus_toolbar = QHBoxLayout()
        bus_lbl = QLabel('Gestion des Bus')
        bus_lbl.setStyleSheet('color: #00d4ff; font-size: 14px; font-weight: bold; background: transparent;')
        add_bus_btn = QPushButton('➕  Ajouter bus')
        add_bus_btn.clicked.connect(self._add_bus)
        bus_toolbar.addWidget(bus_lbl); bus_toolbar.addStretch(); bus_toolbar.addWidget(add_bus_btn)
        bl.addLayout(bus_toolbar)

        self.bus_table = QTableWidget()
        self.bus_table.setColumnCount(5)
        self.bus_table.setHorizontalHeaderLabels(['Nom', 'Plaque', 'Capacité', 'Chauffeur', 'Route'])
        self.bus_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bus_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.bus_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.bus_table.setAlternatingRowColors(True)
        self.bus_table.verticalHeader().setVisible(False)
        self.bus_table.setStyleSheet(TABLE_STYLE)
        bl.addWidget(self.bus_table)

        bus_actions = QHBoxLayout()
        edit_bus = QPushButton('✏️  Modifier'); edit_bus.clicked.connect(self._edit_bus)
        del_bus = QPushButton('🗑️  Supprimer')
        del_bus.setStyleSheet('background: #aa1100; color: white; border-radius: 6px; padding: 8px 18px;')
        del_bus.clicked.connect(self._delete_bus)
        bus_actions.addStretch(); bus_actions.addWidget(edit_bus); bus_actions.addWidget(del_bus)
        bl.addLayout(bus_actions)

        # --- Subscribers tab ---
        sub_tab = QWidget()
        sl = QVBoxLayout(sub_tab); sl.setContentsMargins(16,16,16,16); sl.setSpacing(10)
        sub_lbl = QLabel('Élèves inscrits au transport')
        sub_lbl.setStyleSheet('color: #00d4ff; font-size: 14px; font-weight: bold; background: transparent;')
        sl.addWidget(sub_lbl)

        self.sub_table = QTableWidget()
        self.sub_table.setColumnCount(5)
        self.sub_table.setHorizontalHeaderLabels(['Code', 'Élève', 'Classe', 'Parent', 'Téléphone'])
        self.sub_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sub_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sub_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sub_table.setAlternatingRowColors(True)
        self.sub_table.verticalHeader().setVisible(False)
        self.sub_table.setStyleSheet(TABLE_STYLE)
        sl.addWidget(self.sub_table)
        self.sub_count_lbl = QLabel()
        self.sub_count_lbl.setStyleSheet('color: #6a8aaa; font-size: 12px; background: transparent;')
        sl.addWidget(self.sub_count_lbl)

        tabs.addTab(bus_tab, '🚌  Gestion Bus')
        tabs.addTab(sub_tab, '👥  Abonnés Transport')
        layout.addWidget(tabs)

    def _load_data(self):
        self._load_buses()
        self._load_subscribers()

    def _load_buses(self):
        buses = self.session.query(Bus).filter_by(active=True).all()
        self.all_buses = buses
        self.bus_table.setRowCount(len(buses))
        for row, b in enumerate(buses):
            driver = self.session.query(Employee).filter_by(id=b.driver_id).first() if b.driver_id else None
            driver_name = f'{driver.first_name} {driver.last_name}' if driver else '-'
            self.bus_table.setItem(row, 0, QTableWidgetItem(b.name or ''))
            self.bus_table.setItem(row, 1, QTableWidgetItem(b.plate or ''))
            self.bus_table.setItem(row, 2, QTableWidgetItem(str(b.capacity or 0)))
            self.bus_table.setItem(row, 3, QTableWidgetItem(driver_name))
            self.bus_table.setItem(row, 4, QTableWidgetItem(b.route or ''))
            self.bus_table.setRowHeight(row, 36)

    def _load_subscribers(self):
        students = self.session.query(Student).filter_by(active=True, transport=True).all()
        self.sub_table.setRowCount(len(students))
        for row, s in enumerate(students):
            self.sub_table.setItem(row, 0, QTableWidgetItem(s.code or ''))
            self.sub_table.setItem(row, 1, QTableWidgetItem(f'{s.first_name} {s.last_name}'))
            self.sub_table.setItem(row, 2, QTableWidgetItem(s.class_name or ''))
            self.sub_table.setItem(row, 3, QTableWidgetItem(s.parent_name or ''))
            self.sub_table.setItem(row, 4, QTableWidgetItem(s.parent_phone or ''))
            self.sub_table.setRowHeight(row, 36)
        self.sub_count_lbl.setText(f'Total abonnés: {len(students)} élèves')

    def _add_bus(self):
        dlg = BusDialog(self, session=self.session)
        if dlg.exec():
            bus = Bus(**dlg.get_data())
            self.session.add(bus); self.session.commit(); self._load_buses()

    def _edit_bus(self):
        row = self.bus_table.currentRow()
        if row < 0: QMessageBox.information(self,'Info','Sélectionnez un bus.'); return
        b = self.all_buses[row]
        dlg = BusDialog(self, b, self.session)
        if dlg.exec():
            data = dlg.get_data()
            for k,v in data.items(): setattr(b,k,v)
            self.session.commit(); self._load_buses()

    def _delete_bus(self):
        row = self.bus_table.currentRow()
        if row < 0: return
        b = self.all_buses[row]
        reply = QMessageBox.question(self,'Confirmation',f'Supprimer le bus {b.name}?', QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            b.active = False; self.session.commit(); self._load_buses()
