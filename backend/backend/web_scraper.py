"""
Web Scraper Module
Scrapes website content including title and text.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any


def scrape_website(url: str, timeout: int = 10) -> Dict[str, Any] | None:
    """
    Scrape website and extract title and text content.
    
    Args:
        url: Website URL to scrape
        timeout: Request timeout in seconds
        
    Returns:
        Dict with 'title' and 'text' keys, or None if failed
    """
    try:
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Make request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = ""
        if soup.title:
            title = soup.title.string.strip() if soup.title.string else ""
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator=' ', strip=True)
        
        # Clean up whitespace
        text = ' '.join(text.split())
        
        return {
            "title": title,
            "text": text,
            "url": url
        }
        
    except requests.exceptions.Timeout:
        print(f"⚠️  Timeout scraping {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Error scraping {url}: {e}")
        return None
    except Exception as e:
        print(f"⚠️  Unexpected error scraping {url}: {e}")
        return None


if __name__ == "__main__":
    # Test
    test_url = "example.com"
    result = scrape_website(test_url)
    if result:
        print(f"Title: {result['title']}")
        print(f"Text: {result['text'][:200]}...")
    else:
        print("Failed to scrape")