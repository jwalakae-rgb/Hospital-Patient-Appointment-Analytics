"""
TALHospitals — Phase 2: SQL Analysis
Uses SQLite (built into Python — no installation needed).
All 6 required queries are included and results are printed + saved to reports/.
"""

import sqlite3
import pandas as pd
import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE    = os.path.join(os.path.dirname(os.path.abspath("__file__")), "..", "data")
REPORTS = os.path.join(os.path.dirname(os.path.abspath("__file__")), "..", "reports")
DB_PATH = os.path.join(BASE, "talhospitals.db")

# ── Load cleaned CSVs into SQLite ─────────────────────────────────────────────
conn = sqlite3.connect(DB_PATH)

for fname, table in [("patients_clean.csv",     "patients"),
                     ("doctors_clean.csv",       "doctors"),
                     ("appointments_clean.csv",  "appointments"),
                     ("treatments_clean.csv",    "treatments")]:
    df = pd.read_csv(os.path.join(BASE, fname))
    df.to_sql(table, conn, if_exists="replace", index=False)

print(f"✅ Database created at: {DB_PATH}\n")

# ── Helper to run + display a query ───────────────────────────────────────────
def run_query(title, sql):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    # Save each result as CSV
    safe_name = title.lower().replace(" ", "_").replace("/", "_")
    df.to_csv(os.path.join(REPORTS, f"sql_{safe_name}.csv"), index=False)
    return df

# ── Query 1: Top Visited Departments ─────────────────────────────────────────
run_query("Top Visited Departments", """
    SELECT d.specialization AS Department,
           COUNT(a.appointmentId) AS Total_Appointments
    FROM   appointments a
    JOIN   doctors d ON a.doctorId = d.doctorId
    GROUP  BY d.specialization
    ORDER  BY Total_Appointments DESC;
""")

# ── Query 2: Most Consulted Doctors ──────────────────────────────────────────
run_query("Most Consulted Doctors", """
    SELECT d.name AS Doctor,
           d.specialization,
           COUNT(a.appointmentId) AS Consultations
    FROM   appointments a
    JOIN   doctors d ON a.doctorId = d.doctorId
    WHERE  a.status = 'Completed'
    GROUP  BY a.doctorId
    ORDER  BY Consultations DESC
    LIMIT  10;
""")

# ── Query 3: Appointment Trends by Month ─────────────────────────────────────
run_query("Appointment Trends by Month", """
    SELECT strftime('%Y-%m', appointmentDate) AS Month,
           COUNT(*) AS Total_Appointments,
           SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END) AS Completed,
           SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END) AS Cancelled
    FROM   appointments
    GROUP  BY Month
    ORDER  BY Month;
""")

# ── Query 4: Average Treatment Cost ──────────────────────────────────────────
run_query("Average Treatment Cost by Diagnosis", """
    SELECT diagnosis,
           ROUND(AVG(treatmentCost), 2) AS Avg_Cost,
           COUNT(*) AS Total_Cases
    FROM   treatments
    GROUP  BY diagnosis
    ORDER  BY Avg_Cost DESC;
""")

# ── Query 5: Cancellation Percentage ─────────────────────────────────────────
run_query("Cancellation Percentage", """
    SELECT
        COUNT(*) AS Total_Appointments,
        SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END) AS Cancelled,
        ROUND(
            100.0 * SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END) / COUNT(*),
        2) AS Cancellation_Pct
    FROM appointments;
""")

# ── Query 6: City-wise Patient Distribution ───────────────────────────────────
run_query("City-wise Patient Distribution", """
    SELECT city,
           COUNT(*) AS Total_Patients,
           ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM patients), 2) AS Pct
    FROM   patients
    GROUP  BY city
    ORDER  BY Total_Patients DESC;
""")

conn.close()
print("\n\n✅ All SQL results saved to reports/ folder.")
