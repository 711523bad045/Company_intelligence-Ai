"""
Pipeline for Processing HTML Dumps - 100% OFFLINE
Processes companies from downloaded HTML files in website_dumps folder.
NO API calls required.
"""

import json
import os
from typing import Dict, Any
from bs4 import BeautifulSoup

# Import our offline modules
from business_classifier import classify_business
from description_generator import generate_descriptions
from quality_gate import validate_and_fix, batch_validate


# Paths
WEBSITE_DUMPS_DIR = "data/input/website_dumps"
CACHE_DIR = "data/cache"
OUTPUT_DIR = "data/output"

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_text_from_html(html_path: str) -> str:
    """Extract clean text from HTML file."""
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        # Remove script, style, nav, footer, header
        for tag in soup(["script", "style", "nav", "footer", "header", "iframe"]):
            tag.decompose()
        
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean whitespace
        text = ' '.join(text.split())
        
        return text
    except Exception as e:
        print(f"⚠️  Error extracting text from {html_path}: {e}")
        return ""


def extract_title_from_html(html_path: str) -> str:
    """Extract title from HTML file."""
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
        
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
            
            # Clean common junk
            for junk in [" | Home", " - Home", " | ", " - ", " – ", "Home - "]:
                if junk in title:
                    title = title.split(junk)[0]
            
            return title.strip()
        
        # Try h1 as fallback
        h1 = soup.find("h1")
        if h1 and h1.text:
            return h1.text.strip()
        
        return ""
    except Exception as e:
        print(f"⚠️  Error extracting title from {html_path}: {e}")
        return ""


def find_logo_from_domain(domain: str) -> str:
    """Generate logo URL using Google's favicon service."""
    return f"https://www.google.com/s2/favicons?sz=128&domain={domain}"


def process_company_html(domain: str, html_path: str) -> Dict[str, Any] | None:
    """
    Process a single company from HTML dump.
    
    Steps:
    1. Extract text from HTML
    2. Extract title
    3. Generate logo URL
    4. Classify business (offline)
    5. Generate descriptions (offline)
    6. Validate quality
    
    Returns:
        Valid profile dict or None if rejected
    """
    print(f"\n{'='*60}")
    print(f"🔧 Processing: {domain}")
    print(f"{'='*60}")
    
    # Step 1: Extract text
    print(f"📄 Extracting text from HTML...")
    text = extract_text_from_html(html_path)
    
    if not text or len(text) < 50:
        print(f"❌ Insufficient text extracted from {domain}")
        return None
    
    print(f"   ✅ Extracted {len(text)} characters")
    
    # Step 2: Extract title
    print(f"📝 Extracting title...")
    title = extract_title_from_html(html_path)
    company_name = title if title else domain.split('.')[0].capitalize()
    
    # Step 3: Generate logo
    print(f"🎨 Generating logo URL...")
    logo_url = find_logo_from_domain(domain)
    
    # Step 4: Classify business
    print(f"🏢 Classifying business...")
    classification = classify_business(text)
    print(f"   ✅ {classification['sector']} > {classification['industry']}")
    
    # Step 5: Generate descriptions
    print(f"📝 Generating descriptions...")
    short_desc, long_desc = generate_descriptions(text)
    print(f"   ✅ Short: {short_desc[:60]}...")
    
    # Build profile
    profile = {
        "domain": domain,
        "company_name": company_name,
        "logo": logo_url,
        "short_description": short_desc,
        "long_description": long_desc,
        "sector": classification.get("sector", ""),
        "industry": classification.get("industry", ""),
        "sub_industry": classification.get("sub_industry", ""),
        "sic_code": classification.get("sic_code", ""),
        "sic_text": classification.get("sic_text", ""),
        "tags": classification.get("tags", "")
    }
    
    # Step 6: Validate
    print(f"🔍 Validating quality...")
    validated = validate_and_fix(profile)
    
    if validated is None:
        print(f"❌ Profile rejected by quality gate")
        return None
    
    print(f"✅ Profile validated successfully")
    return validated


def run_pipeline() -> None:
    """
    Run the full pipeline on all HTML dumps.
    """
    print("\n" + "="*60)
    print("🚀 STARTING HTML DUMP PIPELINE - 100% OFFLINE")
    print("="*60)
    
    # Check if website_dumps directory exists
    if not os.path.exists(WEBSITE_DUMPS_DIR):
        print(f"❌ Website dumps directory not found: {WEBSITE_DUMPS_DIR}")
        print(f"   Please ensure HTML files are in {WEBSITE_DUMPS_DIR}/domain/index.html")
        return
    
    # Get list of company folders
    company_folders = [
        d for d in os.listdir(WEBSITE_DUMPS_DIR)
        if os.path.isdir(os.path.join(WEBSITE_DUMPS_DIR, d))
    ]
    
    if not company_folders:
        print(f"❌ No company folders found in {WEBSITE_DUMPS_DIR}")
        return
    
    print(f"📋 Found {len(company_folders)} companies to process\n")
    
    # Process each company
    results = []
    failed = []
    
    for i, domain in enumerate(company_folders, 1):
        html_path = os.path.join(WEBSITE_DUMPS_DIR, domain, "index.html")
        
        if not os.path.exists(html_path):
            print(f"⚠️  [{i}/{len(company_folders)}] Skipping {domain}: index.html not found")
            failed.append(domain)
            continue
        
        print(f"\n[{i}/{len(company_folders)}] Processing {domain}")
        
        try:
            profile = process_company_html(domain, html_path)
            
            if profile:
                results.append(profile)
                
                # Save individual JSON
                output_json = os.path.join(OUTPUT_DIR, "json", f"{domain}.json")
                os.makedirs(os.path.dirname(output_json), exist_ok=True)
                with open(output_json, 'w', encoding='utf-8') as f:
                    json.dump(profile, f, indent=2, ensure_ascii=False)
            else:
                failed.append(domain)
                
        except Exception as e:
            print(f"❌ Error processing {domain}: {e}")
            import traceback
            traceback.print_exc()
            failed.append(domain)
    
    # Save combined results
    output_file = os.path.join(OUTPUT_DIR, "companies_raw.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Generate report
    print("\n" + "="*60)
    print("📊 PIPELINE COMPLETE")
    print("="*60)
    print(f"✅ Successful: {len(results)}/{len(company_folders)} ({len(results)/len(company_folders)*100:.1f}%)")
    print(f"❌ Failed: {len(failed)}/{len(company_folders)} ({len(failed)/len(company_folders)*100:.1f}%)")
    print(f"💾 Output: {output_file}")
    
    # Field coverage stats
    if results:
        print(f"\n📈 Field Coverage:")
        for field in ["short_description", "sector", "industry", "logo"]:
            count = sum(1 for r in results if r.get(field))
            pct = count / len(results) * 100
            print(f"   {field:20} {count:4}/{len(results):4} ({pct:5.1f}%)")
        
        # Sector distribution
        print(f"\n🏢 Sector Distribution:")
        sectors = {}
        for r in results:
            sector = r.get("sector", "Unknown")
            sectors[sector] = sectors.get(sector, 0) + 1
        
        for sector, count in sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {sector:30} {count:4}")
    
    if failed:
        print(f"\n❌ Failed companies: {', '.join(failed[:10])}")
        if len(failed) > 10:
            print(f"   ... and {len(failed) - 10} more")
        
        # Save failed list
        failed_file = os.path.join(OUTPUT_DIR, "failed_companies.txt")
        with open(failed_file, 'w') as f:
            f.write('\n'.join(failed))
        print(f"   Saved to: {failed_file}")
    
    print("\n✨ Next steps:")
    print("   1. python merge_json.py")
    print("   2. copy data\\output\\companies.json ..\\frontend\\public\\company_profiles.json")


if __name__ == "__main__":
    run_pipeline()