import os
import time
import pandas as pd
import requests

INPUT_CSV = "data/input/Topic1_Input_Records.csv"
OUTPUT_DIR = "data/input/website_dumps"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(INPUT_CSV)

for i, row in df.iterrows():
    domain = row["domain"].strip()
    folder_path = os.path.join(OUTPUT_DIR, domain)
    html_path = os.path.join(folder_path, "index.html")

    # Skip if already downloaded
    if os.path.exists(html_path):
        continue

    os.makedirs(folder_path, exist_ok=True)

    url = f"https://{domain}"

    try:
        print(f"🌐 Downloading {url}")
        response = requests.get(url, headers=HEADERS, timeout=15)

        if response.status_code == 200:
            with open(html_path, "w", encoding="utf-8", errors="ignore") as f:
                f.write(response.text)
        else:
            print(f"⚠️ Skipped {domain} (status {response.status_code})")

    except Exception as e:
        print(f"❌ Failed {domain}: {e}")

    time.sleep(1)  # polite delay (VERY IMPORTANT)

print("✅ Website download completed")
