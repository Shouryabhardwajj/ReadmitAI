import os

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

from secrets_utils import get_secret

load_dotenv()

DATABASE_URL = get_secret("DATABASE_URL")
engine = None


def init_db():
    global engine

    if not DATABASE_URL:
        print("No DATABASE_URL found. Running without database.")
        return

    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(
                text(
                    """
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
                        respiratory_rate FLOAT,
                        prediction INT,
                        probability FLOAT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )
            )
            conn.commit()
        print("Database initialized successfully")
    except OperationalError as e:
        engine = None
        print(f"Database connection failed: {e}. Running without database.")


def save_prediction(data: dict):
    global engine
    if not engine:
        print("No database connection. Prediction not saved.")
        return

    try:
        with engine.connect() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO predictions (
                        age, heart_rate, systolic_bp, diastolic_bp,
                        glucose, creatinine, troponin, los,
                        respiratory_rate, prediction, probability
                    )
                    VALUES (
                        :age, :heart_rate, :systolic_bp, :diastolic_bp,
                        :glucose, :creatinine, :troponin, :los,
                        :respiratory_rate, :prediction, :probability
                    );
                    """
                ),
                data,
            )
            conn.commit()
        print("Saved prediction to database.")
    except Exception as e:
        print(f"Failed to save prediction: {e}")


def fetch_predictions():
    global engine
    if not engine:
        return []

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM predictions ORDER BY created_at DESC LIMIT 50;")
            )
            return result.fetchall()
    except Exception as e:
        print(f"Failed to fetch predictions: {e}")
        return []
