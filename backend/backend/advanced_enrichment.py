"""
Advanced Company Enrichment using LLM
Extracts: company_type, founded_year, employee_count, headquarters
"""

import json
import re
from typing import Dict, Optional


def enrich_company_metadata(text: str, domain: str, company_name: str) -> Dict:
    """
    Use LLM to extract company metadata that requires inference.
    
    NOTE: Replace this with actual Claude API call in production.
    For now, uses rule-based extraction as fallback.
    
    Returns:
        {
            "company_type": "Private|Public|Startup|Enterprise|SMB|null",
            "founded_year": 2015 or null,
            "employee_count_estimate": "1-10|11-50|51-200|201-500|501+|null",
            "headquarters": "City, Country" or null,
            "confidence": {
                "company_type": 0.0-1.0,
                "founded_year": 0.0-1.0,
                "employee_count": 0.0-1.0
            }
        }
    """
    
    # === RULE-BASED EXTRACTION (Fast fallback) ===
    
    result = {
        "company_type": None,
        "founded_year": None,
        "employee_count_estimate": None,
        "headquarters": None,
        "confidence": {
            "company_type": 0.0,
            "founded_year": 0.0,
            "employee_count": 0.0
        }
    }
    
    # Founded year patterns
    year_patterns = [
        r'founded in (\d{4})',
        r'established in (\d{4})',
        r'since (\d{4})',
        r'est\.?\s*(\d{4})',
        r'©\s*(\d{4})',
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, text.lower())
        if match:
            year = int(match.group(1))
            if 1900 <= year <= 2025:
                result["founded_year"] = year
                result["confidence"]["founded_year"] = 0.8
                break
    
    # Company type indicators
    if any(word in text.lower() for word in ['startup', 'early stage', 'seed funded']):
        result["company_type"] = "Startup"
        result["confidence"]["company_type"] = 0.7
    elif any(word in text.lower() for word in ['publicly traded', 'nasdaq:', 'nyse:']):
        result["company_type"] = "Public"
        result["confidence"]["company_type"] = 0.9
    elif any(word in text.lower() for word in ['enterprise', 'fortune 500', 'global leader']):
        result["company_type"] = "Enterprise"
        result["confidence"]["company_type"] = 0.7
    else:
        result["company_type"] = "Private"
        result["confidence"]["company_type"] = 0.5
    
    # Employee count (very rough heuristics)
    if any(word in text.lower() for word in ['small team', 'boutique', 'family-owned']):
        result["employee_count_estimate"] = "1-10"
        result["confidence"]["employee_count"] = 0.4
    elif 'team of' in text.lower():
        match = re.search(r'team of (\d+)', text.lower())
        if match:
            count = int(match.group(1))
            if count < 10:
                result["employee_count_estimate"] = "1-10"
            elif count < 50:
                result["employee_count_estimate"] = "11-50"
            elif count < 200:
                result["employee_count_estimate"] = "51-200"
            else:
                result["employee_count_estimate"] = "201-500"
            result["confidence"]["employee_count"] = 0.6
    
    # Headquarters (simple extraction from common phrases)
    hq_patterns = [
        r'headquartered in ([A-Za-z\s,]+)',
        r'based in ([A-Za-z\s,]+)',
        r'headquarters:?\s*([A-Za-z\s,]+)',
    ]
    
    for pattern in hq_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["headquarters"] = match.group(1).strip()[:50]
            break
    
    return result


# === PRODUCTION LLM PROMPT (Use with Claude API) ===

LLM_ENRICHMENT_PROMPT = """You are extracting company metadata from website text.

**CRITICAL RULES:**
1. ONLY use information EXPLICITLY stated in the text
2. If unclear or not mentioned, return null
3. DO NOT guess or infer without strong evidence
4. Output ONLY valid JSON, no explanation

**INPUT:**
Domain: {domain}
Company Name: {company_name}
Website Text: {text}

**OUTPUT (JSON only):**
{{
  "company_type": "Startup|Private|Public|Enterprise|SMB|null",
  "founded_year": 2015 or null,
  "employee_count_estimate": "1-10|11-50|51-200|201-500|501-1000|1000+|null",
  "headquarters": "City, Country" or null,
  "confidence": {{
    "company_type": 0.0-1.0,
    "founded_year": 0.0-1.0,
    "employee_count": 0.0-1.0,
    "headquarters": 0.0-1.0
  }}
}}

**RULES:**
- company_type: "Startup" if <5 years old OR explicitly says startup. "Public" if mentions stock/trading. "Enterprise" if mentions Fortune 500/global scale. Otherwise "Private".
- founded_year: ONLY if explicitly stated (e.g., "founded in 2015", "since 2010"). Do NOT infer from domain registration or copyright dates unless clearly stated as founding.
- employee_count_estimate: ONLY if text mentions team size, number of employees, or clear scale indicators. Be conservative.
- headquarters: ONLY if explicitly states "headquartered in", "based in", or location is clearly mentioned as HQ.
- confidence: 1.0 = explicitly stated, 0.8 = clear context, 0.6 = reasonable inference, <0.6 = return null

Extract metadata:"""


def enrich_with_claude_api(text: str, domain: str, company_name: str) -> Dict:
    """
    Call Claude API for metadata extraction.
    
    Replace this function body with actual Anthropic API call:
    
    import anthropic
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        temperature=0,
        messages=[{
            "role": "user",
            "content": LLM_ENRICHMENT_PROMPT.format(
                domain=domain,
                company_name=company_name,
                text=text[:3000]  # Limit context
            )
        }]
    )
    
    json_text = response.content[0].text
    data = json.loads(json_text)
    
    # Filter by confidence
    filtered = {}
    for key, value in data.items():
        if key == "confidence":
            continue
        confidence = data.get("confidence", {}).get(key, 0)
        filtered[key] = value if confidence >= 0.6 else None
    
    return filtered
    """
    
    # Fallback to rule-based for now
    return enrich_company_metadata(text, domain, company_name)