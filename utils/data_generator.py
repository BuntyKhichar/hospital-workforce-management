import numpy as np
import pandas as pd

DEPARTMENTS = ["Emergency", "Cardiology", "Orthopedics", "Pediatrics", "General Medicine"]

def generate_patients(days=400, seed=42):
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=days, freq="D")
    rows = []
    base = {"Emergency": 38, "Cardiology": 22, "Orthopedics": 25,
            "Pediatrics": 20, "General Medicine": 45}
    for date in dates:
        weekend_factor = 1.12 if date.dayofweek >= 5 else 1.0
        seasonal = 1 + 0.12 * np.sin(2 * np.pi * date.dayofyear / 365)
        for dept in DEPARTMENTS:
            count = max(5, int(rng.normal(base[dept] * weekend_factor * seasonal, 6)))
            avg_wait = max(5, rng.normal(18 + count * 0.22, 5))
            rows.append({
                "date": date.date().isoformat(),
                "department": dept,
                "patient_count": count,
                "avg_wait_minutes": round(float(avg_wait), 1),
                "peak_hour": int(rng.choice([9, 10, 11, 16, 17, 18], p=[.12,.18,.18,.16,.2,.16]))
            })
    return pd.DataFrame(rows)

def generate_staff(seed=43):
    rng = np.random.default_rng(seed)
    rows = []
    departments = DEPARTMENTS
    roles = ["Doctor", "Nurse", "Support"]
    for i in range(1, 61):
        dept = departments[(i - 1) % len(departments)]
        role = roles[(i - 1) % len(roles)]
        rows.append({
            "staff_id": f"STF{i:03d}",
            "name": f"Employee {i:02d}",
            "role": role,
            "department": dept,
            "available": True,
            "max_shifts_per_week": int(rng.choice([4, 5, 6]))
        })
    return pd.DataFrame(rows)
