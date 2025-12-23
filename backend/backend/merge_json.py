"""
JSON Merger - Creates Frontend-Safe companies.json
Enforces final schema, converts null/[] to empty strings.
"""

import json
import os
from typing import Dict, Any, List


# Paths
INPUT_FILE = "data/output/companies_raw.json"
OUTPUT_FILE = "data/output/companies.json"


def enforce_schema(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enforce final schema and ensure frontend-safe values.
    
    Final Schema:
    - domain: string
    - company_name: string
    - logo: string
    - short_description: string
    - long_description: string
    - sector: string
    - industry: string
    - sub_industry: string
    - sic_code: string
    - sic_text: string
    - tags: string
    
    All fields must be strings, never null or arrays.
    """
    # Define expected schema
    schema = {
        "domain": "",
        "company_name": "",
        "logo": "",
        "short_description": "",
        "long_description": "",
        "sector": "",
        "industry": "",
        "sub_industry": "",
        "sic_code": "",
        "sic_text": "",
        "tags": ""
    }
    
    # Start with schema defaults
    clean_profile = schema.copy()
    
    # Fill in values from profile
    for key in schema.keys():
        if key in profile:
            value = profile[key]
            
            # Convert None to empty string
            if value is None:
                clean_profile[key] = ""
            
            # Convert list to comma-separated string
            elif isinstance(value, list):
                if value:  # Non-empty list
                    clean_profile[key] = ", ".join(str(v) for v in value if v)
                else:
                    clean_profile[key] = ""
            
            # Convert other types to string
            elif not isinstance(value, str):
                clean_profile[key] = str(value)
            
            # String value
            else:
                clean_profile[key] = value.strip()
        
        # Key missing from profile, use default empty string
        else:
            clean_profile[key] = ""
    
    return clean_profile


def merge_json() -> None:
    """
    Merge and clean company profiles for frontend consumption.
    
    Process:
    1. Load companies_raw.json
    2. Enforce schema on each profile
    3. Remove duplicates by domain
    4. Sort by company name
    5. Save to companies.json
    """
    print("\n" + "="*60)
    print("🔧 MERGING JSON FOR FRONTEND")
    print("="*60)
    
    # Check input file exists
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
        print("   Run pipeline_fast.py first!")
        return
    
    # Load raw data
    print(f"📖 Loading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        raw_profiles = json.load(f)
    
    print(f"   Found {len(raw_profiles)} profiles")
    
    # Enforce schema and deduplicate
    print("🔧 Enforcing schema and cleaning data...")
    
    clean_profiles = []
    seen_domains = set()
    duplicates = 0
    
    for profile in raw_profiles:
        # Enforce schema
        clean = enforce_schema(profile)
        
        # Check for duplicates
        domain = clean["domain"]
        if domain in seen_domains:
            print(f"   ⚠️  Duplicate domain: {domain}")
            duplicates += 1
            continue
        
        seen_domains.add(domain)
        clean_profiles.append(clean)
    
    # Sort by company name
    print("📊 Sorting by company name...")
    clean_profiles.sort(key=lambda x: x["company_name"].lower())
    
    # Save final output
    print(f"💾 Saving to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(clean_profiles, f, indent=2, ensure_ascii=False)
    
    # Generate statistics
    print("\n" + "="*60)
    print("📊 MERGE COMPLETE")
    print("="*60)
    print(f"✅ Total profiles: {len(clean_profiles)}")
    print(f"⚠️  Duplicates removed: {duplicates}")
    print(f"💾 Output file: {OUTPUT_FILE}")
    
    # Field statistics
    print("\n📈 Field Coverage:")
    field_counts = {field: 0 for field in ["logo", "short_description", "long_description", "sector", "industry"]}
    
    for profile in clean_profiles:
        for field in field_counts:
            if profile.get(field):
                field_counts[field] += 1
    
    for field, count in field_counts.items():
        percentage = (count / len(clean_profiles) * 100) if clean_profiles else 0
        print(f"   {field}: {count}/{len(clean_profiles)} ({percentage:.1f}%)")
    
    # Sector distribution
    print("\n🏢 Sector Distribution:")
    sector_counts = {}
    for profile in clean_profiles:
        sector = profile.get("sector", "Unknown")
        sector_counts[sector] = sector_counts.get(sector, 0) + 1
    
    for sector, count in sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {sector}: {count}")
    
    print("\n✨ Next step: Copy to frontend")
    print(f"   copy backend\\data\\output\\companies.json frontend\\public\\company_profiles.json")


if __name__ == "__main__":
    merge_json()