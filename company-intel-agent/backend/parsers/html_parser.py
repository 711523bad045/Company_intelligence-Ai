"""
Optimized HTML Text Extraction
- Strips navigation, footer, scripts
- Hard limit: 3000 characters
- Extracts only business content
"""

from bs4 import BeautifulSoup


def extract_text_from_html(html_path: str) -> str:
    """
    Fast HTML parsing with intelligent content extraction.
    
    Speed optimizations:
    - Remove junk elements (nav, footer, script)
    - Extract only main content
    - Hard limit: 3000 chars
    
    Args:
        html_path: Path to HTML file
    
    Returns:
        Cleaned text (max 3000 chars)
    """
    
    try:
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            soup = BeautifulSoup(f, "html.parser")
        
        # ⚡ SPEED: Remove junk elements
        junk_tags = [
            "script", "style", "nav", "footer", 
            "header", "aside", "iframe", "noscript"
        ]
        
        for tag in junk_tags:
            for element in soup.find_all(tag):
                element.decompose()
        
        # ⚡ SPEED: Remove cookie banners, popups
        junk_classes = [
            "cookie", "banner", "popup", "modal",
            "navigation", "menu", "sidebar"
        ]
        
        for class_name in junk_classes:
            for element in soup.find_all(class_=lambda x: x and class_name in x.lower()):
                element.decompose()
        
        # Extract text
        text = soup.get_text(separator=" ", strip=True)
        
        # ⚡ SPEED: Clean whitespace
        text = " ".join(text.split())
        
        # ⚡ SPEED: Hard limit to 3000 chars
        return text[:3000]
        
    except Exception as e:
        print(f"⚠️ HTML parsing error: {e}")
        return ""