# Company Intelligence Agent

## Abstract

Company Intelligence Agent is an end-to-end AI-powered data extraction and intelligence system designed to automatically collect, process, structure, and visualize company information from real-world websites.

The system takes a list of company domains as input, visits each website, extracts meaningful content, processes it using a local Large Language Model (LLM), and produces structured company intelligence in JSON format. The final output is displayed in a clean, fast, and simple React-based dashboard.

This project demonstrates real-world skills in data engineering, backend pipeline design, LLM integration, web scraping, data processing, and frontend visualization.

---

## Table of Contents

- Introduction  
- Problem Statement  
- Objectives  
- System Architecture  
- Technology Stack  
- Project Structure  
- Detailed Backend Workflow  
- Detailed Frontend Workflow  
- Data Pipeline Explanation  
- LLM Prompt Engineering Strategy  
- Error Handling and Real-World Constraints  
- Performance and Scalability Considerations  
- Results and Output  
- How to Run the Project  
- Screenshots  
- Resume Description  
- Future Improvements  
- Author  

---

## Introduction

In many business, research, and consulting environments, collecting company intelligence is a slow and manual process. Analysts typically visit company websites, read content, and manually summarize the information.

This project automates the entire process using a modern AI-driven pipeline.

The system:
- Visits company websites automatically
- Extracts meaningful text from HTML
- Uses a local LLM to convert unstructured text into structured business intelligence
- Stores the results in machine-readable JSON format
- Displays the output in a user-friendly web dashboard

---

## Problem Statement

Design and implement a system that:

- Accepts 100–150 company domains
- Automatically visits and downloads each website
- Extracts company-related information
- Converts unstructured website text into structured company intelligence
- Stores the results in JSON format
- Displays the results in a simple React-based UI

---

## Objectives

- Build a fully automated data pipeline
- Handle real-world website failures gracefully
- Use a local LLM for cost-free and private inference
- Produce structured, machine-readable company profiles
- Provide a simple visualization layer for browsing and searching results
- Follow modular and scalable software architecture principles

---

## System Architecture

CSV (Domains)
↓
Website Downloader
↓
HTML Parser
↓
Clean Text
↓
LLM (Ollama)
↓
Structured JSON
↓
JSON Merger
↓
React Dashboard

yaml
Copy code

---

## Technology Stack

### Backend
- Python
- Requests, BeautifulSoup
- Ollama (Local LLM)
- JSON, CSV processing

### Frontend
- React
- Vite
- JavaScript

### Tools
- Git, GitHub
- Postman (for API testing if extended)
- VS Code

---

## Project Structure

company-intel-agent/
│
├── backend/
│ ├── pipeline.py
│ ├── download_websites.py
│ ├── merge_json.py
│ ├── llm/
│ │ └── company_extractor.py
│ ├── parsers/
│ │ └── html_parser.py
│ └── data/
│ ├── input/
│ │ ├── Topic1_Input_Records.csv
│ │ └── website_dumps/
│ └── output/
│ ├── json/
│ └── excel/
│
├── frontend/
│ ├── public/
│ │ └── company_profiles.json
│ └── src/
│ └── App.jsx
│
└── venv/

yaml
Copy code

---

## Detailed Backend Workflow

### Step 1: Input Data

The system starts with a CSV file containing company domains:

backend/data/input/Topic1_Input_Records.csv

yaml
Copy code

---

### Step 2: Website Downloading

Run:

```bash
python backend/download_websites.py
This script:

Visits each domain

Downloads the homepage HTML

Saves it to:

pgsql
Copy code
backend/data/input/website_dumps/<domain>/index.html
Result:

108 websites successfully downloaded

Some failed due to:

SSL errors

Bot blocking

Redirect loops

Empty pages

Step 3: HTML to Clean Text
File:

bash
Copy code
backend/parsers/html_parser.py
Responsibilities:

Remove script, style, and irrelevant tags

Extract visible text

Normalize and clean text for LLM input

Step 4: LLM-Based Information Extraction
File:

bash
Copy code
backend/llm/company_extractor.py
Uses Ollama local LLM

Uses a strictly structured prompt

Forces JSON-only output

Extracted Schema:

json
Copy code
{
  "company_name": "",
  "industry": "",
  "sub_industry": "",
  "products_or_services": [],
  "locations": [],
  "key_people": [],
  "short_description": "",
  "long_description": ""
}
Step 5: Pipeline Orchestration
Run:

bash
Copy code
python backend/pipeline.py
This script:

Iterates over all domains

Finds available HTML dumps

Parses text

Calls LLM extractor

Saves output to:

pgsql
Copy code
backend/data/output/json/<domain>.json
Result:

67 high-quality company profiles generated

Step 6: JSON Merge for Frontend
Run:

bash
Copy code
python backend/merge_json.py
This script:

Merges all individual JSON files into:

pgsql
Copy code
frontend/public/company_profiles.json
Frontend Workflow
Setup
bash
Copy code
cd frontend
npm install
npm run dev
Open:

arduino
Copy code
http://localhost:5173
Data Loading
The frontend loads:

js
Copy code
fetch("/company_profiles.json")
UI Features
Company list

Industry and domain display

Search functionality

Total companies counter

Simple and fast UI

Error Handling and Real-World Constraints
Website blocking is handled by skipping failed domains

Empty or JS-heavy sites are ignored

LLM failures are caught and logged

The pipeline continues even if some entries fail

Performance and Scalability
Modular architecture allows:

Parallel downloading

Parallel LLM processing

JSON-based storage allows easy migration to databases later

Frontend loads pre-merged static JSON for fast performance

Results and Output
Input domains processed: ~150

Websites downloaded: 108

Valid structured profiles generated: 67
<img width="1918" height="949" alt="Screenshot 2026-01-13 063754" src="https://github.com/user-attachments/assets/90fecb45-f252-4203-a60f-5cca292ac95d" />


### Dashboard View
<img width="1906" height="958" alt="Screenshot 2026-01-13 063743" src="https://github.com/user-attachments/assets/33c85cde-b044-4da5-bb3e-5714483cc03a" />


### Search Functionality
<img width="1890" height="381" alt="Screenshot 2026-01-13 063827" src="https://github.com/user-attachments/assets/67272b22-8a01-4fd5-9b59-8b2fcd9714db" />



Future Improvements
Add async and parallel processing

Store results in a database (PostgreSQL / MongoDB)

Add advanced filtering and analytics in UI

Add API layer for real-time queries

Support more document types (PDF, DOC, etc.)

Author
Rajesh N
B.Tech Artificial Intelligence and Data Science

