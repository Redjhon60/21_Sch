import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from datetime import datetime

try:
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib.pyplot as plt
    HAS_MPL = True
except:
    HAS_MPL = False


def make_stat_card(icon, label, value, color='#00d4ff', bg='#0d1832'):
    card = QFrame()
    card.setObjectName('stat_card')
    card.setMinimumHeight(110)
    card.setStyleSheet(f"""
        QFrame#stat_card {{
            background: {bg};
            border: 1px solid #1e3a5f;
            border-radius: 12px;
        }}
        QFrame#stat_card:hover {{
            border: 1px solid {color};
        }}
    """)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(16, 14, 16, 14)

    top = QHBoxLayout()
    icon_lbl = QLabel(icon)
    icon_lbl.setStyleSheet(f'font-size: 26px; background: transparent;')
    top.addWidget(icon_lbl)
    top.addStretch()

    val_lbl = QLabel(str(value))
    val_lbl.setStyleSheet(f'font-size: 26px; font-weight: bold; color: {color}; background: transparent;')
    val_lbl.setObjectName('stat_value')
    top.addWidget(val_lbl)

    lbl = QLabel(label)
    lbl.setStyleSheet('font-size: 11px; color: #6a8aaa; background: transparent;')

    layout.addLayout(top)
    layout.addWidget(lbl)
    card._val_label = val_lbl
    return card


class DashboardWidget(QWidget):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')

        container = QWidget()
        container.setStyleSheet('background: transparent;')
        self.main_layout = QVBoxLayout(container)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # Header
        now = datetime.now()
        header_lbl = QLabel(f'Tableau de Bord — {now.strftime("%A %d %B %Y")}')
        header_lbl.setStyleSheet('color: #6a8aaa; font-size: 12px; background: transparent;')
        self.main_layout.addWidget(header_lbl)

        # Stats grid
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(12)
        self.main_layout.addLayout(self.stats_grid)

        # Charts row
        if HAS_MPL:
            charts_row = QHBoxLayout()
            charts_row.setSpacing(12)

            self.revenue_canvas = self._make_chart_frame('Revenus Mensuels')
            self.students_canvas = self._make_chart_frame('Répartition par Classe')

            charts_row.addWidget(self.revenue_canvas[0])
            charts_row.addWidget(self.students_canvas[0])
            self.main_layout.addLayout(charts_row)

        # Notifications
        notif_frame = QFrame()
        notif_frame.setStyleSheet("""
            QFrame { background: #0d1832; border: 1px solid #1e3a5f; border-radius: 10px; }
        """)
        notif_layout = QVBoxLayout(notif_frame)
        notif_layout.setContentsMargins(16, 12, 16, 12)

        notif_title = QLabel('🔔  Notifications & Alertes')
        notif_title.setStyleSheet('color: #00d4ff; font-size: 14px; font-weight: bold; background: transparent;')
        notif_layout.addWidget(notif_title)

        self.notif_container = QVBoxLayout()
        notif_layout.addLayout(self.notif_container)
        self.main_layout.addWidget(notif_frame)
        self.main_layout.addStretch()

        scroll.setWidget(container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _make_chart_frame(self, title):
        frame = QFrame()
        frame.setStyleSheet('QFrame { background: #0d1832; border: 1px solid #1e3a5f; border-radius: 10px; }')
        frame.setMinimumHeight(250)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        lbl = QLabel(title)
        lbl.setStyleSheet('color: #00d4ff; font-size: 13px; font-weight: bold; background: transparent;')
        layout.addWidget(lbl)
        placeholder = QLabel('Chargement...')
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet('color: #3a5a7a; background: transparent;')
        layout.addWidget(placeholder)
        frame._layout = layout
        frame._placeholder = placeholder
        return frame, layout

    def _load_data(self):
        from models.database import Student, Payment, Employee, Expense
        session = self.session

        try:
            total_students = session.query(Student).filter_by(active=True).count()
            total_transport = session.query(Student).filter_by(active=True, transport=True).count()
            total_teachers = session.query(Employee).filter_by(active=True, role='teacher').count()
            total_staff = session.query(Employee).filter_by(active=True).count()

            year = datetime.now().year
            month = datetime.now().month
            payments = session.query(Payment).all()
            monthly_rev = sum(p.amount for p in payments if p.payment_date and p.payment_date.month == month and p.payment_date.year == year)
            yearly_rev = sum(p.amount for p in payments if p.payment_date and p.payment_date.year == year)
            expenses = session.query(Expense).all()
            yearly_exp = sum(e.amount for e in expenses if e.date and e.date.year == year)
            profit = yearly_rev - yearly_exp

            unpaid = session.query(Student).filter_by(active=True).filter(
                Student.monthly_fee > 0
            ).count()
        except:
            total_students = total_transport = total_teachers = total_staff = 0
            monthly_rev = yearly_rev = yearly_exp = profit = unpaid = 0

        cards_data = [
            ('🎓', 'Total Élèves', total_students, '#00d4ff'),
            ('💰', 'Revenus du mois', f'{monthly_rev:.0f} MAD', '#00ff88'),
            ('📊', 'Revenus annuels', f'{yearly_rev:.0f} MAD', '#8866ff'),
            ('💸', 'Dépenses annuelles', f'{yearly_exp:.0f} MAD', '#ff6644'),
            ('📈', 'Bénéfice net', f'{profit:.0f} MAD', '#ffaa00'),
            ('🚌', 'Transport', total_transport, '#00aaff'),
            ('👨‍🏫', 'Enseignants', total_teachers, '#ff88aa'),
            ('👥', 'Personnel total', total_staff, '#aaffaa'),
        ]

        # Clear existing
        for i in reversed(range(self.stats_grid.count())):
            self.stats_grid.itemAt(i).widget().setParent(None)

        for idx, (icon, label, value, color) in enumerate(cards_data):
            card = make_stat_card(icon, label, value, color)
            self.stats_grid.addWidget(card, idx // 4, idx % 4)

        # Charts
        if HAS_MPL:
            self._draw_revenue_chart(payments)
            self._draw_class_chart(session)

        # Notifications
        self._load_notifications(session)

    def _draw_revenue_chart(self, payments):
        from models.database import Payment
        frame, layout = self.revenue_canvas
        if frame._placeholder:
            frame._placeholder.setParent(None)

        fig = Figure(figsize=(5, 3), facecolor='#0d1832')
        ax = fig.add_subplot(111, facecolor='#0d1832')

        months_labels = ['Sep','Oct','Nov','Déc','Jan','Fév','Mar','Avr','Mai','Juin','Juil','Aoû']
        month_nums = list(range(1, 13))
        year = datetime.now().year
        rev_by_month = []
        for m in month_nums:
            total = sum(p.amount for p in payments if p.payment_date and p.payment_date.month == m and p.payment_date.year == year)
            rev_by_month.append(total)

        bars = ax.bar(months_labels, rev_by_month, color='#0066cc', alpha=0.8, width=0.6)
        ax.plot(months_labels, rev_by_month, color='#00d4ff', linewidth=2, marker='o', markersize=4)

        ax.set_facecolor('#0d1832')
        ax.tick_params(colors='#6a8aaa', labelsize=8)
        ax.spines['bottom'].set_color('#1e3a5f')
        ax.spines['left'].set_color('#1e3a5f')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.yaxis.label.set_color('#6a8aaa')
        fig.tight_layout(pad=1.0)

        canvas = FigureCanvas(fig)
        canvas.setStyleSheet('background: transparent;')
        layout.addWidget(canvas)

    def _draw_class_chart(self, session):
        from models.database import Student
        from themes.style import CLASSES
        frame, layout = self.students_canvas
        if frame._placeholder:
            frame._placeholder.setParent(None)

        counts = []
        labels = []
        for cls in CLASSES:
            c = session.query(Student).filter_by(class_name=cls, active=True).count()
            if c > 0:
                counts.append(c)
                labels.append(cls)

        if not counts:
            counts = [1]; labels = ['Aucun']

        fig = Figure(figsize=(5, 3), facecolor='#0d1832')
        ax = fig.add_subplot(111, facecolor='#0d1832')
        colors_list = ['#00d4ff','#0066ff','#8866ff','#ff6644','#00ff88','#ffaa00','#ff88aa','#aaffaa']
        wedges, texts, autotexts = ax.pie(counts, labels=labels, autopct='%1.0f%%',
            colors=colors_list[:len(counts)], textprops={'color':'#c0d0e0','fontsize':8},
            pctdistance=0.8)
        for at in autotexts:
            at.set_fontsize(7)
        fig.tight_layout(pad=0.5)

        canvas = FigureCanvas(fig)
        canvas.setStyleSheet('background: transparent;')
        layout.addWidget(canvas)

    def _load_notifications(self, session):
        from models.database import Student, Salary, Employee
        for i in reversed(range(self.notif_container.count())):
            w = self.notif_container.itemAt(i).widget()
            if w:
                w.setParent(None)

        notifs = []
        try:
            unpaid_count = session.query(Student).filter_by(active=True).filter(
                Student.insurance_paid == False
            ).count()
            if unpaid_count > 0:
                notifs.append(('⚠', f'{unpaid_count} élèves sans assurance payée', '#ffaa00'))

            transport_count = session.query(Student).filter_by(active=True, transport=True).count()
            notifs.append(('🚌', f'{transport_count} élèves inscrits au transport', '#00d4ff'))

            total = session.query(Student).filter_by(active=True).count()
            notifs.append(('🎓', f'{total} élèves actifs inscrits cette année', '#00ff88'))
        except:
            pass

        if not notifs:
            notifs.append(('✅', 'Aucune alerte en ce moment', '#00ff88'))

        for icon, msg, color in notifs:
            row = QFrame()
            row.setStyleSheet(f'QFrame {{ background: rgba(30,58,95,0.4); border-left: 3px solid {color}; border-radius: 4px; margin: 2px 0; }}')
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 8, 12, 8)
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet('font-size: 16px; background: transparent;')
            msg_lbl = QLabel(msg)
            msg_lbl.setStyleSheet(f'color: #c0d0e0; font-size: 12px; background: transparent;')
            row_layout.addWidget(icon_lbl)
            row_layout.addWidget(msg_lbl)
            row_layout.addStretch()
            self.notif_container.addWidget(row)

    def refresh(self):
        self._load_data()
