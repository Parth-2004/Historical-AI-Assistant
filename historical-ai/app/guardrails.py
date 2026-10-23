import re

keywords = [
    "ai", "artificial intelligence", "wifi", "wi-fi", "iphone",
    "computer", "internet", "smartphone", "nuclear", "airplane", "television",
    "radio", "transistor", "microchip", "software", "email", "website", "blog",
    "online", "digital", "virtual", "cyber", "quantum mechanics", "relativity",
    "antibiotics", "dna", "gene editing", "spaceflight", "satellite",
    "tank", "video", "mp3", "laser", "world war", "united nations",
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
    if re.search(r'\b(?:(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)[\s-]*(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth)|(?:twentieth|thirtieth|fortieth|fiftieth|sixtieth|seventieth|eightieth|ninetieth)|(?:2[0-9]|[3-9][0-9]|[1-9][0-9]{2,})(?:st|nd|rd|th))[\s-]*century\b', query_lower):
        return False

    # Check for spelled-out modern years (e.g., "nineteen hundred", "nineteen twenty", "two thousand", "twenty twenty", "twenty-one hundred")
    ones = r'one|two|three|four|five|six|seven|eight|nine'
    teens = r'ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen'
    tens = r'twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety'
    tens_ones = rf'(?:{tens})(?:[\s-]+(?:{ones}))?'
    num_10_to_99 = rf'(?:{teens}|{tens_ones})'
    num_0_to_99 = rf'(?:{ones}|{num_10_to_99})'
    year_prefix = rf'(?:nineteen|twenty|twenty[\s-]+one)'

    pattern_spelled_years = rf'\b(?:{year_prefix}[\s-]+hundred|(?:nineteen|twenty)[\s-]+(?:oh[\s-]+(?:{ones})|{num_10_to_99})|two[\s-]*thousand(?:\s+and\s+(?:{num_0_to_99}))?)\b'
    # Ensure matches_spelled includes 'twenty hundred'
    matches_spelled = list(re.finditer(pattern_spelled_years, query_lower))
    matches_twenty = list(re.finditer(r'\btwenty[\s-]+hundred\b', query_lower))

    # Simple deduplication (just append, doesn't matter if tested twice)
    matches_spelled.extend(matches_twenty)
    for match in matches_spelled:
        context_after = query_lower[match.end():].strip()
        if re.match(r'^[\W_]*(men|women|soldiers|troops|people|persons|dollars|pounds|francs|marks|rupees|yen|shillings|pence|ducats|guilders|gold|silver|copper|miles|feet|meters|leagues|yards|acres|horses|sheep|cattle|pigs|cows|dogs|cats|ships|boats|guns|swords|muskets|cannons|pages|words|letters|years|days|months|hours|minutes|seconds|apples|books|casualties|deaths|sailors|ton|tons|kilogram|kilograms|gram|grams|ounce|ounces|gallons|liters|pints|quarts|coin|coins|pieces|chickens|trees|houses|birds|fish|plants|buildings|stones|bricks|shields|arrows|bows|spears|knives|chariots|wagons|carts|wheels|nails|tools|weapons|instruments|garments|clothes|shoes|boots|hats|chairs|tables|beds|pots|pans|cups|bowls|plates|bottles|barrels|chests|boxes|bags|sacks|tents|huts|cabins|cottages|farms|villages|towns|cities|kingdoms|empires|nations|countries|islands|mountains|rivers|lakes|seas|oceans|stars|planets|moons|suns|galaxies|universes|atoms|molecules|cells|organisms|animals|fungi|bacteria|viruses|diseases|plagues|epidemics|pandemics|wars|battles|skirmishes|sieges|campaigns|treaties|alliances|pacts|agreements|laws|rules|regulations|decrees|edicts|proclamations|declarations|constitutions|charters|bills|acts|statutes|ordinances|resolutions|petitions|appeals|demands|requests|prayers|hymns|songs|poems|stories|tales|myths|legends|fables|epics|sagas|chronicles|histories|annals|records|registers|lists|inventories|catalogues|directories|dictionaries|encyclopedias|almanacs|atlases|maps|charts|graphs|diagrams|figures|illustrations|pictures|paintings|drawings|sketches|sculptures|statues|monuments|memorials|tombs|graves|cemeteries|churches|cathedrals|temples|mosques|synagogues|shrines|altars|idols|gods|goddesses|deities|spirits|demons|angels|saints|prophets|priests|monks|nuns|kings|queens|princes|princesses|emperors|empresses|pharaohs|sultans|tsars|khas|khans|chiefs|leaders|rulers|governors|mayors|judges|magistrates|lawyers|doctors|healers|scholars|teachers|students|philosophers|scientists|engineers|architects|artists|musicians|writers|poets|actors|dancers|athletes|warriors|knights|samurai|ninjas|pirates|merchants|traders|farmers|peasants|serfs|slaves|servants|workers|laborers|artisans|craftsmen|smiths|weavers|tailors|carpenters|masons|bakers|butchers|brewers|vintners|cooks|waiters|maids|nannies|tutors|guards|watchmen|policemen|detectives|spies|assassins|thieves|robbers|bandits|outlaws|smugglers|rebels|revolutionaries|patriots|traitors|heroes|villains|victims|survivors|refugees|immigrants|emigrants|travelers|explorers|adventurers|pioneers|settlers|colonists|conquerors|invaders|barbarians|nomads|tribes|clans|families|households|couples|parents|children|sons|daughters|brothers|sisters|uncles|aunts|nephews|nieces|cousins|grandparents|grandchildren|ancestors|descendants|relatives|friends|enemies|allies|rivals|partners|colleagues|acquaintances|strangers|guests|hosts|neighbors|citizens|subjects|residents|inhabitants|natives|foreigners|aliens)\b', context_after):
            continue
        if re.match(r'^[\W_]*[£$€¥]', context_after):
            continue
        context_before = query_lower[:match.start()].strip()
        if re.search(r'[£$€¥]\s*$', context_before):
            continue
        return False

    # Check for spelled-out modern decades (e.g., "nineteen twenties", "nineteen nineties")
    if re.search(r'\b(nineteen|twenty)[\s-]*(twenties|thirties|forties|fifties|sixties|seventies|eighties|nineties|tens)\b', query_lower):
        return False

    # Check for dates > 1899
    # We match numbers >= 1900.
    # To avoid false positives (e.g. "5000 men" or "1950 dollars"), we check the following word.
    # We use a negative lookahead (?![.,]\d) to ignore numbers that are part of a larger decimal or comma-separated quantity (e.g., 1950.00, 1900,000).
    matches = re.finditer(r'\b([1-9]\d{0,2}(?:,\d{3})+|[1-9]\d{3,})(s|th|st|nd|rd|ad|ce|bc|bce)?\b(?![.,]\d)', query_lower)
    for match in matches:
        num = int(match.group(1).replace(",", ""))
        suffix = match.group(2)
        if num >= 1900:
            if suffix in ['s', 'th', 'st', 'nd', 'rd', 'ad', 'ce']:
                return False
            elif suffix in ['bc', 'bce']:
                continue

            # Check context immediately after the number
            context_after = query_lower[match.end():].strip()
            if re.match(r'^[\W_]*(men|women|soldiers|troops|people|persons|dollars|pounds|francs|marks|rupees|yen|shillings|pence|ducats|guilders|gold|silver|copper|miles|feet|meters|leagues|yards|acres|horses|sheep|cattle|pigs|cows|dogs|cats|ships|boats|guns|swords|muskets|cannons|pages|words|letters|years|days|months|hours|minutes|seconds|apples|books|casualties|deaths|sailors|ton|tons|kilogram|kilograms|gram|grams|ounce|ounces|gallons|liters|pints|quarts|coin|coins|pieces|chickens|trees|houses|birds|fish|plants|buildings|stones|bricks|shields|arrows|bows|spears|knives|chariots|wagons|carts|wheels|nails|tools|weapons|instruments|garments|clothes|shoes|boots|hats|chairs|tables|beds|pots|pans|cups|bowls|plates|bottles|barrels|chests|boxes|bags|sacks|tents|huts|cabins|cottages|farms|villages|towns|cities|kingdoms|empires|nations|countries|islands|mountains|rivers|lakes|seas|oceans|stars|planets|moons|suns|galaxies|universes|atoms|molecules|cells|organisms|animals|fungi|bacteria|viruses|diseases|plagues|epidemics|pandemics|wars|battles|skirmishes|sieges|campaigns|treaties|alliances|pacts|agreements|laws|rules|regulations|decrees|edicts|proclamations|declarations|constitutions|charters|bills|acts|statutes|ordinances|resolutions|petitions|appeals|demands|requests|prayers|hymns|songs|poems|stories|tales|myths|legends|fables|epics|sagas|chronicles|histories|annals|records|registers|lists|inventories|catalogues|directories|dictionaries|encyclopedias|almanacs|atlases|maps|charts|graphs|diagrams|figures|illustrations|pictures|paintings|drawings|sketches|sculptures|statues|monuments|memorials|tombs|graves|cemeteries|churches|cathedrals|temples|mosques|synagogues|shrines|altars|idols|gods|goddesses|deities|spirits|demons|angels|saints|prophets|priests|monks|nuns|kings|queens|princes|princesses|emperors|empresses|pharaohs|sultans|tsars|khas|khans|chiefs|leaders|rulers|governors|mayors|judges|magistrates|lawyers|doctors|healers|scholars|teachers|students|philosophers|scientists|engineers|architects|artists|musicians|writers|poets|actors|dancers|athletes|warriors|knights|samurai|ninjas|pirates|merchants|traders|farmers|peasants|serfs|slaves|servants|workers|laborers|artisans|craftsmen|smiths|weavers|tailors|carpenters|masons|bakers|butchers|brewers|vintners|cooks|waiters|maids|nannies|tutors|guards|watchmen|policemen|detectives|spies|assassins|thieves|robbers|bandits|outlaws|smugglers|rebels|revolutionaries|patriots|traitors|heroes|villains|victims|survivors|refugees|immigrants|emigrants|travelers|explorers|adventurers|pioneers|settlers|colonists|conquerors|invaders|barbarians|nomads|tribes|clans|families|households|couples|parents|children|sons|daughters|brothers|sisters|uncles|aunts|nephews|nieces|cousins|grandparents|grandchildren|ancestors|descendants|relatives|friends|enemies|allies|rivals|partners|colleagues|acquaintances|strangers|guests|hosts|neighbors|citizens|subjects|residents|inhabitants|natives|foreigners|aliens)\b', context_after):
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
