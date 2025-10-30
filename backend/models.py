from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime
from typing import Generator

DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="student", nullable=False)  # 'student' or 'administrator'
    full_name = Column(String, nullable=True)
    predictions = relationship("Prediction", back_populates="user")

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    features = Column(Text)
    prediction = Column(Integer)
    proba_1 = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class StudentMetrics(Base):
    __tablename__ = "student_metrics"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test1 = Column(Float, nullable=True)
    test2 = Column(Float, nullable=True)
    test3 = Column(Float, nullable=True)
    avg_percent = Column(Float, nullable=True)
    attendance = Column(Float, nullable=True)
    pass_probability = Column(Float, nullable=True)
    predicted_next_exam = Column(Float, nullable=True)
    suggestion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
    # Lightweight migration: add missing columns if DB was created before
    with engine.connect() as conn:
        # users.role
        res = conn.exec_driver_sql("PRAGMA table_info(users)").fetchall()
        cols = {r[1] for r in res}
        if "role" not in cols:
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'student'")
        if "full_name" not in cols:
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN full_name TEXT NULL")
        # predictions.proba_1
        res = conn.exec_driver_sql("PRAGMA table_info(predictions)").fetchall()
        cols = {r[1] for r in res}
        if "proba_1" not in cols:
            conn.exec_driver_sql("ALTER TABLE predictions ADD COLUMN proba_1 REAL")
        # messages table
        try:
            conn.exec_driver_sql("SELECT 1 FROM messages LIMIT 1")
        except Exception:
            conn.exec_driver_sql(
                "CREATE TABLE IF NOT EXISTS messages (\n"
                "id INTEGER PRIMARY KEY,\n"
                "from_user_id INTEGER NOT NULL,\n"
                "to_user_id INTEGER NOT NULL,\n"
                "text TEXT NOT NULL,\n"
                "created_at DATETIME\n)"
            )
        # student_metrics table
        try:
            conn.exec_driver_sql("SELECT 1 FROM student_metrics LIMIT 1")
        except Exception:
            conn.exec_driver_sql(
                "CREATE TABLE IF NOT EXISTS student_metrics (\n"
                "id INTEGER PRIMARY KEY,\n"
                "user_id INTEGER NOT NULL,\n"
                "test1 REAL,\n"
                "test2 REAL,\n"
                "test3 REAL,\n"
                "avg_percent REAL,\n"
                "attendance REAL,\n"
                "pass_probability REAL,\n"
                "predicted_next_exam REAL,\n"
                "suggestion TEXT,\n"
                "created_at DATETIME\n)"
            )
        # add missing columns to student_metrics
        res = conn.exec_driver_sql("PRAGMA table_info(student_metrics)").fetchall()
        sm_cols = {r[1] for r in res}
        if "avg_percent" not in sm_cols:
            conn.exec_driver_sql("ALTER TABLE student_metrics ADD COLUMN avg_percent REAL")
        if "attendance" not in sm_cols:
            conn.exec_driver_sql("ALTER TABLE student_metrics ADD COLUMN attendance REAL")

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
