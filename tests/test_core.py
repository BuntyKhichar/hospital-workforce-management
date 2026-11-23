import pandas as pd
from utils.data_generator import generate_patients, generate_staff
from models.forecast import train_and_forecast
from utils.scheduler import create_schedule

def test_forecast_returns_rows():
    data = generate_patients(days=80)
    forecast, metrics = train_and_forecast(data, 7)
    assert len(forecast) == 7 * data.department.nunique()
    assert (forecast.predicted_patients >= 0).all()
    assert metrics["mae"] >= 0

def test_scheduler_no_duplicate_staff_shift():
    staff = generate_staff()
    demand = pd.DataFrame([{"department":"Emergency","role":"Doctor","required":2}])
    schedule, summary = create_schedule(staff, demand, "2026-11-25")
    assert not schedule.duplicated(["staff_id","shift"]).any()
    assert int(summary.allocated.sum()) <= 2
