import os
import streamlit as st
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt

from db import init_db, save_prediction, fetch_predictions
from pdf_utils import generate_pdf
from email_utils import send_email

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")

pipeline = joblib.load(os.path.join(MODELS_DIR, "best.pkl"))
saved_threshold = joblib.load(os.path.join(MODELS_DIR, "threshold.pkl"))

if isinstance(saved_threshold, (list, tuple, np.ndarray)):
    saved_threshold = float(saved_threshold[0])
threshold = float(saved_threshold)
if threshold > 0.2:
    threshold = 0.05

EXPECTED_COLUMNS = pipeline.named_steps["preprocessing"].feature_names_in_

init_db()

st.set_page_config(page_title="Heart Failure Readmission", layout="wide")
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Predict", "History & Analytics"])

if page == "Predict":
    st.markdown(
        "<h2 style='text-align: center;'>Heart Failure Readmission Prediction</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: gray;'>Enter discharge-time clinical details to estimate 30-day readmission risk.</p>",
        unsafe_allow_html=True,
    )

    with st.form("prediction_form"):
        st.subheader("Patient details")

        col1, col2 = st.columns(2)

        with col1:
            age = st.number_input("Age at admission", 18, 100, value=60)
            heart_rate = st.number_input("Heart Rate", 30.0, 200.0, value=80.0)
            systolic_bp = st.number_input("Systolic BP", 60.0, 250.0, value=120.0)
            diastolic_bp = st.number_input("Diastolic BP", 30.0, 150.0, value=80.0)
            respiratory_rate = st.number_input("Respiratory Rate", 5.0, 60.0, value=18.0)
            spo2 = st.number_input("Oxygen Saturation (SpO₂)", 70.0, 100.0, value=96.0)
            glucose = st.number_input("Glucose", 40.0, 600.0, value=110.0)

        with col2:
            los = st.number_input("Length of Stay (Days)", 0.1, 365.0, value=5.0)
            creatinine = st.number_input("Creatinine", 0.1, 10.0, value=1.0)
            troponin = st.number_input("Troponin", 0.0, 100.0, value=0.1)
            bun = st.number_input("BUN", 1.0, 200.0, value=20.0)
            hemoglobin = st.number_input("Hemoglobin", 3.0, 20.0, value=13.0)
            temperature = st.number_input("Temperature (°C)", 30.0, 45.0, value=37.0)
            hdl = st.number_input("HDL", 5.0, 150.0, value=45.0)

        email = st.text_input("Email for PDF Report (optional)")
        submit = st.form_submit_button("🔮 Predict Risk", type="primary")

    if submit:
        input_df = pd.DataFrame({col: [np.nan] for col in EXPECTED_COLUMNS})

        input_mapping = {
            "age_at_admission": age,
            "heart_rate": heart_rate,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "glucose": glucose,
            "creatinine": creatinine,
            "troponin": troponin,
            "los": los,
            "respiratory_rate": respiratory_rate,
            "spo2": spo2,
            "bun": bun,
            "hemoglobin": hemoglobin,
            "temperature": temperature,
            "hdl": hdl
        }
        
        for col, value in input_mapping.items():
            if col in EXPECTED_COLUMNS:
                input_df.loc[0, col] = value

        if "log_los" in EXPECTED_COLUMNS:
            input_df.loc[0, "log_los"] = np.log1p(los)

        if "age_group" in EXPECTED_COLUMNS:
            if age <= 40:
                input_df.loc[0, "age_group"] = "young"
            elif age <= 60:
                input_df.loc[0, "age_group"] = "middle"
            elif age <= 75:
                input_df.loc[0, "age_group"] = "senior"
            else:
                input_df.loc[0, "age_group"] = "elderly"

        binary_defaults = ["aspirin", "statins", "beta_blockers", "diuretics"]
        for col in binary_defaults:
            if col in EXPECTED_COLUMNS:
                input_df.loc[0, col] = 0

        categorical_defaults = {
            "gender": "unknown",
            "ethnicity": "unknown",
            "insurance": "unknown",
            "admission_type": "UNKNOWN",
            "admission_location": "UNKNOWN",
        }
        for col, val in categorical_defaults.items():
            if col in EXPECTED_COLUMNS:
                input_df.loc[0, col] = val

        num_cols = input_df.select_dtypes(include=[np.number]).columns
        cat_cols = input_df.select_dtypes(exclude=[np.number]).columns
        input_df[num_cols] = input_df[num_cols].fillna(0)
        input_df[cat_cols] = input_df[cat_cols].fillna("unknown")

        prob = pipeline.predict_proba(input_df)[0][1]
        pred = int(prob >= threshold)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.metric("30-Day Readmission Risk", f"{prob:.1%}")
        with col2:
            risk_color = "🟢 Low" if pred == 0 else "🔴 High"
            st.markdown(f"**{risk_color}**")

        risk_label = "High Readmission Risk" if pred == 1 else "Low Readmission Risk"
        st.success(risk_label)
        st.info(f"Model confidence: **{prob:.3f}**")

        record = {
            "age": age,
            "heart_rate": heart_rate,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "glucose": glucose,
            "creatinine": creatinine,
            "troponin": troponin,
            "los": los,
            "respiratory_rate": respiratory_rate,
            "prediction": pred,
            "probability": float(prob)
        }
        save_prediction(record)

        if email:
            pdf_path = generate_pdf(record)
            send_email(email, pdf_path, record)
            st.success("✅ PDF Report emailed!")

else:
    st.title("📋 Prediction History & Analytics")

    records = fetch_predictions()
    if records:
        df_history = pd.DataFrame(records, columns=[
            'id', 'age', 'heart_rate', 'systolic_bp', 'diastolic_bp',
            'glucose', 'creatinine', 'troponin', 'los', 'respiratory_rate',
            'prediction', 'probability', 'created_at'
        ])
        
        st.dataframe(df_history.tail(20), use_container_width=True)

        st.subheader("Prediction Distribution")
        preds = [int(r.prediction) for r in records]
        fig, ax = plt.subplots()
        ax.hist(preds, bins=[-0.5, 0.5, 1.5], rwidth=0.8, color=['green', 'red'])
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Low Risk', 'High Risk'])
        ax.set_xlabel("Prediction")
        ax.set_ylabel("Count")
        st.pyplot(fig)

        st.subheader("📧 Send PDF Report by ID")
        email = st.text_input("Recipient Email")
        selected_id = st.number_input("Prediction ID", min_value=1, step=1)

        if st.button("Generate PDF & Send Email"):
            row = next((r for r in records if r.id == selected_id), None)
            if row is None:
                st.error(f"No prediction found with id = {selected_id}")
            else:
                data_dict = dict(row._mapping)
                pdf_path = generate_pdf(data_dict)
                send_email(email, pdf_path, data_dict)
                st.success(f"✅ Email sent for prediction ID {selected_id}")

    else:
        st.info("No prediction history available. Make some predictions first!")
