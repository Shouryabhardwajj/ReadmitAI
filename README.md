# ReadmitAI - Readmission prediction for heart failure patients

ReadmitAI is a machine-learning powered clinical decision-support tool that predicts **30‑day readmission risk for heart failure patients at discharge** using real ICU data (MIMIC‑III heart failure cohort). It helps clinicians identify **high‑risk patients** early and plan targeted follow‑up to reduce avoidable readmissions.




- [Figma UI Design](https://www.figma.com/design/dROJAWxaz4Zz8wxyggXs4b/Untitled?node-id=0-1&p=f&t=gXgsgLNkeIDbzD6W-0)

- [Information Architecture](https://fire-plan-26174977.figma.site)

- [Test Case Document](https://docs.google.com/document/d/1jLI6TseUjNur3rrGg-d-QmnYgvY9BbLw/)

- [Video Presentation](https://drive.google.com/file/d/1zrqX5ln2uUaaw6uo5teONhpi1w0f2msx/view)

---

## Problem Statement:

Hospitals struggle with high **30‑day readmission rates** in heart failure patients, which leads to poor outcomes and financial penalties.  

ReadmitAI addresses this by:
- Analyzing discharge‑time vitals, labs, demographics, and medications.  
- Predicting whether a patient is **likely to be readmitted within 30 days**.  
- Providing a simple web UI for clinicians to input patient data, view risk, and email a PDF report for documentation.

---

##  Key Features:

- **Heart Failure Readmission Risk** – Predicts 30‑day readmission probability from 14+ discharge‑time clinical features.  
-  **Threshold‑tuned ML Model** – GradientBoostingClassifier with custom probability threshold to **prioritize recall** on an imbalanced dataset.  
-  **Streamlit Web Interface** – Two tabs:
    - **Predict**: Input patient details and get immediate risk prediction.
    - **History & Analytics**: View past predictions and basic analytics.
- **Persistent Storage (PostgreSQL/Neon)** – Every prediction is stored with patient features, risk score, and IST timestamp.  
-  **PDF Report Generator** – Generates a structured clinical PDF for any prediction and emails it to the requested address.  
-  **Email Integration** – Sends the PDF report via SMTP (Gmail) with basic rate‑limiting and error handling.  
-  **Documented QA** – Manual test cases written against each requirement (functional, error handling, and edge cases).  
-  **Modular Codebase** – Separate modules for DB access, ML model, PDF generation, and email utilities.

---

## Tech Stack

| Area          | Tools / Libraries                 |
|---------------|-----------------------------------|
| Interface     | Streamlit, Python                 |
| ML & Data     | scikit-learn, pandas, numpy       |
| Database      | Neon PostgreSQL, psycopg2         |
| PDFs          | ReportLab                         |
| Email         | smtplib, email                    |
| Deployment    | Streamlit Cloud                   |

---

## Project Structure

``` 
ReadmitAI/
├── app/
│   ├── app.py               # Streamlit UI (Predict + History & Analytics)
│   ├── db.py                # Database connection + CRUD helpers
│   ├── email_utils.py       # Email sending utilities (SMTP, formatting)
│   ├── pdf_utils.py         # PDF report creation via ReportLab
│   ├── requirements.txt     # Python dependencies for app
│   └── secrets_utils.py     # Helpers for loading secrets / env vars
│
├── data/
│   └── heart_failure_dataset.csv  # Processed heart failure dataset (MIMIC-III Open Access)
|
├── docs/
│   └── Test Case.docx       # Manual test cases for quality assurance
|
├── images/                  # Output images of EDA and App UI
│
├── models/
│   ├── best.pkl             # Trained scikit-learn Pipeline (preprocessing + model)
│   └── threshold.pkl        # Tuned probability threshold for classification
│
├── notebook/
│   └── heart_failure_readmission_prediction.ipynb # EDA, preprocessing, model training, evaluation
│                     
├── LICENSE
└── README.md
```

---

##  Data & Modeling Overview

- **Dataset**: Heart failure subset derived from MIMIC‑III Clinical Database Open Access.  
- **Rows / Columns**: ~7K encounters, 38 engineered features (demographics, vitals, labs, meds, admission type/location, LOS, etc.).  
- **Target Variable**: readmission_30d (0 = no readmission, 1 = readmitted within 30 days).   

### Modeling Approach

- End‑to‑end **scikit‑learn Pipeline**:
  - Numeric branch → RobustScaler.  
  - Categorical branch → OneHotEncoder(handle_unknown="ignore").  
- Core model: **GradientBoostingClassifier** (300 estimators, learning_rate=0.05, max_depth=3).  
- **GroupShuffleSplit** on subject_id for patient‑level train/test separation.  
- Tuned a **custom probability threshold** (instead of 0.5) to favor **recall** for readmission cases.  

---

## System Architecture

![System Architecture](images/System%20Architecture.png)
---

##  QA & Test Cases

- Requirements documented from the problem statement (ML + UI + deployment).  
- For each requirement, **manual test cases** were written and validated.  
- Coverage includes: prediction logic, DB operations, PDF content, email success/failure, invalid inputs, and edge cases.

---

##  Local Setup & Running the App

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/readmitai.git
cd readmitai/app
```
### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a .env file in the project root (or configure Streamlit Cloud secrets):

```bash
DATABASE_URL=YOUR_DATABASE_URL 
EMAIL_FROM=YOUR_EMAIL_ID
EMAIL_PASSWORD=SMTP_EMAIL_PASSWORD
```


### 5. Run the App

Run http://localhost:8501 in your browser.

---

## Deployment

- Hosted on **Streamlit Cloud**.  
- Connected to a **public GitHub repository** for CI/CD.  
- Secrets (DB credentials, email password) are stored in Streamlit **Secrets Manager**.  
---

##  Team
- **Team Name**: ReadmitAI