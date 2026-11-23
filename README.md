# AI-Powered Hospital Workforce & Patient Flow Management System

A college-level, end-to-end analytics prototype built with Python, Streamlit, SQLite, scikit-learn and Plotly.

## Features
- Hospital overview dashboard and patient-flow analytics
- Random Forest patient-volume forecast for 3–14 days
- Validation metrics (MAE and RMSE)
- Staff directory and CSV import/export
- Draft shift allocation with department/role demand coverage
- SQLite persistence for patients, staff, schedules and predictions
- Synthetic sample data (no real patient information)

## Run locally
Python 3.10+ recommended.

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
# .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app creates `database/hospital.db` and seeds synthetic data on first run.

## Tests
```bash
pip install pytest
pytest -q
```

## Dataset
The app generates 400 days of synthetic department-level patient data and 60 synthetic staff records. You can replace these using CSV uploads.

## Important limitations
- Forecast is a teaching demonstration, not validated for hospital operations.
- The scheduler is a greedy heuristic, not a globally optimal solver. It demonstrates allocation and shortage reporting; it does not enforce weekly rest, legal working-hour, credential, or consecutive-night constraints.
- Synthetic data does not represent any real hospital.
- Do not upload identifiable patient information.
