# %% [markdown]
# # TALHospitals — Phase 1: Data Cleaning
# **Goal:** Remove duplicates, standardize dates, handle nulls, normalize departments.

# %%
import pandas as pd
import numpy as np
import os

# Load raw data (adjust path if needed)
BASE = os.path.join(os.path.dirname(os.path.abspath("__file__")), "..", "data")

patients_raw = pd.read_csv(os.path.join(BASE, "patients_raw.csv"))
doctors      = pd.read_csv(os.path.join(BASE, "doctors.csv"))
appointments = pd.read_csv(os.path.join(BASE, "appointments.csv"))
treatments   = pd.read_csv(os.path.join(BASE, "treatments.csv"))

print("=== RAW SHAPES ===")
print(f"Patients    : {patients_raw.shape}")
print(f"Doctors     : {doctors.shape}")
print(f"Appointments: {appointments.shape}")
print(f"Treatments  : {treatments.shape}")

# %% [markdown]
# ## 1. Remove Duplicate Patients

# %%
print(f"\nDuplicates before: {patients_raw.duplicated(subset='patientId').sum()}")
patients = patients_raw.drop_duplicates(subset="patientId").reset_index(drop=True)
print(f"Rows after removing duplicates: {len(patients)}")

# %% [markdown]
# ## 2. Standardize Dates

# %%
for df, col in [(patients, "registrationDate"),
                (appointments, "appointmentDate")]:
    df[col] = pd.to_datetime(df[col], errors="coerce")

print("Date columns converted to datetime ✅")
print(patients["registrationDate"].dtype)
print(appointments["appointmentDate"].dtype)

# %% [markdown]
# ## 3. Handle Null / Missing Values

# %%
print("\n=== NULL COUNTS BEFORE CLEANING ===")
print(patients.isnull().sum())
print(appointments.isnull().sum())

# Fill nulls
patients["city"]                    = patients["city"].fillna("Unknown")
appointments["consultationType"]    = appointments["consultationType"].fillna("In-Person")

print("\n=== NULL COUNTS AFTER CLEANING ===")
print(patients.isnull().sum())
print(appointments.isnull().sum())

# %% [markdown]
# ## 4. Normalize Department / Specialization Names

# %%
doctors["specialization"] = (
    doctors["specialization"]
    .str.strip()
    .str.title()
)

print("\nUnique specializations after normalization:")
print(doctors["specialization"].unique())

# %% [markdown]
# ## 5. Extra Cleaning — Fix Data Types & Ranges

# %%
# Remove patients with unrealistic ages
patients = patients[(patients["age"] >= 0) & (patients["age"] <= 120)]

# Ensure consultationFee and treatmentCost are numeric
doctors["consultationFee"]     = pd.to_numeric(doctors["consultationFee"],     errors="coerce").fillna(0)
treatments["treatmentCost"]    = pd.to_numeric(treatments["treatmentCost"],    errors="coerce").fillna(0)

print("\nData types after fixing:")
print(doctors[["consultationFee"]].dtypes)
print(treatments[["treatmentCost"]].dtypes)

# %% [markdown]
# ## 6. Save Cleaned Data

# %%
patients.to_csv(os.path.join(BASE, "patients_clean.csv"),    index=False)
doctors.to_csv(os.path.join(BASE,  "doctors_clean.csv"),     index=False)
appointments.to_csv(os.path.join(BASE, "appointments_clean.csv"), index=False)
treatments.to_csv(os.path.join(BASE,  "treatments_clean.csv"),    index=False)

print("\n✅ Cleaned files saved:")
print(f"  patients_clean.csv    → {len(patients)} rows")
print(f"  doctors_clean.csv     → {len(doctors)} rows")
print(f"  appointments_clean.csv→ {len(appointments)} rows")
print(f"  treatments_clean.csv  → {len(treatments)} rows")
