import re

keywords = [
    "ai", "artificial intelligence", "wifi", "wi-fi", "iphone",
    "computer", "internet", "smartphone", "nuclear", "airplane", "television",
    "radio", "transistor", "microchip", "software", "email", "website", "blog",
    "online", "digital", "virtual", "cyber", "quantum mechanics", "relativity",
    "plastic", "antibiotics", "dna", "gene editing", "spaceflight", "satellite",
    "automobile", "tank", "video", "mp3", "laser", "world war", "united nations",
    "python", "programming language", "nazi", "soviet union", "cold war"
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
        if re.search(r'\b' + re.escape(word) + r'(?:s|es)?\b', query_lower):
            return False

    # Check for spelled-out modern centuries
    if re.search(r'\b(twentieth|twenty[\s-]*first|twenty[\s-]*second|20th|21st|22nd)\s+century\b', query_lower):
        return False

    # Check for spelled-out modern years (e.g., "nineteen hundred", "nineteen twenty", "two thousand")
    # We match "nineteen" followed by 0-99, or "two thousand"
    if re.search(r'\bnineteen[\s-]*(hundred|oh[\s-]+(one|two|three|four|five|six|seven|eight|nine)|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)\b|\btwo[\s-]*thousand\b', query_lower):
        return False

    # Check for dates > 1899
    # We match numbers >= 1900.
    # To avoid false positives (e.g. "5000 men" or "1950 dollars"), we check the following word.
    matches = re.finditer(r'\b([1-9]\d{3})(s)?\b', query_lower)
    for match in matches:
        num = int(match.group(1))
        has_s = match.group(2)
        if num >= 1900:
            if has_s:
                # "1920s" -> definitely a year/decade reference
                return False

            # Check context immediately after the number
            context_after = query_lower[match.end():].strip()
            if re.match(r'^[\W_]*(men|women|soldiers|troops|people|persons|dollars|pounds|miles|feet|meters|horses|ships|guns|pages|words|years|days|months|hours|minutes|apples|books|casualties|deaths|sailors|ton|tons|kilogram|kilograms|gram|grams|ounce|ounces|coin|coins)\b', context_after):
                # It's a quantity
                continue

            if re.match(r'^[\W_]*[£$€¥]', context_after):
                # It's a currency with symbol after
                continue

            # Check context before the number (e.g. £1900, $1950)
            context_before = query_lower[:match.start()].strip()
            if re.search(r'[£$€¥]\s*$', context_before):
                continue

            if re.match(r'^[\W_]*(bc|bce|b\.c\.|b\.c\.e\.)(?:\b|\Z|\s)', context_after):
                # It's a BC/BCE year
                continue

            # Likely a year > 1899
            return False

    return True

def validate_response(response: str) -> bool:
    """
    Returns True if response contains no modern info.
    """
    return validate_query(response)
