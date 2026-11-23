import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

FEATURES = ["day_of_week", "month", "day_of_year", "is_weekend", "department_code"]

def train_and_forecast(patient_df, horizon=7):
    df = patient_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    daily = df.groupby(["date", "department"], as_index=False)["patient_count"].sum()
    departments = sorted(daily["department"].unique())
    dept_map = {name: i for i, name in enumerate(departments)}
    daily["department_code"] = daily["department"].map(dept_map)
    daily["day_of_week"] = daily["date"].dt.dayofweek
    daily["month"] = daily["date"].dt.month
    daily["day_of_year"] = daily["date"].dt.dayofyear
    daily["is_weekend"] = (daily["day_of_week"] >= 5).astype(int)

    X = daily[FEATURES]
    y = daily["patient_count"]
    split = max(1, int(len(daily) * .8))
    model = RandomForestRegressor(n_estimators=160, random_state=42, min_samples_leaf=2)
    model.fit(X.iloc[:split], y.iloc[:split])
    pred_test = model.predict(X.iloc[split:]) if split < len(daily) else model.predict(X.iloc[-1:])
    actual_test = y.iloc[split:] if split < len(daily) else y.iloc[-1:]
    mae = float(mean_absolute_error(actual_test, pred_test))
    rmse = float(np.sqrt(mean_squared_error(actual_test, pred_test)))

    future_dates = pd.date_range(daily["date"].max() + pd.Timedelta(days=1), periods=horizon)
    rows = []
    for date in future_dates:
        for dept in departments:
            row = pd.DataFrame([{
                "day_of_week": date.dayofweek, "month": date.month,
                "day_of_year": date.dayofyear,
                "is_weekend": int(date.dayofweek >= 5),
                "department_code": dept_map[dept]
            }])
            value = max(0, int(round(model.predict(row[FEATURES])[0])))
            rows.append({"date": date.date().isoformat(), "department": dept,
                         "predicted_patients": value})
    return pd.DataFrame(rows), {"mae": mae, "rmse": rmse, "model": "Random Forest Regressor"}
