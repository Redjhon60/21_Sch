import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout, QLineEdit, QComboBox,
    QMessageBox, QHeaderView, QAbstractItemView, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from models.database import Schedule, Employee
from themes.style import CLASSES

TABLE_STYLE = """
    QTableWidget { background: #0d1228; border: 1px solid #1e3a5f; border-radius: 8px; gridline-color: #1a2744; }
    QTableWidget::item { padding: 6px 8px; color: #c0d0e0; border: 1px solid #1a2744; }
    QTableWidget::item:selected { background: rgba(0,212,255,0.25); color: white; }
    QHeaderView::section { background: #162040; color: #00d4ff; padding: 8px 10px;
        border: none; border-right: 1px solid #1e3a5f; border-bottom: 2px solid #00d4ff;
        font-weight: bold; font-size: 11px; }
"""
DAYS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
TIME_SLOTS = ['08:00-09:00','09:00-10:00','10:00-11:00','11:00-12:00',
              '14:00-15:00','15:00-16:00','16:00-17:00','17:00-18:00']


class ScheduleDialog(QDialog):
    def __init__(self, parent=None, schedule=None, session=None):
        super().__init__(parent)
        self.session = session
        self.schedule = schedule
        self.setWindowTitle('Modifier' if schedule else 'Ajouter un cours')
        self.setFixedSize(460, 360)
        self.setStyleSheet("""
            QDialog { background: #0a0e1a; }
            QLabel { color: #c0d0e0; font-size: 12px; background: transparent; }
            QLineEdit, QComboBox {
                background: #0d1832; border: 1px solid #1e3a5f; border-radius: 6px;
                color: #e0e6f0; padding: 6px 10px; font-size: 13px; }
            QComboBox QAbstractItemView { background: #0d1832; color: #e0e6f0; }
        """)
        self._setup_ui()
        if schedule: self._populate(schedule)

    def _setup_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(24,20,24,20); layout.setSpacing(14)
        title = QLabel('📅  Ajouter / Modifier un Cours')
        title.setStyleSheet('color: #00d4ff; font-size: 15px; font-weight: bold; background: transparent;')
        layout.addWidget(title)

        form = QFormLayout(); form.setSpacing(10)
        self.class_combo = QComboBox(); self.class_combo.addItems(CLASSES)
        self.day_combo = QComboBox(); self.day_combo.addItems(DAYS)
        self.time_start = QComboBox()
        self.time_start.addItems([t.split('-')[0] for t in TIME_SLOTS])
        self.time_end = QComboBox()
        self.time_end.addItems([t.split('-')[1] for t in TIME_SLOTS])
        self.time_end.setCurrentIndex(1)
        self.subject = QLineEdit(); self.subject.setPlaceholderText('Mathématiques, Français...')
        self.teacher_combo = QComboBox()
        self.teacher_combo.addItem('-- Aucun --', None)
        if self.session:
            teachers = self.session.query(Employee).filter_by(role='teacher', active=True).all()
            for t in teachers:
                self.teacher_combo.addItem(f'{t.first_name} {t.last_name}', t.id)
        self.room = QLineEdit(); self.room.setPlaceholderText('Salle 1, Labo...')

        form.addRow('Classe:', self.class_combo)
        form.addRow('Jour:', self.day_combo)
        form.addRow('Heure début:', self.time_start)
        form.addRow('Heure fin:', self.time_end)
        form.addRow('Matière:', self.subject)
        form.addRow('Enseignant:', self.teacher_combo)
        form.addRow('Salle:', self.room)
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

    def _populate(self, s):
        self.class_combo.setCurrentText(s.class_name or '')
        self.day_combo.setCurrentText(s.day or '')
        if s.time_start: self.time_start.setCurrentText(s.time_start)
        if s.time_end: self.time_end.setCurrentText(s.time_end)
        self.subject.setText(s.subject or '')
        if s.teacher_id:
            idx = self.teacher_combo.findData(s.teacher_id)
            if idx >= 0: self.teacher_combo.setCurrentIndex(idx)
        self.room.setText(s.room or '')

    def get_data(self):
        return {
            'class_name': self.class_combo.currentText(),
            'day': self.day_combo.currentText(),
            'time_start': self.time_start.currentText(),
            'time_end': self.time_end.currentText(),
            'subject': self.subject.text().strip(),
            'teacher_id': self.teacher_combo.currentData(),
            'room': self.room.text().strip(),
        }


class TimetableWidget(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(20,20,20,20); layout.setSpacing(12)

        toolbar = QHBoxLayout()
        title = QLabel('📅  Emploi du Temps')
        title.setStyleSheet('color: #00d4ff; font-size: 16px; font-weight: bold; background: transparent;')
        self.class_filter = QComboBox(); self.class_filter.addItems(CLASSES)
        self.class_filter.setStyleSheet('background: #0d1832; border: 1px solid #1e3a5f; border-radius: 6px; color: #e0e6f0; padding: 6px 10px; min-width: 100px;')
        self.class_filter.currentTextChanged.connect(self._load_timetable)
        add_btn = QPushButton('➕  Ajouter cours')
        add_btn.clicked.connect(self._add_schedule)
        toolbar.addWidget(title); toolbar.addStretch()
        toolbar.addWidget(QLabel('Classe:')); toolbar.addWidget(self.class_filter)
        toolbar.addWidget(add_btn)
        layout.addLayout(toolbar)

        # Grid timetable
        self.grid = QTableWidget()
        self.grid.setRowCount(len(TIME_SLOTS))
        self.grid.setColumnCount(len(DAYS))
        self.grid.setHorizontalHeaderLabels(DAYS)
        self.grid.setVerticalHeaderLabels(TIME_SLOTS)
        self.grid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.grid.verticalHeader().setDefaultSectionSize(55)
        self.grid.verticalHeader().setStyleSheet('QHeaderView::section { background: #0d1832; color: #8a9bb0; padding: 4px; font-size: 10px; border: none; border-right: 1px solid #1e3a5f; }')
        self.grid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.grid.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.grid.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.grid)

        # List view
        list_toolbar = QHBoxLayout()
        list_lbl = QLabel('Liste des cours')
        list_lbl.setStyleSheet('color: #00d4ff; font-size: 14px; font-weight: bold; background: transparent;')
        del_btn = QPushButton('🗑️  Supprimer cours sélectionné')
        del_btn.setStyleSheet('background: #aa1100; color: white; border-radius: 6px; padding: 7px 16px;')
        del_btn.clicked.connect(self._delete_schedule)
        list_toolbar.addWidget(list_lbl); list_toolbar.addStretch(); list_toolbar.addWidget(del_btn)
        layout.addLayout(list_toolbar)

        self.list_table = QTableWidget()
        self.list_table.setColumnCount(6)
        self.list_table.setHorizontalHeaderLabels(['Jour', 'Horaire', 'Matière', 'Enseignant', 'Salle', 'Classe'])
        self.list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.list_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.list_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.list_table.setAlternatingRowColors(True)
        self.list_table.verticalHeader().setVisible(False)
        self.list_table.setMaximumHeight(180)
        self.list_table.setStyleSheet(TABLE_STYLE)
        layout.addWidget(self.list_table)

        self.all_schedules = []

    def _load_data(self):
        self._load_timetable(self.class_filter.currentText())

    def _load_timetable(self, class_name=None):
        class_name = class_name or self.class_filter.currentText()
        schedules = self.session.query(Schedule).filter_by(class_name=class_name).all()
        self.all_schedules = schedules

        # Clear grid
        for r in range(len(TIME_SLOTS)):
            for c in range(len(DAYS)):
                self.grid.setItem(r, c, QTableWidgetItem(''))

        subject_colors = ['#003366','#330033','#003300','#333300','#330000','#001a33','#1a0033','#001a00']
        color_map = {}
        color_idx = 0

        for s in schedules:
            if s.day in DAYS and s.time_start:
                col = DAYS.index(s.day)
                time_key = s.time_start
                for ridx, ts in enumerate(TIME_SLOTS):
                    if ts.startswith(time_key):
                        teacher = self.session.query(Employee).filter_by(id=s.teacher_id).first() if s.teacher_id else None
                        teacher_name = f'{teacher.first_name} {teacher.last_name}' if teacher else ''
                        text = f'{s.subject or ""}\n{teacher_name}\n{s.room or ""}'
                        item = QTableWidgetItem(text)
                        item.setTextAlignment(Qt.AlignCenter)
                        subj = s.subject or ''
                        if subj not in color_map:
                            color_map[subj] = subject_colors[color_idx % len(subject_colors)]
                            color_idx += 1
                        item.setBackground(QColor(color_map[subj]))
                        item.setForeground(QColor('#00d4ff'))
                        self.grid.setItem(ridx, col, item)
                        break

        # List
        self.list_table.setRowCount(len(schedules))
        for row, s in enumerate(schedules):
            teacher = self.session.query(Employee).filter_by(id=s.teacher_id).first() if s.teacher_id else None
            teacher_name = f'{teacher.first_name} {teacher.last_name}' if teacher else '-'
            self.list_table.setItem(row, 0, QTableWidgetItem(s.day or ''))
            self.list_table.setItem(row, 1, QTableWidgetItem(f'{s.time_start}-{s.time_end}'))
            self.list_table.setItem(row, 2, QTableWidgetItem(s.subject or ''))
            self.list_table.setItem(row, 3, QTableWidgetItem(teacher_name))
            self.list_table.setItem(row, 4, QTableWidgetItem(s.room or ''))
            self.list_table.setItem(row, 5, QTableWidgetItem(s.class_name or ''))
            self.list_table.setRowHeight(row, 34)

    def _add_schedule(self):
        dlg = ScheduleDialog(self, session=self.session)
        if dlg.exec():
            sch = Schedule(**dlg.get_data())
            self.session.add(sch); self.session.commit()
            self._load_timetable()

    def _delete_schedule(self):
        row = self.list_table.currentRow()
        if row < 0: QMessageBox.information(self,'Info','Sélectionnez un cours.'); return
        s = self.all_schedules[row]
        reply = QMessageBox.question(self,'Confirmation',f'Supprimer le cours {s.subject}?',
            QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.session.delete(s); self.session.commit(); self._load_timetable()
