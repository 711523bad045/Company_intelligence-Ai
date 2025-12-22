"""
Description Generator - 100% OFFLINE
NO API calls, uses rule-based text extraction only.
"""

import re
from typing import Tuple


def clean_text(text: str) -> str:
    """Remove navigation, footer, and common noise."""
    if not text:
        return ""
    
    noise_patterns = [
        r'(?i)(home|about|contact|privacy|terms|cookies?|login|sign up|subscribe)\s*\|',
        r'(?i)copyright\s+©?\s*\d{4}',
        r'(?i)all rights reserved',
        r'(?i)follow us on',
        r'(?i)(facebook|twitter|linkedin|instagram|youtube)\s*:?',
        r'(?i)menu\s*\n',
        r'(?i)skip to (main )?content',
    ]
    
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text)
    
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)
    
    return text.strip()


def extract_sentences(text: str) -> list:
    """Extract meaningful sentences."""
    if not text:
        return []
    
    sentences = re.split(r'[.!?]+', text)
    good_sentences = []
    
    for sent in sentences:
        sent = sent.strip()
        
        if len(sent) < 20 or len(sent) > 200:
            continue
        
        noise_keywords = ['cookie', 'privacy policy', 'terms of service', 'login', 
                         'sign up', 'subscribe', 'newsletter', 'click here', 'read more']
        if any(keyword in sent.lower() for keyword in noise_keywords):
            continue
        
        special_chars = len(re.findall(r'[^a-zA-Z0-9\s]', sent))
        if special_chars > len(sent) * 0.3:
            continue
        
        good_sentences.append(sent)
    
    return good_sentences


def score_sentence(sentence: str) -> int:
    """Score sentence quality for business description."""
    score = 0
    lower = sentence.lower()
    
    # High-value phrases
    business_phrases = [
        'we provide', 'we offer', 'we help', 'we are', 'we specialize',
        'our company', 'our mission', 'our service', 'our product',
        'leading provider', 'established', 'founded', 'specializes in',
        'delivers', 'creates', 'develops', 'builds', 'designs',
        'trusted by', 'serving', 'dedicated to'
    ]
    
    for phrase in business_phrases:
        if phrase in lower:
            score += 15
    
    # Industry keywords
    industry_terms = [
        'software', 'technology', 'services', 'solutions', 'platform',
        'healthcare', 'financial', 'consulting', 'manufacturing', 'retail',
        'education', 'enterprise', 'business', 'professional', 'digital',
        'innovative', 'comprehensive', 'quality', 'expert'
    ]
    
    for term in industry_terms:
        if term in lower:
            score += 5
    
    # Negative indicators
    bad_words = ['click', 'here', 'more info', 'learn more', 'contact us']
    for word in bad_words:
        if word in lower:
            score -= 20
    
    return score


def generate_descriptions(text: str) -> Tuple[str, str]:
    """
    Generate descriptions using OFFLINE rule-based extraction.
    NO API CALLS - 100% local processing.
    
    Args:
        text: Raw website text
        
    Returns:
        (short_description, long_description)
    """
    cleaned_text = clean_text(text)
    sentences = extract_sentences(cleaned_text)
    
    if not sentences:
        return (
            "Company providing business services and solutions.",
            "Company providing business services and solutions. Committed to delivering quality products and professional support to customers."
        )
    
    # Score and rank sentences
    scored = [(sent, score_sentence(sent)) for sent in sentences]
    scored.sort(key=lambda x: x[1], reverse=True)
    
    # Get best sentences
    best = [sent for sent, score in scored if score > 0]
    
    if not best:
        best = sentences[:3]
    
    # Short description: best single sentence
    short = best[0]
    if not short.endswith('.'):
        short += '.'
    
    # Long description: top 2-3 sentences
    long_parts = best[:min(3, len(best))]
    long = '. '.join(long_parts)
    if not long.endswith('.'):
        long += '.'
    
    # Clean formatting
    short = re.sub(r'\s+', ' ', short).strip()
    long = re.sub(r'\s+', ' ', long).strip()
    
    # Quality checks
    if len(short) < 20:
        short = "Company providing business services and solutions."
    
    if len(long) < 40:
        long = short + " Committed to delivering quality products and professional support."
    
    return short, long


if __name__ == "__main__":
    test = """
    Welcome to TechCorp Industries
    
    We are a leading provider of cloud-based enterprise software solutions.
    Our platform helps businesses streamline operations and improve productivity.
    Founded in 2015, we serve over 500 companies worldwide.
    
    Contact us today.
    """
    
    short, long = generate_descriptions(test)
    print("SHORT:", short)
    print("LONG:", long)