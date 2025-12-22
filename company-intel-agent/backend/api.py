from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

DATA_DIR = "backend/data/output/json"

@app.route("/companies")
def get_companies():
    companies = []
    for file in os.listdir(DATA_DIR):
        if file.endswith(".json"):
            with open(os.path.join(DATA_DIR, file), "r", encoding="utf-8") as f:
                companies.append(json.load(f))
    return jsonify(companies)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
