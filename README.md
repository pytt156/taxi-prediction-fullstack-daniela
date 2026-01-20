# Taxi Price Prediction

## Purpose and Goals
This project demonstrates an end-to-end machine learning workflow for predicting taxi prices based on structured trip data.
It is designed as an educational and portfolio project, with emphasis on correctness, reproducibility, and clean software structure rather than maximum predictive performance.

The project focuses on:
- building a reproducible ML pipeline
- avoiding data leakage
- separating data processing, modeling, API, and frontend concerns
- exposing predictions via an API and a simple frontend
- applying realistic MLOps-oriented project structure

---

## Project Structure

    .
    ├── assets/                # Images and screenshots used in documentation
    ├── data/
    │   ├── raw/               # Original, immutable dataset
    │   └── processed/         # Cleaned data used for training
    ├── notebooks/             # EDA, data cleaning, evaluation, pipelines
    ├── models/                # Trained model artifacts
    ├── src/
    │   └── taxipred/
    │       ├── backend/       # FastAPI application
    │       ├── frontend/      # Streamlit application
    │       └── utils/         # Shared business & ML logic
    ├── pyproject.toml
    └── uv.lock
---

## How to Use This Repo

### 1. Install dependencies
This project uses pyproject.toml and uv.lock.

Using uv:
    uv sync

Or using pip:
    pip install -e .

---

### 2. Run the API (FastAPI)

    uvicorn taxipred.backend.api:app --reload

Open Swagger UI:
    http://127.0.0.1:8000/docs

---

### 3. Run the Frontend (Streamlit)

    streamlit run src/taxipred/frontend/app.py

---

### 4. Model Artifact
The trained model is stored at:

    models/taxi_price_predictor.joblib

It is loaded by the prediction logic during inference.

---

## Notebooks Overview
- 01_eda.ipynb: Dataset exploration and sanity checks
- 02_data_cleaning.ipynb: Cleaning and exporting processed data
- 03_model_test_eval.ipynb: Model comparison and evaluation
- 04_creating_pipeline.ipynb: Building and serializing the final pipeline

---

## Insights

### Separation of concerns
- Notebooks are used for experimentation only.
- Production logic lives under src/.
- API, frontend, and model logic are decoupled.

### Reproducibility
- Raw data remains immutable.
- Processed data and model artifacts are versioned.
- Dependency versions are pinned.

### ML best practices
- Preprocessing logic is shared between training and inference.
- Clear boundaries reduce risk of data leakage.

---

## Screenshots

Frontend UI:
    assets/..

API (Swagger):
    assets/..

Model evaluation:
    assets/..

---

## Known Limitations
- This is a learning project.
- No monitoring, CI/CD, or production deployment is included.
- Changes to features require retraining the model.

---