"""
TALHospitals — Phase 3: Python Analytics
Generates 5 analysis charts and saves them to dashboard/ folder.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE      = os.path.join(os.path.dirname(os.path.abspath("__file__")), "..", "data")
DASH      = os.path.join(os.path.dirname(os.path.abspath("__file__")), "..", "dashboard")
REPORTS   = os.path.join(os.path.dirname(os.path.abspath("__file__")), "..", "reports")

# ── Load cleaned data ─────────────────────────────────────────────────────────
patients     = pd.read_csv(os.path.join(BASE, "patients_clean.csv"), parse_dates=["registrationDate"])
doctors      = pd.read_csv(os.path.join(BASE, "doctors_clean.csv"))
appointments = pd.read_csv(os.path.join(BASE, "appointments_clean.csv"), parse_dates=["appointmentDate"])
treatments   = pd.read_csv(os.path.join(BASE, "treatments_clean.csv"))

print("✅ Data loaded successfully.\n")

# ── Style ─────────────────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
COLORS = ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#3B1F2B",
          "#44BBA4", "#E94F37", "#393E41", "#F5A623", "#7B68EE"]

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 1 — Patient Growth Trend (monthly)
# ─────────────────────────────────────────────────────────────────────────────
print("📊 Analysis 1: Patient Growth Trend")
monthly_patients = (
    patients.groupby(patients["registrationDate"].dt.to_period("M"))
    .size()
    .reset_index(name="new_patients")
)
monthly_patients["registrationDate"] = monthly_patients["registrationDate"].astype(str)
monthly_patients["cumulative"] = monthly_patients["new_patients"].cumsum()

fig, ax1 = plt.subplots(figsize=(14, 5))
ax2 = ax1.twinx()
ax1.bar(monthly_patients["registrationDate"], monthly_patients["new_patients"],
        color=COLORS[0], alpha=0.6, label="New Patients")
ax2.plot(monthly_patients["registrationDate"], monthly_patients["cumulative"],
         color=COLORS[2], linewidth=2.5, marker="o", markersize=3, label="Cumulative")
ax1.set_xlabel("Month")
ax1.set_ylabel("New Patients", color=COLORS[0])
ax2.set_ylabel("Cumulative Patients", color=COLORS[2])
ax1.set_xticks(range(0, len(monthly_patients), 3))
ax1.set_xticklabels(monthly_patients["registrationDate"].iloc[::3], rotation=45, ha="right")
ax1.set_title("Patient Growth Trend (Monthly)", fontsize=14, fontweight="bold")
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(DASH, "01_patient_growth.png"), dpi=150)
plt.close()
print("   Saved: 01_patient_growth.png")

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 2 — Seasonal Disease Patterns
# ─────────────────────────────────────────────────────────────────────────────
print("📊 Analysis 2: Seasonal Disease Patterns")
appointments["month"] = appointments["appointmentDate"].dt.month
appointments["month_name"] = appointments["appointmentDate"].dt.strftime("%b")
appt_merged = appointments.merge(doctors[["doctorId", "specialization"]], on="doctorId")

monthly_dept = (
    appt_merged[appt_merged["status"] == "Completed"]
    .groupby(["month", "month_name", "specialization"])
    .size()
    .reset_index(name="count")
)

# Top 5 departments
top5_dept = (monthly_dept.groupby("specialization")["count"].sum()
             .nlargest(5).index.tolist())
pivot = (monthly_dept[monthly_dept["specialization"].isin(top5_dept)]
         .pivot_table(index="month", columns="specialization", values="count", aggfunc="sum")
         .fillna(0))

fig, ax = plt.subplots(figsize=(14, 6))
for i, col in enumerate(pivot.columns):
    ax.plot(pivot.index, pivot[col], marker="o", linewidth=2, color=COLORS[i], label=col)
ax.set_xticks(range(1, 13))
ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"])
ax.set_xlabel("Month")
ax.set_ylabel("Completed Appointments")
ax.set_title("Seasonal Disease Patterns — Top 5 Departments", fontsize=14, fontweight="bold")
ax.legend(loc="upper right")
plt.tight_layout()
plt.savefig(os.path.join(DASH, "02_seasonal_patterns.png"), dpi=150)
plt.close()
print("   Saved: 02_seasonal_patterns.png")

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 3 — Doctor Workload Analysis
# ─────────────────────────────────────────────────────────────────────────────
print("📊 Analysis 3: Doctor Workload Analysis")
workload = (
    appointments[appointments["status"] == "Completed"]
    .groupby("doctorId")
    .size()
    .reset_index(name="completed")
    .merge(doctors[["doctorId", "name", "specialization"]], on="doctorId")
    .sort_values("completed", ascending=False)
    .head(15)
)

fig, ax = plt.subplots(figsize=(12, 7))
bars = ax.barh(workload["name"], workload["completed"],
               color=[COLORS[i % len(COLORS)] for i in range(len(workload))])
for bar, val in zip(bars, workload["completed"]):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
            str(val), va="center", fontsize=9)
ax.set_xlabel("Completed Appointments")
ax.set_title("Top 15 Doctors by Workload", fontsize=14, fontweight="bold")
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(os.path.join(DASH, "03_doctor_workload.png"), dpi=150)
plt.close()
print("   Saved: 03_doctor_workload.png")

# Save workload report
workload_report = workload[["name","specialization","completed"]].rename(
    columns={"name":"Doctor","specialization":"Specialization","completed":"Completed_Appointments"})
workload_report.to_csv(os.path.join(REPORTS, "doctor_workload.csv"), index=False)

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 4 — Revenue Estimation
# ─────────────────────────────────────────────────────────────────────────────
print("📊 Analysis 4: Revenue Estimation")
appt_with_fee = (
    appointments[appointments["status"] == "Completed"]
    .merge(doctors[["doctorId", "consultationFee"]], on="doctorId")
)
appt_with_fee["month"] = appt_with_fee["appointmentDate"].dt.to_period("M").astype(str)
monthly_rev = appt_with_fee.groupby("month")["consultationFee"].sum()
treatment_rev = treatments.groupby(
    treatments["patientId"].apply(lambda x: x)  # placeholder; no date in treatments
)["treatmentCost"].sum().sum() / 36  # approximate monthly avg over 3 years
monthly_total = monthly_rev.copy()
# add flat treatment revenue per month
monthly_total = monthly_total + (treatments["treatmentCost"].sum() / len(monthly_total))

fig, ax = plt.subplots(figsize=(14, 5))
monthly_rev.plot(kind="bar", ax=ax, color=COLORS[0], alpha=0.8, label="Consultation Fees")
monthly_total.plot(kind="line", ax=ax, color=COLORS[2], linewidth=2.5,
                   marker="o", markersize=3, label="Total Revenue (incl. Treatments)")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (₹)")
ax.set_title("Monthly Revenue Estimation", fontsize=14, fontweight="bold")
ax.set_xticklabels(monthly_rev.index, rotation=45, ha="right", fontsize=7)
ax.legend()
plt.tight_layout()
plt.savefig(os.path.join(DASH, "04_revenue_trend.png"), dpi=150)
plt.close()

total_consult  = appt_with_fee["consultationFee"].sum()
total_treatment = treatments["treatmentCost"].sum()
print(f"   Consultation Revenue : ₹{total_consult:,.0f}")
print(f"   Treatment Revenue    : ₹{total_treatment:,.0f}")
print(f"   TOTAL REVENUE        : ₹{total_consult + total_treatment:,.0f}")
print("   Saved: 04_revenue_trend.png")

# ─────────────────────────────────────────────────────────────────────────────
# ANALYSIS 5 — Appointment Success Ratio (pie + bar)
# ─────────────────────────────────────────────────────────────────────────────
print("📊 Analysis 5: Appointment Success Ratio")
status_counts = appointments["status"].value_counts()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Pie chart
axes[0].pie(status_counts, labels=status_counts.index, autopct="%1.1f%%",
            colors=COLORS[:len(status_counts)], startangle=140,
            wedgeprops=dict(edgecolor="white", linewidth=1.5))
axes[0].set_title("Appointment Status Distribution", fontsize=13, fontweight="bold")

# Bar chart by department
dept_status = (
    appt_merged.groupby(["specialization", "status"])
    .size().unstack(fill_value=0)
)
dept_status.plot(kind="bar", ax=axes[1], color=COLORS[:dept_status.shape[1]], edgecolor="white")
axes[1].set_title("Status by Department", fontsize=13, fontweight="bold")
axes[1].set_xlabel("Department")
axes[1].set_ylabel("Appointments")
axes[1].set_xticklabels(dept_status.index, rotation=45, ha="right")
axes[1].legend(title="Status", bbox_to_anchor=(1.02, 1), loc="upper left")

plt.tight_layout()
plt.savefig(os.path.join(DASH, "05_appointment_success.png"), dpi=150, bbox_inches="tight")
plt.close()

success_rate = status_counts.get("Completed", 0) / status_counts.sum() * 100
cancel_rate  = status_counts.get("Cancelled", 0) / status_counts.sum() * 100
print(f"   Success Rate     : {success_rate:.1f}%")
print(f"   Cancellation Rate: {cancel_rate:.1f}%")
print("   Saved: 05_appointment_success.png")

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY STATS → reports/
# ─────────────────────────────────────────────────────────────────────────────
summary = {
    "Total Patients":             len(patients),
    "Total Doctors":              len(doctors),
    "Total Appointments":         len(appointments),
    "Total Treatments":           len(treatments),
    "Completed Appointments":     int(status_counts.get("Completed", 0)),
    "Cancelled Appointments":     int(status_counts.get("Cancelled", 0)),
    "Success Rate (%)":           round(success_rate, 2),
    "Cancellation Rate (%)":      round(cancel_rate, 2),
    "Total Consultation Revenue": int(total_consult),
    "Total Treatment Revenue":    int(total_treatment),
    "Grand Total Revenue":        int(total_consult + total_treatment),
}

summary_df = pd.DataFrame(list(summary.items()), columns=["Metric", "Value"])
summary_df.to_csv(os.path.join(REPORTS, "summary_stats.csv"), index=False)

print("\n" + "="*50)
print("  📋 KEY METRICS SUMMARY")
print("="*50)
for k, v in summary.items():
    print(f"  {k:<35}: {v:>15,}" if isinstance(v, int) else f"  {k:<35}: {v:>15}")

print(f"\n✅ All 5 charts saved to dashboard/")
print(f"✅ Summary saved to reports/summary_stats.csv")
