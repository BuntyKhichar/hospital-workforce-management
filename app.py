import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from database.db import init_db, read_table, replace_table, clear_schedules, save_schedules
from utils.data_generator import generate_patients, generate_staff, DEPARTMENTS
from models.forecast import train_and_forecast
from utils.scheduler import create_schedule

st.set_page_config(page_title="Hospital Workforce & Patient Flow", page_icon="🏥",
                   layout="wide", initial_sidebar_state="expanded")
init_db()

st.markdown("""
<style>
.main {background:#f7f9fc;}
[data-testid="stMetric"] {
    background: #1e293b;
    color: #ffffff;
    padding: 18px;
    border: 1px solid #334155;
    border-radius: 12px;
}

[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
}
            .block-container {padding-top:1.5rem;}
</style>
""", unsafe_allow_html=True)

def seed_if_empty():
    patients = read_table("patients")
    staff = read_table("staff")
    if patients.empty:
        replace_table("patients", generate_patients())
    if staff.empty:
        replace_table("staff", generate_staff())

seed_if_empty()
patients = read_table("patients")
staff = read_table("staff")
page = st.sidebar.radio("Navigation", [
    "Overview", "Patient Analytics", "AI Forecasting",
    "Staff Management", "Shift Optimization", "Data Import & Export", "About"
])
st.sidebar.caption("Academic demonstration • Synthetic data")
st.sidebar.info("All patient and employee records are generated demo data.")

st.title("🏥 AI-Powered Hospital Workforce & Patient Flow Management")
st.caption("Predict patient demand • Forecast staffing needs • Plan employee shifts")

if page == "Overview":
    latest = pd.to_datetime(patients["date"]).max().date()
    today_data = patients[pd.to_datetime(patients["date"]).dt.date == latest]
    total = int(today_data["patient_count"].sum())
    avg_wait = float(patients["avg_wait_minutes"].mean())
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Latest-day patients", f"{total:,}")
    c2.metric("Departments", patients["department"].nunique())
    c3.metric("Active staff", int(staff["available"].astype(bool).sum()))
    c4.metric("Average waiting time", f"{avg_wait:.1f} min")
    col1,col2 = st.columns(2)
    trend = patients.copy()
    trend["date"] = pd.to_datetime(trend["date"])
    daily = trend.groupby("date", as_index=False)["patient_count"].sum().tail(45)
    col1.plotly_chart(px.line(daily, x="date", y="patient_count", title="Patient volume – last 45 days",
                              markers=True), use_container_width=True)
    dept = patients.groupby("department", as_index=False)["patient_count"].mean()
    col2.plotly_chart(px.bar(dept, x="department", y="patient_count",
                             title="Average daily patients by department", color="department"),
                      use_container_width=True)
    st.subheader("Recent patient records")
    st.dataframe(patients.tail(12), use_container_width=True, hide_index=True)

elif page == "Patient Analytics":
    st.subheader("Patient Flow Analytics")
    p = patients.copy()
    p["date"] = pd.to_datetime(p["date"])
    departments = st.multiselect("Departments", sorted(p["department"].unique()),
                                 default=sorted(p["department"].unique()))
    filtered = p[p["department"].isin(departments)]
    a,b,c = st.columns(3)
    a.metric("Total visits in dataset", f"{int(filtered.patient_count.sum()):,}")
    b.metric("Mean waiting time", f"{filtered.avg_wait_minutes.mean():.1f} min")
    c.metric("Peak hour (most frequent)", f"{int(filtered.peak_hour.mode().iloc[0])}:00")
    daily = filtered.groupby("date", as_index=False)["patient_count"].sum()
    st.plotly_chart(px.line(daily, x="date", y="patient_count", title="Daily patient inflow",
                            markers=True), use_container_width=True)
    dept = filtered.groupby("department", as_index=False).agg(
        patients=("patient_count","sum"), wait=("avg_wait_minutes","mean"))
    x,y = st.columns(2)
    x.plotly_chart(px.bar(dept, x="department", y="patients", title="Total patients by department"), use_container_width=True)
    y.plotly_chart(px.bar(dept, x="department", y="wait", title="Average waiting time (minutes)"), use_container_width=True)
    st.dataframe(dept.round(1), use_container_width=True, hide_index=True)

elif page == "AI Forecasting":
    st.subheader("7-Day Patient Inflow Forecast")
    st.write("A Random Forest regression model is trained on historical synthetic patient records.")
    horizon = st.slider("Forecast horizon (days)", 3, 14, 7)
    if st.button("Train model & generate forecast", type="primary"):
        with st.spinner("Training model and generating predictions..."):
            forecast, metrics = train_and_forecast(patients, horizon)
            st.session_state["forecast"] = forecast
            st.session_state["metrics"] = metrics
    if "forecast" in st.session_state:
        forecast = st.session_state["forecast"]
        metrics = st.session_state["metrics"]
        x,y,z = st.columns(3)
        x.metric("Model", metrics["model"])
        y.metric("Validation MAE", f'{metrics["mae"]:.2f}')
        z.metric("Validation RMSE", f'{metrics["rmse"]:.2f}')
        st.plotly_chart(px.line(forecast, x="date", y="predicted_patients", color="department",
                                markers=True, title="Predicted patients by department"),
                        use_container_width=True)
        st.dataframe(forecast, use_container_width=True, hide_index=True)
        st.download_button("Download forecast CSV", forecast.to_csv(index=False),
                           "patient_forecast.csv", "text/csv")
    else:
        st.info("Click the button to train the model and view predictions.")

elif page == "Staff Management":
    st.subheader("Staff Directory")
    st.dataframe(staff, use_container_width=True, hide_index=True)
    with st.expander("Add a staff member"):
        with st.form("add_staff"):
            sid = st.text_input("Staff ID (e.g. STF061)")
            name = st.text_input("Name")
            role = st.selectbox("Role", ["Doctor","Nurse","Support"])
            dept = st.selectbox("Department", DEPARTMENTS)
            available = st.checkbox("Available", True)
            max_shifts = st.number_input("Maximum shifts per week", 1, 7, 5)
            submitted = st.form_submit_button("Add staff")
        if submitted:
            if not sid.strip() or not name.strip():
                st.error("Staff ID and name are required.")
            elif sid in set(staff.staff_id):
                st.error("That Staff ID already exists.")
            else:
                new = pd.concat([staff, pd.DataFrame([{"staff_id":sid,"name":name,"role":role,
                    "department":dept,"available":available,"max_shifts_per_week":max_shifts}])], ignore_index=True)
                replace_table("staff", new)
                st.success("Staff member added. Refreshing data...")
                st.rerun()
    st.caption("To change existing records, export the staff CSV, edit it, then upload it in Data Import & Export.")

elif page == "Shift Optimization":
    st.subheader("Automated Staff Shift Allocation")
    st.write("This academic scheduler assigns available staff against configurable department and role requirements.")
    forecast = st.session_state.get("forecast")
    default_date = pd.Timestamp.today().date()
    schedule_date = st.date_input("Schedule date", default_date)
    st.markdown("**Required staff per department and role**")
    req_rows = []
    for dept in DEPARTMENTS:
        cols = st.columns([1,1,1,1])
        cols[0].write(dept)
        doc = cols[1].number_input(f"{dept} doctors", 0, 20, 2, key=f"{dept}_doc")
        nurse = cols[2].number_input(f"{dept} nurses", 0, 30, 3, key=f"{dept}_nurse")
        support = cols[3].number_input(f"{dept} support", 0, 20, 1, key=f"{dept}_support")
        req_rows += [{"department":dept,"role":"Doctor","required":doc},
                     {"department":dept,"role":"Nurse","required":nurse},
                     {"department":dept,"role":"Support","required":support}]
    demand = pd.DataFrame(req_rows)
    if st.button("Generate optimized schedule", type="primary"):
        schedule, summary = create_schedule(staff, demand, schedule_date)
        st.session_state["schedule"] = schedule
        st.session_state["schedule_summary"] = summary
    if "schedule" in st.session_state:
        schedule = st.session_state["schedule"]
        summary = st.session_state["schedule_summary"]
        st.subheader("Generated schedule")
        if schedule.empty:
            st.warning("No staff could be allocated. Check staff availability and requirements.")
        else:
            st.dataframe(schedule, use_container_width=True, hide_index=True)
            st.download_button("Download schedule CSV", schedule.to_csv(index=False),
                               "staff_schedule.csv", "text/csv")
        st.subheader("Demand coverage")
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.metric("Total unfilled positions", int(summary["shortage"].sum()))
        if st.button("Save schedule to database"):
            clear_schedules()
            save_schedules(schedule)
            st.success("Schedule saved.")

elif page == "Data Import & Export":
    st.subheader("Data Import & Export")
    st.write("Upload a CSV file to replace the corresponding demo dataset.")
    uploaded = st.file_uploader("Choose patient or staff CSV", type=["csv"])
    kind = st.selectbox("Dataset type", ["Patient records", "Staff records"])
    if uploaded is not None:
        try:
            incoming = pd.read_csv(uploaded)
            if kind == "Patient records":
                required = {"date","department","patient_count","avg_wait_minutes","peak_hour"}
                if not required.issubset(incoming.columns):
                    st.error(f"Missing columns: {sorted(required - set(incoming.columns))}")
                elif (pd.to_numeric(incoming.patient_count, errors="coerce").isna().any()
                      or (pd.to_numeric(incoming.patient_count, errors="coerce") < 0).any()):
                    st.error("patient_count must contain non-negative numbers.")
                else:
                    st.dataframe(incoming.head(), use_container_width=True)
                    if st.button("Import patient records"):
                        replace_table("patients", incoming)
                        st.success("Patient data imported.")
                        st.rerun()
            else:
                required = {"staff_id","name","role","department","available","max_shifts_per_week"}
                if not required.issubset(incoming.columns):
                    st.error(f"Missing columns: {sorted(required - set(incoming.columns))}")
                else:
                    st.dataframe(incoming.head(), use_container_width=True)
                    if st.button("Import staff records"):
                        replace_table("staff", incoming)
                        st.success("Staff data imported.")
                        st.rerun()
        except Exception as e:
            st.error(f"Could not read CSV: {e}")
    st.download_button("Export patient data", patients.to_csv(index=False), "patient_records.csv", "text/csv")
    st.download_button("Export staff data", staff.to_csv(index=False), "staff_records.csv", "text/csv")
    schedules = read_table("schedules")
    st.download_button("Export saved schedules", schedules.to_csv(index=False), "saved_schedules.csv", "text/csv")
    st.caption("Importing replaces the selected demo table. Keep a backup before replacing data.")

else:
    st.subheader("Project Information")
    st.markdown("""
    **Problem:** Hospitals may face uneven patient arrivals, long waiting times and staff workload imbalance.

    **Proposed solution:** An analytics platform that forecasts patient demand, estimates staffing needs and creates a draft shift allocation.

    **Machine learning:** Random Forest regression using calendar features and department identity.

    **Scheduling:** A transparent greedy allocation algorithm. It is a prototype, not a certified hospital rostering system.

    **Data privacy:** The included records are synthetic. Do not upload identifiable patient health information.
    """)
    st.warning("Predictions are educational estimates, not clinical or operational recommendations. Validate with real hospital experts before real-world use.")
