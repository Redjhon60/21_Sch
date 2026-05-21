
DARK_THEME = """
QWidget {
    background-color: #0a0e1a;
    color: #e0e6f0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #0a0e1a;
}

/* Sidebar */
#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #0d1228, stop:1 #070b18);
    border-right: 1px solid #1e3a5f;
    min-width: 220px;
    max-width: 220px;
}

#sidebar_logo {
    padding: 20px;
    border-bottom: 1px solid #1e3a5f;
}

#school_title {
    color: #00d4ff;
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 1px;
}

#school_subtitle {
    color: #6a8aaa;
    font-size: 10px;
}

/* Sidebar buttons */
QPushButton#nav_btn {
    background: transparent;
    border: none;
    color: #8a9bb0;
    text-align: left;
    padding: 12px 20px;
    border-radius: 0px;
    font-size: 13px;
}

QPushButton#nav_btn:hover {
    background: rgba(0, 212, 255, 0.08);
    color: #00d4ff;
    border-left: 3px solid #00d4ff;
}

QPushButton#nav_btn:checked {
    background: rgba(0, 212, 255, 0.15);
    color: #00d4ff;
    border-left: 3px solid #00d4ff;
    font-weight: bold;
}

/* Top navbar */
#topbar {
    background: rgba(13, 18, 40, 0.95);
    border-bottom: 1px solid #1e3a5f;
    min-height: 55px;
    max-height: 55px;
    padding: 0 20px;
}

#page_title {
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
}

/* Cards */
QFrame#stat_card {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0d1832, stop:1 #0a1428);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 15px;
}

QFrame#stat_card:hover {
    border: 1px solid #00d4ff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #0f1e3a, stop:1 #0c1830);
}

#stat_value {
    font-size: 28px;
    font-weight: bold;
    color: #00d4ff;
}

#stat_label {
    font-size: 12px;
    color: #6a8aaa;
}

#stat_icon {
    font-size: 24px;
}

/* Tables */
QTableWidget {
    background-color: #0d1228;
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    gridline-color: #1a2744;
    selection-background-color: rgba(0, 212, 255, 0.2);
}

QTableWidget::item {
    padding: 8px 12px;
    border-bottom: 1px solid #1a2744;
    color: #c0d0e0;
}

QTableWidget::item:selected {
    background: rgba(0, 212, 255, 0.2);
    color: #ffffff;
}

QHeaderView::section {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #162040, stop:1 #0f1830);
    color: #00d4ff;
    padding: 10px 12px;
    border: none;
    border-right: 1px solid #1e3a5f;
    border-bottom: 2px solid #00d4ff;
    font-weight: bold;
    font-size: 12px;
    letter-spacing: 0.5px;
}

/* Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0066cc, stop:1 #0044aa);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 13px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0080ff, stop:1 #0055cc);
}

QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #004499, stop:1 #003388);
}

QPushButton#btn_danger {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #cc2200, stop:1 #aa1100);
}

QPushButton#btn_danger:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #ee3300, stop:1 #cc2200);
}

QPushButton#btn_success {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #006633, stop:1 #004422);
}

QPushButton#btn_success:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #008844, stop:1 #006633);
}

QPushButton#btn_warning {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #cc7700, stop:1 #aa5500);
}

/* Input fields */
QLineEdit, QTextEdit, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox {
    background-color: #0d1832;
    border: 1px solid #1e3a5f;
    border-radius: 6px;
    color: #e0e6f0;
    padding: 8px 12px;
    selection-background-color: rgba(0, 212, 255, 0.3);
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1px solid #00d4ff;
    background-color: #0f1e3a;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #0d1832;
    border: 1px solid #1e3a5f;
    color: #e0e6f0;
    selection-background-color: rgba(0, 212, 255, 0.2);
}

/* Scrollbar */
QScrollBar:vertical {
    background: #0a0e1a;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #1e3a5f;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #00d4ff;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #0a0e1a;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: #1e3a5f;
    border-radius: 4px;
}

/* Tab widget */
QTabWidget::pane {
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    background: #0a0e1a;
}

QTabBar::tab {
    background: #0d1228;
    color: #6a8aaa;
    border: 1px solid #1e3a5f;
    padding: 8px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background: rgba(0, 212, 255, 0.15);
    color: #00d4ff;
    border-bottom: 2px solid #00d4ff;
}

QTabBar::tab:hover:!selected {
    background: rgba(0, 212, 255, 0.08);
    color: #88ccee;
}

/* Dialog */
QDialog {
    background-color: #0a0e1a;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
}

/* Labels */
QLabel#section_title {
    color: #00d4ff;
    font-size: 15px;
    font-weight: bold;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 8px;
    margin-bottom: 10px;
}

QLabel#form_label {
    color: #8a9bb0;
    font-size: 12px;
}

/* Search bar */
QLineEdit#search_bar {
    background-color: #0d1832;
    border: 1px solid #1e3a5f;
    border-radius: 20px;
    padding: 6px 15px 6px 35px;
    color: #e0e6f0;
    min-width: 250px;
}

QLineEdit#search_bar:focus {
    border: 1px solid #00d4ff;
}

/* Group box */
QGroupBox {
    border: 1px solid #1e3a5f;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    color: #00d4ff;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #00d4ff;
}

/* CheckBox */
QCheckBox {
    color: #c0d0e0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #1e3a5f;
    background: #0d1832;
}

QCheckBox::indicator:checked {
    background: #00d4ff;
    border-color: #00d4ff;
}

/* Message box */
QMessageBox {
    background-color: #0a0e1a;
}

/* Splitter */
QSplitter::handle {
    background: #1e3a5f;
}

/* Frame */
QFrame#content_frame {
    background: #0d1228;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
}

/* Status bar */
QStatusBar {
    background: #070b18;
    color: #6a8aaa;
    border-top: 1px solid #1e3a5f;
}
"""

CLASSES = ['PS', 'MS', 'GS', 'CP', 'CE1', 'CE2', 'CM1', 'CM2',
           '6EME', '1AC', '2AC', '3AC', 'TC', '1BAC', '2BAC']

MONTHS = ['Septembre', 'Octobre', 'Novembre', 'Décembre', 'Janvier',
          'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août']

PAYMENT_TYPES = ['Mensualité', 'Assurance', 'Transport']

EXPENSE_CATEGORIES = ['Électricité', 'Eau', 'Loyer', 'Matériel', 'Fournitures',
                      'Maintenance', 'Communication', 'Autre']
