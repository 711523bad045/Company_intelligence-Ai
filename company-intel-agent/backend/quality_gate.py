"""
Quality Gate Module
Validates and fixes company profile data before export.
Ensures no null/empty critical fields reach frontend.
"""

from typing import Dict, Any


def validate_and_fix(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate company profile and fix issues.
    
    Rejection Rules:
    - short_description is empty
    - industry is "Unknown" or empty
    - sector is empty
    
    Conversion Rules:
    - None → ""
    - [] → ""
    - Ensure all fields exist
    
    Args:
        profile: Company profile dictionary
        
    Returns:
        Fixed profile dictionary or None if rejected
    """
    # Create a copy to avoid mutating original
    fixed = profile.copy()
    
    # Define required schema
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
    
    # Ensure all fields exist
    for key in schema:
        if key not in fixed:
            fixed[key] = schema[key]
    
    # Convert None and [] to empty strings
    for key, value in fixed.items():
        if value is None or value == []:
            fixed[key] = ""
        elif isinstance(value, list):
            # Join list items if it's a list of strings
            fixed[key] = ", ".join(str(v) for v in value if v)
        elif not isinstance(value, str):
            # Convert other types to string
            fixed[key] = str(value)
    
    # Strip whitespace from all string fields
    for key in fixed:
        if isinstance(fixed[key], str):
            fixed[key] = fixed[key].strip()
    
    # REJECTION RULES
    
    # Rule 1: short_description cannot be empty
    if not fixed.get("short_description"):
        print(f"❌ REJECTED {fixed.get('domain', 'unknown')}: No short_description")
        return None
    
    # Rule 2: industry cannot be "Unknown" or empty
    industry = fixed.get("industry", "").lower()
    if not industry or industry == "unknown":
        print(f"❌ REJECTED {fixed.get('domain', 'unknown')}: Industry is '{fixed.get('industry')}'")
        return None
    
    # Rule 3: sector cannot be empty
    if not fixed.get("sector"):
        print(f"❌ REJECTED {fixed.get('domain', 'unknown')}: No sector")
        return None
    
    # Additional quality checks
    
    # Ensure company_name is not empty (use domain as fallback)
    if not fixed.get("company_name"):
        domain = fixed.get("domain", "")
        if domain:
            # Extract company name from domain (e.g., example.com -> Example)
            name = domain.replace("www.", "").split(".")[0]
            fixed["company_name"] = name.capitalize()
        else:
            fixed["company_name"] = "Unknown Company"
    
    # Ensure long_description exists (use short as fallback)
    if not fixed.get("long_description"):
        fixed["long_description"] = fixed.get("short_description", "")
    
    # Validate logo URL format if present
    logo = fixed.get("logo", "")
    if logo and not (logo.startswith("http://") or logo.startswith("https://")):
        # Invalid logo URL, clear it
        fixed["logo"] = ""
    
    # Success
    print(f"✅ VALIDATED {fixed.get('domain', 'unknown')}")
    return fixed


def batch_validate(profiles: list) -> list:
    """
    Validate a batch of profiles.
    
    Args:
        profiles: List of profile dictionaries
        
    Returns:
        List of valid profiles (rejected ones removed)
    """
    valid_profiles = []
    rejected_count = 0
    
    print(f"\n🔍 Running quality gate on {len(profiles)} profiles...")
    
    for profile in profiles:
        validated = validate_and_fix(profile)
        if validated is not None:
            valid_profiles.append(validated)
        else:
            rejected_count += 1
    
    print(f"\n📊 Quality Gate Results:")
    print(f"   ✅ Valid: {len(valid_profiles)}")
    print(f"   ❌ Rejected: {rejected_count}")
    print(f"   📈 Pass rate: {len(valid_profiles)/len(profiles)*100:.1f}%\n")
    
    return valid_profiles


# Test function
if __name__ == "__main__":
    # Test cases
    test_profiles = [
        {
            "domain": "example.com",
            "company_name": "Example Corp",
            "logo": "https://example.com/logo.png",
            "short_description": "We make great software.",
            "long_description": "We make great software for businesses.",
            "sector": "Technology",
            "industry": "Software",
            "sub_industry": "Enterprise Software",
            "sic_code": "7372",
            "sic_text": "Prepackaged Software",
            "tags": "B2B, SaaS"
        },
        {
            "domain": "bad1.com",
            "company_name": "Bad Company",
            "short_description": "",  # Should be rejected
            "industry": "Software",
            "sector": "Technology"
        },
        {
            "domain": "bad2.com",
            "company_name": "Bad Company 2",
            "short_description": "We do stuff",
            "industry": "Unknown",  # Should be rejected
            "sector": "Technology"
        },
        {
            "domain": "bad3.com",
            "company_name": "Bad Company 3",
            "short_description": "We do stuff",
            "industry": "Software",
            "sector": None  # Should be rejected
        },
        {
            "domain": "fixable.com",
            "company_name": None,  # Should be fixed
            "logo": None,  # Should be fixed
            "short_description": "Good description",
            "industry": "Software",
            "sector": "Technology",
            "tags": ["tag1", "tag2"]  # Should be converted
        }
    ]
    
    results = batch_validate(test_profiles)
    
    print("\n📋 Valid profiles:")
    for profile in results:
        print(f"   - {profile['domain']}: {profile['company_name']}")