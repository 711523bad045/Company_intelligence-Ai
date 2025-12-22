"""
Robust logo extraction with multiple fallback strategies.
Guarantees a valid logo URL is ALWAYS returned.
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Timeout for favicon checks
TIMEOUT = 3


def extract_logo(domain: str, html_path: str) -> str:
    """
    Multi-tier logo resolution:
    1. Parse HTML for <link rel="icon"> variants
    2. Try common favicon paths (/favicon.ico, /favicon.png)
    3. Use Clearbit logo API (high quality)
    4. Fallback to Google favicon service (guaranteed)
    
    Returns: Valid logo URL (never empty)
    """
    
    # Tier 1: Parse HTML
    logo = _extract_from_html(domain, html_path)
    if logo and _is_valid_url(logo):
        return logo
    
    # Tier 2: Common paths
    logo = _try_common_paths(domain)
    if logo:
        return logo
    
    # Tier 3: Clearbit API (best quality, but rate limited)
    logo = _try_clearbit(domain)
    if logo:
        return logo
    
    # Tier 4: Google favicon (guaranteed fallback)
    return _google_favicon(domain)


def _extract_from_html(domain: str, html_path: str) -> str:
    """
    Parse HTML for favicon references.
    Checks multiple <link> tag variations.
    """
    try:
        if not os.path.exists(html_path):
            return ""
        
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")
        
        # Priority order for <link> tags
        selectors = [
            {"rel": "apple-touch-icon"},  # High-res iOS icons
            {"rel": "icon", "sizes": "192x192"},  # High-res favicon
            {"rel": "icon", "type": "image/png"},
            {"rel": "shortcut icon"},
            {"rel": "icon"}
        ]
        
        for selector in selectors:
            icon = soup.find("link", selector)
            if icon and icon.get("href"):
                href = icon["href"]
                
                # Handle relative URLs
                if href.startswith("//"):
                    href = "https:" + href
                elif href.startswith("/"):
                    href = f"https://{domain}{href}"
                elif not href.startswith("http"):
                    href = urljoin(f"https://{domain}", href)
                
                # Validate it's an image
                if _looks_like_image(href):
                    return href
        
        # Check for <meta property="og:image"> (often high quality)
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]
        
    except Exception as e:
        print(f"⚠️ HTML parsing error for {domain}: {e}")
    
    return ""


def _try_common_paths(domain: str) -> str:
    """
    Try standard favicon locations.
    Tests if URLs are accessible before returning.
    """
    common_paths = [
        f"https://{domain}/favicon.ico",
        f"https://{domain}/favicon.png",
        f"https://{domain}/apple-touch-icon.png",
        f"https://{domain}/assets/favicon.ico",
        f"https://{domain}/static/favicon.ico",
    ]
    
    for url in common_paths:
        if _url_exists(url):
            return url
    
    return ""


def _try_clearbit(domain: str) -> str:
    """
    Clearbit Logo API - provides high-quality company logos.
    Free tier: 100 requests/month, no API key needed.
    
    Returns: Logo URL if available, else empty string
    """
    try:
        # Extract root domain (remove subdomains)
        clean_domain = _get_root_domain(domain)
        
        url = f"https://logo.clearbit.com/{clean_domain}"
        
        # Quick HEAD request to check if logo exists
        response = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
        
        if response.status_code == 200:
            return url
            
    except Exception:
        pass
    
    return ""


def _google_favicon(domain: str, size: int = 128) -> str:
    """
    Google favicon service - guaranteed fallback.
    Always returns an image (uses generic icon if favicon not found).
    
    Args:
        domain: Domain name
        size: Icon size (16, 32, 64, 128, 256)
    
    Returns: Valid Google favicon URL
    """
    clean_domain = _get_root_domain(domain)
    return f"https://www.google.com/s2/favicons?sz={size}&domain={clean_domain}"


def _is_valid_url(url: str) -> bool:
    """Check if string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def _looks_like_image(url: str) -> bool:
    """Quick heuristic check if URL is likely an image."""
    image_extensions = ['.ico', '.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp']
    url_lower = url.lower()
    return any(ext in url_lower for ext in image_extensions)


def _url_exists(url: str) -> bool:
    """
    Check if URL is accessible (returns 200).
    Uses HEAD request for efficiency.
    """
    try:
        response = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
        return response.status_code == 200
    except Exception:
        return False


def _get_root_domain(domain: str) -> str:
    """
    Extract root domain from subdomains.
    Examples:
        www.example.com -> example.com
        api.app.example.com -> example.com
        example.co.uk -> example.co.uk
    """
    # Remove protocol if present
    domain = domain.replace("https://", "").replace("http://", "")
    
    # Remove path if present
    domain = domain.split("/")[0]
    
    # Handle known TLDs
    parts = domain.split(".")
    
    # Special handling for .co.uk, .com.au, etc.
    two_part_tlds = ["co.uk", "com.au", "co.nz", "co.za", "com.br"]
    
    if len(parts) >= 3:
        potential_tld = ".".join(parts[-2:])
        if potential_tld in two_part_tlds:
            # Return last 3 parts (e.g., example.co.uk)
            return ".".join(parts[-3:]) if len(parts) > 2 else domain
    
    # Standard case: return last 2 parts (e.g., example.com)
    return ".".join(parts[-2:]) if len(parts) > 1 else domain