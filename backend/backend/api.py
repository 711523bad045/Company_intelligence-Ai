"""
FastAPI endpoints for Company Intelligence
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import os

app = FastAPI(title="Company Intelligence API")

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === DATA LOADING ===

COMPANIES_FILE = "data/output/companies_raw.json"
companies_cache = {}

def load_companies():
    """Load companies from JSON file into memory."""
    global companies_cache
    
    if not os.path.exists(COMPANIES_FILE):
        return
    
    with open(COMPANIES_FILE, 'r', encoding='utf-8') as f:
        companies = json.load(f)
    
    # Index by domain for O(1) lookup
    for company in companies:
        domain = company.get("domain")
        if domain:
            companies_cache[domain] = company

# Load on startup
load_companies()


# === RESPONSE MODELS ===

class Address(BaseModel):
    full: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

class SocialLinks(BaseModel):
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    github: Optional[str] = None
    facebook: Optional[str] = None

class CompanyDetail(BaseModel):
    domain: str
    company_name: str
    logo: Optional[str] = None
    
    # Business info
    sector: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    company_type: Optional[str] = None
    
    # Descriptions
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    tags: Optional[str] = None
    
    # Contact
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Address] = None
    
    # Metadata
    founded_year: Optional[int] = None
    employee_count_estimate: Optional[str] = None
    headquarters: Optional[str] = None
    
    # Social & Tech
    social_links: Optional[SocialLinks] = None
    technologies: Optional[List[str]] = None
    
    # Quality
    confidence_scores: Optional[Dict[str, float]] = None
    last_updated: Optional[str] = None


# === ENDPOINTS ===

@app.get("/")
def root():
    return {
        "service": "Company Intelligence API",
        "version": "1.0",
        "companies_loaded": len(companies_cache)
    }

@app.get("/api/companies")
def list_companies():
    """
    List all companies (basic info only).
    For the table view.
    """
    companies = [
        {
            "domain":c["domain"],
            "company_name": c["company_name"],
            "logo": c.get("logo"),
            "sector": c.get("sector"),
            "short_description": c.get("short_description")
        }
        for c in companies_cache.values()
    ]
    return {"companies": companies, "total": len(companies)}


@app.get("/api/company/{domain}", response_model=CompanyDetail)
def get_company_details(domain: str):
    """
    Get full company details for the detail view.
    This is called when user clicks "View Details".
    """
    
    # Normalize domain (remove www, https, etc.)
    domain = domain.replace("https://", "").replace("http://", "").replace("www.", "")
    
    if domain not in companies_cache:
        raise HTTPException(status_code=404, detail=f"Company not found: {domain}")
    
    company = companies_cache[domain]
    
    # Transform to response model
    return CompanyDetail(
        domain=company["domain"],
        company_name=company["company_name"],
        logo=company.get("logo"),
        sector=company.get("sector"),
        industry=company.get("industry"),
        sub_industry=company.get("sub_industry"),
        company_type=company.get("company_type"),
        short_description=company.get("short_description"),
        long_description=company.get("long_description"),
        tags=company.get("tags"),
        email=company.get("email"),
        phone=company.get("phone"),
        address=company.get("address"),
        founded_year=company.get("founded_year"),
        employee_count_estimate=company.get("employee_count_estimate"),
        headquarters=company.get("headquarters"),
        social_links=company.get("social_links"),
        technologies=company.get("technologies"),
        confidence_scores=company.get("confidence_scores"),
        last_updated=company.get("last_updated")
    )


@app.post("/api/company/{domain}/refresh")
def refresh_company(domain: str):
    """
    Trigger re-processing of a company.
    For future use - returns 202 Accepted.
    """
    return {
        "status": "not_implemented",
        "message": "Re-scraping not available in current version"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)