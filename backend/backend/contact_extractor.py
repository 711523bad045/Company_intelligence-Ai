"""
Contact & Social Link Extractor
Direct scraping - NO LLM needed for these fields
"""

import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional


def extract_contact_info(html_path: str, text: str) -> Dict:
    """
    Extract contact information from HTML.
    
    Returns:
        {
            "email": "contact@example.com" or None,
            "phone": "+1-555-0100" or None,
            "address": {
                "full": "123 Main St, City, State 12345" or None,
                "city": None,
                "country": None
            },
            "social_links": {
                "linkedin": "https://linkedin.com/company/..." or None,
                "twitter": "https://twitter.com/..." or None,
                "github": "https://github.com/..." or None,
                "facebook": "https://facebook.com/..." or None
            }
        }
    """
    
    result = {
        "email": None,
        "phone": None,
        "address": {"full": None, "city": None, "country": None},
        "social_links": {
            "linkedin": None,
            "twitter": None,
            "github": None,
            "facebook": None
        }
    }
    
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except:
        return result
    
    # === EMAIL EXTRACTION ===
    # Priority 1: mailto: links
    mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.I))
    if mailto_links:
        email = mailto_links[0]['href'].replace('mailto:', '').split('?')[0]
        result["email"] = email.strip()
    else:
        # Priority 2: email pattern in text (common formats only)
        email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        emails = re.findall(email_pattern, text)
        # Filter out common junk emails
        valid_emails = [e for e in emails if not any(x in e.lower() for x in 
                       ['example.com', 'yoursite', 'domain.com', 'test', 'sample'])]
        if valid_emails:
            result["email"] = valid_emails[0]
    
    # === PHONE EXTRACTION ===
    # Priority 1: tel: links
    tel_links = soup.find_all('a', href=re.compile(r'^tel:', re.I))
    if tel_links:
        phone = tel_links[0]['href'].replace('tel:', '').strip()
        result["phone"] = phone
    else:
        # Priority 2: phone pattern in text
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1-555-123-4567
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',  # (555) 123-4567
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                result["phone"] = phones[0].strip()
                break
    
    # === SOCIAL LINKS ===
    all_links = soup.find_all('a', href=True)
    
    for link in all_links:
        href = link['href'].lower()
        
        if 'linkedin.com/company' in href and not result["social_links"]["linkedin"]:
            result["social_links"]["linkedin"] = link['href']
        elif 'twitter.com' in href and not result["social_links"]["twitter"]:
            result["social_links"]["twitter"] = link['href']
        elif 'github.com' in href and not result["social_links"]["github"]:
            result["social_links"]["github"] = link['href']
        elif 'facebook.com' in href and not result["social_links"]["facebook"]:
            result["social_links"]["facebook"] = link['href']
    
    # === ADDRESS EXTRACTION ===
    # Look for schema.org PostalAddress
    address_schema = soup.find(itemprop="address")
    if address_schema:
        street = address_schema.find(itemprop="streetAddress")
        city = address_schema.find(itemprop="addressLocality")
        country = address_schema.find(itemprop="addressCountry")
        
        if street:
            result["address"]["full"] = street.get_text(strip=True)
        if city:
            result["address"]["city"] = city.get_text(strip=True)
        if country:
            result["address"]["country"] = country.get_text(strip=True)
    else:
        # Fallback: look for address patterns in footer
        footer = soup.find('footer')
        if footer:
            footer_text = footer.get_text(separator=' ', strip=True)
            # Simple heuristic: look for postal code patterns
            postal_pattern = r'\b\d{5}(?:-\d{4})?\b'  # US zip
            if re.search(postal_pattern, footer_text):
                result["address"]["full"] = footer_text[:200]  # First 200 chars
    
    return result


def extract_technologies(html_path: str) -> List[str]:
    """
    Detect technologies from <script> tags and meta tags.
    
    Returns:
        ["React", "WordPress", "Shopify", ...]
    """
    
    tech_signatures = {
        "React": ["react.js", "react.min.js", "_react", "reactdom"],
        "Vue": ["vue.js", "vue.min.js", "vuejs"],
        "Angular": ["angular.js", "angular.min.js", "@angular"],
        "WordPress": ["wp-content", "wp-includes", "wordpress"],
        "Shopify": ["shopify.com", "cdn.shopify"],
        "Wix": ["wix.com", "parastorage"],
        "Squarespace": ["squarespace.com", "sqsp.net"],
        "jQuery": ["jquery.js", "jquery.min.js"],
        "Bootstrap": ["bootstrap.css", "bootstrap.min.css"],
        "Tailwind": ["tailwindcss", "tailwind.min.css"],
        "Google Analytics": ["google-analytics.com", "googletagmanager"],
        "Stripe": ["stripe.com/v3", "js.stripe.com"],
        "Cloudflare": ["cloudflare.com", "cf-ray"],
    }
    
    detected = set()
    
    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()
        
        for tech, signatures in tech_signatures.items():
            if any(sig in content for sig in signatures):
                detected.add(tech)
    except:
        pass
    
    return sorted(list(detected))