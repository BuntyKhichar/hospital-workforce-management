import pandas as pd
from collections import defaultdict

SHIFTS = ["Morning", "Evening", "Night"]

def create_schedule(staff_df, demand_df, schedule_date):
    """Greedy demonstrator scheduler. Allocates available staff to role/department demand."""
    staff = staff_df.copy()
    staff["available"] = staff["available"].astype(bool)
    assignments = []
    used_per_day = set()
    demand = demand_df.copy()

    for _, need in demand.iterrows():
        dept, role = need["department"], need["role"]
        required = max(0, int(need["required"]))
        candidates = staff[
            (staff["department"] == dept) &
            (staff["role"] == role) &
            (staff["available"])
        ].sort_values("staff_id")
        allocated = 0
        for _, person in candidates.iterrows():
            if allocated >= required:
                break
            # Rotate shift by staff index for a simple, explainable demo schedule.
            shift = SHIFTS[(int(person["staff_id"][-3:]) + len(assignments)) % 3]
            if (person["staff_id"], shift) in used_per_day:
                continue
            assignments.append({
                "schedule_date": str(schedule_date), "shift": shift,
                "department": dept, "staff_id": person["staff_id"],
                "staff_name": person["name"], "role": role
            })
            used_per_day.add((person["staff_id"], shift))
            allocated += 1
    result = pd.DataFrame(assignments)
    if result.empty:
        return result, pd.DataFrame()
    summary = demand.copy()
    actual = result.groupby(["department", "role"]).size().rename("allocated")
    summary = summary.merge(actual, on=["department", "role"], how="left")
    summary["allocated"] = summary["allocated"].fillna(0).astype(int)
    summary["shortage"] = (summary["required"] - summary["allocated"]).clip(lower=0)
    return result, summary
