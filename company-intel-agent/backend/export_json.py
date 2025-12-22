import pandas as pd
import json
import os

INPUT_EXCEL = "backend/data/output/excel/company_profiles.xlsx"
OUTPUT_JSON = "frontend/public/company_profiles.json"

# Read excel
df = pd.read_excel(INPUT_EXCEL)

# Convert to list of dicts
data = df.fillna("").to_dict(orient="records")

# Ensure folder exists
os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)

# Write JSON
with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print("✅ company_profiles.json created successfully")
