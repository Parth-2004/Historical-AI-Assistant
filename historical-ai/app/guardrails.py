import re

keywords = [
    "ai", "artificial intelligence", "wifi", "wi-fi", "iphone", 
    "computer", "internet", "smartphone", "nuclear", "airplane", "television", 
    "radio", "transistor", "microchip", "software", "email", "website", "blog", 
    "online", "digital", "virtual", "cyber", "quantum mechanics", "relativity",
    "plastic", "antibiotics", "dna", "gene editing", "spaceflight", "satellite",
    "automobile", "tank", "video", "mp3", "laser"
]

def validate_query(query: str) -> bool:
    """
    Returns True if query is valid for the era (pre-1900).
    Returns False if it contains modern terms.
    """
    query_lower = query.lower()
    for word in keywords:
        # Use regex to check for whole word match to avoid false positives (e.g. "ai" in "explain")
        # Escape the word in case it contains regex special chars
        if re.search(r'\b' + re.escape(word) + r'\b', query_lower):
            return False
            
    # Check for dates > 1899
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', query)
    if years:
        # Allow '1900'? "before 31 December 1899" -> so 1900 is improper usually, 
        # but boundaries are tricky. The prompt says "Pre-1900", so < 1900.
        return False
        
    return True

def validate_response(response: str) -> bool:
    """
    Returns True if response contains no modern info.
    """
    return validate_query(response)
