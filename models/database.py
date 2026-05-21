
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'school.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f'sqlite:///{DB_PATH}', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # admin, comptable, secretaire
    full_name = Column(String(100))
    email = Column(String(100))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    code = Column(String(20), unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    photo = Column(String(255))
    gender = Column(String(10))
    birth_date = Column(Date)
    address = Column(Text)
    parent_name = Column(String(100))
    parent_phone = Column(String(20))
    emergency_phone = Column(String(20))
    class_name = Column(String(20))
    registration_date = Column(Date, default=datetime.today)
    transport = Column(Boolean, default=False)
    insurance_paid = Column(Boolean, default=False)
    monthly_fee = Column(Float, default=0.0)
    notes = Column(Text)
    active = Column(Boolean, default=True)
    payments = relationship('Payment', back_populates='student')


class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    payment_type = Column(String(20))  # monthly, insurance, transport
    amount = Column(Float)
    month = Column(String(20))
    year = Column(Integer)
    payment_date = Column(DateTime, default=datetime.now)
    receipt_number = Column(String(30))
    notes = Column(Text)
    student = relationship('Student', back_populates='payments')


class Receipt(Base):
    __tablename__ = 'receipts'
    id = Column(Integer, primary_key=True)
    receipt_number = Column(String(30), unique=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    payment_id = Column(Integer, ForeignKey('payments.id'))
    amount = Column(Float)
    payment_type = Column(String(20))
    generated_at = Column(DateTime, default=datetime.now)
    pdf_path = Column(String(255))


class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    role = Column(String(50))  # teacher, staff, driver
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    hire_date = Column(Date)
    base_salary = Column(Float, default=0.0)
    active = Column(Boolean, default=True)
    salaries = relationship('Salary', back_populates='employee')


class Salary(Base):
    __tablename__ = 'salaries'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    month = Column(String(20))
    year = Column(Integer)
    base_amount = Column(Float)
    bonus = Column(Float, default=0.0)
    total = Column(Float)
    paid = Column(Boolean, default=False)
    paid_date = Column(DateTime)
    notes = Column(Text)
    employee = relationship('Employee', back_populates='salaries')


class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True)
    category = Column(String(50))
    description = Column(Text)
    amount = Column(Float)
    expense_type = Column(String(20))  # fixed, variable
    date = Column(Date, default=datetime.today)
    paid_by = Column(String(100))
    notes = Column(Text)


class Bus(Base):
    __tablename__ = 'buses'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    plate = Column(String(20))
    capacity = Column(Integer)
    driver_id = Column(Integer, ForeignKey('employees.id'))
    route = Column(Text)
    active = Column(Boolean, default=True)


class Schedule(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True)
    class_name = Column(String(20))
    day = Column(String(20))
    time_start = Column(String(10))
    time_end = Column(String(10))
    subject = Column(String(50))
    teacher_id = Column(Integer, ForeignKey('employees.id'))
    room = Column(String(20))


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    doc_type = Column(String(50))  # certificate, contract, cin, receipt, report
    related_id = Column(Integer)
    related_type = Column(String(20))  # student, employee
    file_path = Column(String(255))
    uploaded_at = Column(DateTime, default=datetime.now)
    notes = Column(Text)


class Setting(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    key = Column(String(50), unique=True)
    value = Column(Text)


def init_db():
    Base.metadata.create_all(engine)
    session = Session()
    # Create default admin if not exists
    if not session.query(User).filter_by(username='admin').first():
        import hashlib
        pw = hashlib.sha256('admin123'.encode()).hexdigest()
        admin = User(username='admin', password=pw, role='admin', full_name='Administrateur')
        comptable = User(username='comptable', password=hashlib.sha256('compta123'.encode()).hexdigest(),
                        role='comptable', full_name='Comptable')
        secretaire = User(username='secretaire', password=hashlib.sha256('secr123'.encode()).hexdigest(),
                         role='secretaire', full_name='Secrétaire')
        session.add_all([admin, comptable, secretaire])
        # Default settings
        settings = [
            Setting(key='school_name', value='Le Schéma'),
            Setting(key='school_address', value='Votre adresse'),
            Setting(key='school_phone', value=''),
            Setting(key='insurance_fee', value='500'),
            Setting(key='transport_fee', value='300'),
        ]
        session.add_all(settings)
        session.commit()
    session.close()


def get_session():
    return Session()
