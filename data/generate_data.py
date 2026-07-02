"""
TALHospitals - Synthetic Dataset Generator
Run this script ONCE to create all 4 CSV files in the data/ folder.
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

random.seed(42)
np.random.seed(42)

# ── helpers ──────────────────────────────────────────────────────────────────
def rand_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

CITIES        = ["Chennai", "Coimbatore", "Madurai", "Salem", "Trichy",
                 "Erode", "Tirunelveli", "Vellore", "Thanjavur", "Hosur"]
SPECIALIZATIONS = ["Cardiology", "Neurology", "Orthopedics", "Pediatrics",
                   "Dermatology", "General Medicine", "Gynecology",
                   "Ophthalmology", "ENT", "Oncology"]
DIAGNOSES     = ["Hypertension", "Diabetes", "Fracture", "Fever", "Asthma",
                 "Migraine", "Anemia", "Infection", "Arthritis", "Appendicitis"]
MEDICINES     = ["Paracetamol", "Metformin", "Amlodipine", "Amoxicillin",
                 "Cetirizine", "Omeprazole", "Aspirin", "Ibuprofen"]
STATUSES      = ["Completed", "Cancelled", "Pending", "No-Show"]
CON_TYPES     = ["In-Person", "Online", "Follow-Up"]

# ── 1. Patients ───────────────────────────────────────────────────────────────
n_patients = 500
patients = pd.DataFrame({
    "patientId":        [f"P{str(i).zfill(4)}" for i in range(1, n_patients + 1)],
    "name":             [f"Patient_{i}" for i in range(1, n_patients + 1)],
    "age":              np.random.randint(1, 85, n_patients),
    "gender":           np.random.choice(["Male", "Female"], n_patients),
    "city":             np.random.choice(CITIES, n_patients),
    "registrationDate": [rand_date(datetime(2021, 1, 1), datetime(2024, 12, 31)).strftime("%Y-%m-%d")
                         for _ in range(n_patients)],
})
# Inject duplicates & nulls so cleaning has something to do
patients = pd.concat([patients, patients.sample(20)], ignore_index=True)
patients.loc[random.sample(range(len(patients)), 15), "city"] = None

# ── 2. Doctors ────────────────────────────────────────────────────────────────
n_doctors = 50
doctors = pd.DataFrame({
    "doctorId":        [f"D{str(i).zfill(3)}" for i in range(1, n_doctors + 1)],
    "name":            [f"Dr. Doctor_{i}" for i in range(1, n_doctors + 1)],
    "specialization":  np.random.choice(SPECIALIZATIONS, n_doctors),
    "experience":      np.random.randint(1, 30, n_doctors),
    "availability":    np.random.choice(["Available", "Busy", "On Leave"], n_doctors),
    "consultationFee": np.random.choice([300, 500, 700, 1000, 1500], n_doctors),
})

# ── 3. Appointments ───────────────────────────────────────────────────────────
n_appts = 1000
appointments = pd.DataFrame({
    "appointmentId":   [f"A{str(i).zfill(5)}" for i in range(1, n_appts + 1)],
    "patientId":       np.random.choice(patients["patientId"].unique(), n_appts),
    "doctorId":        np.random.choice(doctors["doctorId"], n_appts),
    "appointmentDate": [rand_date(datetime(2022, 1, 1), datetime(2024, 12, 31)).strftime("%Y-%m-%d")
                        for _ in range(n_appts)],
    "status":          np.random.choice(STATUSES, n_appts, p=[0.6, 0.2, 0.1, 0.1]),
    "consultationType": np.random.choice(CON_TYPES, n_appts),
})
appointments.loc[random.sample(range(n_appts), 20), "consultationType"] = None

# ── 4. Treatments ─────────────────────────────────────────────────────────────
n_treatments = 600
treatments = pd.DataFrame({
    "treatmentId":  [f"T{str(i).zfill(5)}" for i in range(1, n_treatments + 1)],
    "patientId":    np.random.choice(patients["patientId"].unique(), n_treatments),
    "diagnosis":    np.random.choice(DIAGNOSES, n_treatments),
    "medicines":    [", ".join(random.sample(MEDICINES, random.randint(1, 3)))
                     for _ in range(n_treatments)],
    "treatmentCost": np.random.randint(500, 15000, n_treatments),
})

# ── Save ──────────────────────────────────────────────────────────────────────
out = os.path.dirname(os.path.abspath(__file__))
patients.to_csv(os.path.join(out, "patients_raw.csv"),    index=False)
doctors.to_csv(os.path.join(out,  "doctors.csv"),         index=False)
appointments.to_csv(os.path.join(out, "appointments.csv"), index=False)
treatments.to_csv(os.path.join(out,  "treatments.csv"),   index=False)

print("✅  4 CSV files saved in data/")
print(f"   patients_raw.csv  → {len(patients)} rows (includes duplicates & nulls)")
print(f"   doctors.csv       → {len(doctors)} rows")
print(f"   appointments.csv  → {len(appointments)} rows")
print(f"   treatments.csv    → {len(treatments)} rows")
