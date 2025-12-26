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

        submit = st.form_submit_button("Predict")

    if submit:
        input_df = pd.DataFrame({col: [np.nan] for col in EXPECTED_COLUMNS})

        if "age_at_admission" in EXPECTED_COLUMNS:
            input_df.loc[0, "age_at_admission"] = age
        if "heart_rate" in EXPECTED_COLUMNS:
            input_df.loc[0, "heart_rate"] = heart_rate
        if "systolic_bp" in EXPECTED_COLUMNS:
            input_df.loc[0, "systolic_bp"] = systolic_bp
        if "diastolic_bp" in EXPECTED_COLUMNS:
            input_df.loc[0, "diastolic_bp"] = diastolic_bp
        if "glucose" in EXPECTED_COLUMNS:
            input_df.loc[0, "glucose"] = glucose
        if "creatinine" in EXPECTED_COLUMNS:
            input_df.loc[0, "creatinine"] = creatinine
        if "troponin" in EXPECTED_COLUMNS:
            input_df.loc[0, "troponin"] = troponin
        if "los" in EXPECTED_COLUMNS:
            input_df.loc[0, "los"] = los
        if "respiratory_rate" in EXPECTED_COLUMNS:
            input_df.loc[0, "respiratory_rate"] = respiratory_rate
        if "spo2" in EXPECTED_COLUMNS:
            input_df.loc[0, "spo2"] = spo2

        if "bun" in EXPECTED_COLUMNS:
            input_df.loc[0, "bun"] = bun
        if "hemoglobin" in EXPECTED_COLUMNS:
            input_df.loc[0, "hemoglobin"] = hemoglobin
        if "temperature" in EXPECTED_COLUMNS:
            input_df.loc[0, "temperature"] = temperature
        if "hdl" in EXPECTED_COLUMNS:
            input_df.loc[0, "hdl"] = hdl

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

        risk_label = "High Readmission Risk" if pred == 1 else "Low Readmission Risk"
        st.success(risk_label)

        if pred == 1:
            st.write(f"Model confidence for high readmission risk: **{prob:.3f}**")
        else:
            st.write(f"Model confidence for low readmission risk: **{1 - prob:.3f}**")

        save_prediction({
            "age": age,
            "heart_rate": heart_rate,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "glucose": glucose,
            "creatinine": creatinine,
            "troponin": troponin,
            "los": los,
            "prediction": pred,
            "probability": float(prob),
        })

else:
    st.title("Prediction History & Analytics")

    records = fetch_predictions()

    if records:
        st.dataframe(records)

        st.subheader("Prediction Distribution")
        preds = [int(r.prediction) for r in records]
        fig, ax = plt.subplots()
        ax.hist(preds, bins=[-0.5, 0.5, 1.5], rwidth=0.8)
        ax.set_xticks([0, 1])
        ax.set_xlabel("Prediction (0 = Low, 1 = High)")
        ax.set_ylabel("Count")
        st.pyplot(fig)

        st.subheader("Send PDF Report by ID")
        email = st.text_input("Recipient Email")
        selected_id = st.number_input("Prediction ID to send", min_value=1, step=1)

        if st.button("Generate PDF & Send Email"):
            row = next((r for r in records if r.id == selected_id), None)
            if row is None:
                st.error(f"No prediction found with id = {selected_id}")
            else:
                data_dict = dict(row._mapping)
                generate_pdf(data_dict, "prediction_report.pdf")
                send_email(email, "prediction_report.pdf", data_dict)
                st.success(f"Email sent successfully for prediction id {selected_id}")

    else:
        st.info("No prediction history available.")