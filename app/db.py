import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from secrets_utils import get_secret

load_dotenv()

DATABASE_URL = get_secret("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS predictions (
                id SERIAL PRIMARY KEY,
                age INT,
                heart_rate FLOAT,
                systolic_bp FLOAT,
                diastolic_bp FLOAT,
                glucose FLOAT,
                creatinine FLOAT,
                troponin FLOAT,
                los FLOAT,
                prediction INT,
                probability FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()

def save_prediction(data: dict):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO predictions (
                age, heart_rate, systolic_bp, diastolic_bp,
                glucose, creatinine, troponin, los,
                prediction, probability
            )
            VALUES (
                :age, :heart_rate, :systolic_bp, :diastolic_bp,
                :glucose, :creatinine, :troponin, :los,
                :prediction, :probability
            );
        """), data)
        conn.commit()

def fetch_predictions():
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM predictions ORDER BY created_at DESC;")
        )
        return result.fetchall()
