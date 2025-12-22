"""
Business Classifier - 100% OFFLINE
Uses deterministic keyword matching only. NO API calls.
"""

import re
from typing import Dict, Any


CLASSIFICATION_RULES = {
    "Technology": {
        "keywords": ["software", "saas", "cloud", "app", "platform", "tech", "digital", "ai", "ml", "data", "cyber", "it solutions", "computer", "programming", "web", "mobile", "api", "database", "server"],
        "industries": {
            "Software": {
                "keywords": ["software", "saas", "application", "app development", "platform", "program"],
                "sic_code": "7372",
                "sic_text": "Prepackaged Software"
            },
            "IT Services": {
                "keywords": ["consulting", "it services", "managed services", "support", "it consulting"],
                "sic_code": "7371",
                "sic_text": "Computer Programming Services"
            },
            "Cybersecurity": {
                "keywords": ["security", "cyber", "encryption", "firewall", "protection", "antivirus"],
                "sic_code": "7373",
                "sic_text": "Computer Integrated Systems Design"
            },
            "Web Development": {
                "keywords": ["web", "website", "web design", "web development", "frontend", "backend"],
                "sic_code": "7371",
                "sic_text": "Computer Programming Services"
            }
        }
    },
    "Financial Services": {
        "keywords": ["bank", "finance", "investment", "insurance", "trading", "wealth", "credit", "loan", "mortgage", "fintech", "payment", "accounting", "financial"],
        "industries": {
            "Banking": {
                "keywords": ["bank", "savings", "checking", "deposit", "atm"],
                "sic_code": "6020",
                "sic_text": "Commercial Banks"
            },
            "Investment": {
                "keywords": ["investment", "portfolio", "trading", "stocks", "securities", "broker"],
                "sic_code": "6211",
                "sic_text": "Security Brokers & Dealers"
            },
            "Insurance": {
                "keywords": ["insurance", "coverage", "policy", "claims", "underwriting"],
                "sic_code": "6311",
                "sic_text": "Life Insurance"
            },
            "Accounting": {
                "keywords": ["accounting", "bookkeeping", "tax", "audit", "cpa"],
                "sic_code": "8721",
                "sic_text": "Accounting, Auditing & Bookkeeping"
            }
        }
    },
    "Healthcare": {
        "keywords": ["health", "medical", "hospital", "clinic", "patient", "doctor", "nurse", "pharmaceutical", "biotech", "medicine", "care", "wellness", "therapy", "healthcare"],
        "industries": {
            "Healthcare Services": {
                "keywords": ["hospital", "clinic", "patient care", "medical services", "healthcare"],
                "sic_code": "8062",
                "sic_text": "General Medical & Surgical Hospitals"
            },
            "Pharmaceuticals": {
                "keywords": ["pharmaceutical", "drug", "medication", "pharmacy", "prescription"],
                "sic_code": "2834",
                "sic_text": "Pharmaceutical Preparations"
            },
            "Medical Devices": {
                "keywords": ["medical device", "equipment", "diagnostic", "imaging", "surgical"],
                "sic_code": "3841",
                "sic_text": "Surgical & Medical Instruments"
            }
        }
    },
    "Retail": {
        "keywords": ["retail", "store", "shop", "ecommerce", "e-commerce", "marketplace", "buy", "sell", "products", "shopping", "merchant", "sales"],
        "industries": {
            "E-commerce": {
                "keywords": ["ecommerce", "e-commerce", "online store", "marketplace", "shopping", "online shop"],
                "sic_code": "5961",
                "sic_text": "Catalog & Mail-Order Houses"
            },
            "Consumer Goods": {
                "keywords": ["products", "goods", "merchandise", "consumer"],
                "sic_code": "5399",
                "sic_text": "Miscellaneous General Merchandise Stores"
            }
        }
    },
    "Manufacturing": {
        "keywords": ["manufacturing", "production", "factory", "industrial", "machinery", "equipment", "fabrication", "assembly", "manufacture"],
        "industries": {
            "Industrial Manufacturing": {
                "keywords": ["manufacturing", "production", "assembly", "factory"],
                "sic_code": "3569",
                "sic_text": "General Industrial Machinery"
            }
        }
    },
    "Professional Services": {
        "keywords": ["consulting", "advisory", "professional services", "legal", "accounting", "marketing", "advertising", "design", "agency", "recruitment", "consulting firm"],
        "industries": {
            "Consulting": {
                "keywords": ["consulting", "advisory", "strategy", "consultant"],
                "sic_code": "8742",
                "sic_text": "Management Consulting Services"
            },
            "Legal Services": {
                "keywords": ["legal", "law", "attorney", "lawyer", "law firm"],
                "sic_code": "8111",
                "sic_text": "Legal Services"
            },
            "Marketing": {
                "keywords": ["marketing", "advertising", "branding", "agency", "digital marketing"],
                "sic_code": "7311",
                "sic_text": "Advertising Agencies"
            },
            "Design": {
                "keywords": ["design", "graphic", "creative", "branding", "ux", "ui"],
                "sic_code": "7336",
                "sic_text": "Commercial Art & Graphic Design"
            }
        }
    },
    "Education": {
        "keywords": ["education", "school", "university", "training", "learning", "course", "teaching", "e-learning", "academic", "tutor"],
        "industries": {
            "Educational Services": {
                "keywords": ["education", "training", "learning", "school", "university"],
                "sic_code": "8200",
                "sic_text": "Educational Services"
            }
        }
    },
    "Real Estate": {
        "keywords": ["real estate", "property", "housing", "commercial property", "residential", "realtor", "broker"],
        "industries": {
            "Real Estate Services": {
                "keywords": ["real estate", "property management", "realtor", "broker"],
                "sic_code": "6531",
                "sic_text": "Real Estate Agents & Managers"
            }
        }
    },
    "Transportation": {
        "keywords": ["transportation", "logistics", "shipping", "delivery", "freight", "trucking", "transport"],
        "industries": {
            "Logistics": {
                "keywords": ["logistics", "shipping", "freight", "delivery"],
                "sic_code": "4213",
                "sic_text": "Trucking, Except Local"
            }
        }
    },
    "Hospitality": {
        "keywords": ["hotel", "restaurant", "hospitality", "travel", "tourism", "accommodation", "food service"],
        "industries": {
            "Hotels": {
                "keywords": ["hotel", "accommodation", "lodging", "resort"],
                "sic_code": "7011",
                "sic_text": "Hotels & Motels"
            },
            "Restaurants": {
                "keywords": ["restaurant", "dining", "food service", "cafe", "catering"],
                "sic_code": "5812",
                "sic_text": "Eating Places"
            }
        }
    }
}


def normalize_text(text: str) -> str:
    """Normalize text for matching."""
    return text.lower().strip()


def classify_business(text: str) -> Dict[str, Any]:
    """
    Classify business using OFFLINE keyword matching only.
    NO API calls - 100% deterministic.
    
    Args:
        text: Website text
        
    Returns:
        Classification dict with sector, industry, SIC codes
    """
    if not text or len(text) < 20:
        return {
            "sector": "Technology",
            "industry": "Software",
            "sub_industry": "Software",
            "sic_code": "7372",
            "sic_text": "Prepackaged Software",
            "tags": "Technology, Software"
        }
    
    normalized = normalize_text(text)
    
    # Find best matching sector
    sector_scores = {}
    for sector, sector_data in CLASSIFICATION_RULES.items():
        score = sum(1 for kw in sector_data["keywords"] if kw in normalized)
        if score > 0:
            sector_scores[sector] = score
    
    if not sector_scores:
        # Default fallback
        return {
            "sector": "Technology",
            "industry": "Software",
            "sub_industry": "Software",
            "sic_code": "7372",
            "sic_text": "Prepackaged Software",
            "tags": "Technology, Software"
        }
    
    # Best sector
    best_sector = max(sector_scores, key=sector_scores.get)
    sector_data = CLASSIFICATION_RULES[best_sector]
    
    # Find best industry within sector
    industry_scores = {}
    for industry, industry_data in sector_data["industries"].items():
        score = sum(1 for kw in industry_data["keywords"] if kw in normalized)
        if score > 0:
            industry_scores[industry] = score
    
    # Default to first industry if no match
    if industry_scores:
        best_industry = max(industry_scores, key=industry_scores.get)
    else:
        best_industry = list(sector_data["industries"].keys())[0]
    
    industry_data = sector_data["industries"][best_industry]
    
    return {
        "sector": best_sector,
        "industry": best_industry,
        "sub_industry": best_industry,
        "sic_code": industry_data["sic_code"],
        "sic_text": industry_data["sic_text"],
        "tags": f"{best_sector}, {best_industry}"
    }


if __name__ == "__main__":
    test_cases = [
        "We provide cloud software solutions for businesses",
        "Banking and financial services for individuals",
        "Healthcare services and patient care"
    ]
    
    for text in test_cases:
        result = classify_business(text)
        print(f"{text[:40]}... => {result['sector']} > {result['industry']}")