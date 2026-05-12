# ── facts_db.py ──────────────────────────────────────────────────
import re

PLANETS = [
    "mars", "jupiter", "saturn", "venus",
    "mercury", "neptune", "uranus", "pluto"
]

CONTINENTS = [
    "asia", "europe", "africa", "antarctica",
    "australia", "north america", "south america"
]

OCEANS = [
    "pacific", "atlantic", "indian", "arctic", "southern"
]

COUNTRIES = [
    "nepal", "india", "china", "usa", "france", "japan",
    "germany", "australia", "brazil", "canada", "italy",
    "spain", "pakistan", "bangladesh", "russia", "uk",
    "thailand", "south korea", "north korea", "sri lanka",
    "myanmar", "indonesia", "malaysia", "singapore", "egypt",
    "nigeria", "kenya", "argentina", "mexico", "portugal"
]

CAPITAL_FACTS = {
    "nepal": "kathmandu",
    "india": "new delhi",
    "usa": "washington",
    "france": "paris",
    "japan": "tokyo",
    "china": "beijing",
    "uk": "london",
    "australia": "canberra",
    "germany": "berlin",
    "russia": "moscow",
    "brazil": "brasilia",
    "canada": "ottawa",
    "italy": "rome",
    "spain": "madrid",
    "pakistan": "islamabad",
    "bangladesh": "dhaka",
    "sri lanka": "colombo",
    "thailand": "bangkok",
    "south korea": "seoul",
    "north korea": "pyongyang",
    "egypt": "cairo",
    "argentina": "buenos aires",
    "mexico": "mexico city",
    "indonesia": "jakarta",
    "malaysia": "kuala lumpur",
    "singapore": "singapore",
    "myanmar": "naypyidaw",
    "portugal": "lisbon",
    "nigeria": "abuja",
    "kenya": "nairobi"
}

HISTORICAL_FIGURES = [
    "prithvi narayan shah", "buddha", "einstein",
    "newton", "gandhi", "shakespeare", "napoleon",
    "hitler", "lincoln", "washington", "socrates",
    "aristotle", "plato", "julius caesar", "cleopatra",
    "genghis khan", "alexander the great", "marie curie",
    "galileo", "copernicus", "darwin", "freud", "marx",
    "beethoven", "mozart", "michelangelo", "leonardo da vinci",
    "columbus", "magellan", "marco polo", "ashoka", "akbar",
    "chandragupta", "ramesses", "confucius", "attila the hun"
]

MODERN_ACTIVITIES = [
    "football", "cricket", "basketball", "baseball",
    "volleyball", "badminton", "tennis", "golf",
    "drove", "drive", "car", "motorcycle", "airplane",
    "aeroplane", "helicopter", "rocket", "spaceship",
    "phone", "mobile", "computer", "internet", "tv",
    "television", "radio", "electricity", "laptop",
    "tablet", "camera", "photograph", "photography",
    "instagram", "facebook", "twitter", "youtube",
    "tiktok", "whatsapp", "snapchat", "google",
    "netflix", "spotify", "pizza", "burger", "microwave",
    "refrigerator", "air conditioner", "elevator",
    "selfie", "video call", "zoom", "email",
    "nuclear", "atomic bomb", "satellite", "gps"
]

MYTHS = [
    ("humans only use 10",
     "Humans use virtually all parts of their brain, not just 10%"),
    ("lightning never strikes",
     "Lightning can and does strike the same place multiple times"),
    ("great wall of china visible from space",
     "The Great Wall of China is not visible from space with the naked eye"),
    ("we swallow spiders",
     "Humans do not swallow spiders in their sleep — this is a myth"),
    ("napoleon was very short",
     "Napoleon was around 5'7\" — average height for his time"),
    ("goldfish memory",
     "Goldfish have a memory span longer than 3 seconds"),
    ("hair nails grow after death",
     "Hair and nails do not grow after death"),
    ("bulls hate red",
     "Bulls are colorblind to red — they react to movement, not color"),
    ("blood is blue inside body",
     "Blood is always red — it is never blue inside the human body"),
    ("humans and dinosaurs",
     "Humans and dinosaurs never coexisted — dinosaurs went extinct 65 million years ago"),
    ("vaccines cause autism",
     "Vaccines do not cause autism — this claim has been thoroughly debunked"),
    ("eating carrots improves eyesight",
     "Carrots do not significantly improve eyesight beyond normal levels"),
    ("sugar makes children hyperactive",
     "Sugar does not cause hyperactivity in children — studies show no link"),
    ("shaving makes hair grow back thicker",
     "Shaving does not make hair grow back thicker — this is a myth"),
    ("humans lose most heat through head",
     "Humans do not lose most heat through their head — it is proportional to exposed area"),
    ("dogs see black and white",
     "Dogs are not completely colorblind — they can see blue and yellow"),
     ("there is cure to cancer",
     "There is no universal cure for cancer — some types are treatable or manageable, but no single cure exists for all cancers"),

    ("cancer is curable",
     "Not all cancers are curable — treatment success depends on type, stage, and individual factors"),

    ("cure for cancer",
     "No universal cure for cancer exists yet — research is ongoing"),
]

SCIENCE_FACTS = [
    (["light", "faster", "sound"],     True,  "Correct — Light travels faster than sound"),
    (["sound", "faster", "light"],     False, "Light travels faster than sound, not the other way around"),
    (["oxygen", "humans", "breathe"],  True,  "Correct — Humans breathe oxygen"),
    (["plants", "photosynthesis"],     True,  "Correct — Plants produce food through photosynthesis"),
    (["diamonds", "hardest"],          True,  "Correct — Diamond is the hardest natural substance"),
    (["humans", "gills"],              False, "Humans breathe with lungs, not gills"),
    (["earth", "sun", "revolves"],     True,  "Correct — Earth revolves around the Sun"),
    (["sun", "earth", "revolves"],     False, "The Sun does not revolve around the Earth"),
    (["antibiotics", "virus"],         False, "Antibiotics do not work against viruses — bacteria only"),
    (["dna", "genes"],                 True,  "Correct — DNA carries genetic information through genes"),
]


# ── check_basic_facts() FUNCTION PANI YAHAN ──────────────────────
def check_basic_facts(text):
    t = text.lower()

    for p in PLANETS:
        if p in t and "country" in t:
            return {"found": True, "prediction": "FAKE", "confidence": 99.0,
                    "method": "Basic Knowledge Check",
                    "rating": f"{p.title()} is a planet, not a country",
                    "publisher": "VERITY Knowledge Base"}

    for c in CONTINENTS:
        if c in t and "country" in t:
            return {"found": True, "prediction": "FAKE", "confidence": 99.0,
                    "method": "Basic Knowledge Check",
                    "rating": f"{c.title()} is a continent, not a country",
                    "publisher": "VERITY Knowledge Base"}

    for o in OCEANS:
        if o in t and "country" in t:
            return {"found": True, "prediction": "FAKE", "confidence": 99.0,
                    "method": "Basic Knowledge Check",
                    "rating": f"The {o.title()} Ocean is an ocean, not a country",
                    "publisher": "VERITY Knowledge Base"}

    for c in COUNTRIES:
        if c in t and "country" in t:
            return {"found": True, "prediction": "REAL", "confidence": 99.0,
                    "method": "Basic Knowledge Check",
                    "rating": f"Yes, {c.title()} is a country",
                    "publisher": "VERITY Knowledge Base"}

    if "earth" in t and "flat" in t:
        return {"found": True, "prediction": "FAKE", "confidence": 99.0,
                "method": "Basic Knowledge Check",
                "rating": "The Earth is not flat — it is an oblate spheroid",
                "publisher": "VERITY Knowledge Base"}
    if "earth" in t and "star" in t:
        return {"found": True, "prediction": "FAKE", "confidence": 99.0,
                "method": "Basic Knowledge Check",
                "rating": "The Earth is a planet, not a star",
                "publisher": "VERITY Knowledge Base"}
    if "earth" in t and "planet" in t:
        return {"found": True, "prediction": "REAL", "confidence": 99.0,
                "method": "Basic Knowledge Check",
                "rating": "Correct — The Earth is indeed a planet",
                "publisher": "VERITY Knowledge Base"}

    if "sun" in t and "planet" in t:
        return {"found": True, "prediction": "FAKE", "confidence": 99.0,
                "method": "Basic Knowledge Check",
                "rating": "The Sun is a star, not a planet",
                "publisher": "VERITY Knowledge Base"}
    if "sun" in t and "star" in t:
        return {"found": True, "prediction": "REAL", "confidence": 99.0,
                "method": "Basic Knowledge Check",
                "rating": "Correct — The Sun is a star",
                "publisher": "VERITY Knowledge Base"}

    if "moon" in t and "star" in t:
        return {"found": True, "prediction": "FAKE", "confidence": 99.0,
                "method": "Basic Knowledge Check",
                "rating": "The Moon is a natural satellite, not a star",
                "publisher": "VERITY Knowledge Base"}
    if "moon" in t and "planet" in t:
        return {"found": True, "prediction": "FAKE", "confidence": 99.0,
                "method": "Basic Knowledge Check",
                "rating": "The Moon is a natural satellite, not a planet",
                "publisher": "VERITY Knowledge Base"}
    if "moon" in t and "landing" in t and "fake" in t:
        return {"found": True, "prediction": "FAKE", "confidence": 99.0,
                "method": "Basic Knowledge Check",
                "rating": "The Moon landing in 1969 was real — Apollo 11 is well-documented",
                "publisher": "VERITY Knowledge Base"}
    if "moon" in t and "landing" in t:
        return {"found": True, "prediction": "REAL", "confidence": 99.0,
                "method": "Basic Knowledge Check",
                "rating": "The Moon landing occurred on July 20, 1969 — Apollo 11 mission",
                "publisher": "VERITY Knowledge Base"}

    if "water" in t and "boil" in t and any(x in t for x in ["0", "zero", "50", "200"]):
        return {"found": True, "prediction": "FAKE", "confidence": 95.0,
                "method": "Basic Knowledge Check",
                "rating": "Water boils at 100°C (212°F) at sea level",
                "publisher": "VERITY Knowledge Base"}
    if "water" in t and "freeze" in t and any(x in t for x in ["100", "50", "200"]):
        return {"found": True, "prediction": "FAKE", "confidence": 95.0,
                "method": "Basic Knowledge Check",
                "rating": "Water freezes at 0°C (32°F) at sea level",
                "publisher": "VERITY Knowledge Base"}

    for country, capital in CAPITAL_FACTS.items():
        if country in t and "capital" in t:
            wrong = [c for c in CAPITAL_FACTS.values()
                     if c != capital and c in t]
            if wrong:
                return {"found": True, "prediction": "FAKE", "confidence": 97.0,
                        "method": "Basic Knowledge Check",
                        "rating": f"The capital of {country.title()} is {capital.title()}, not {wrong[0].title()}",
                        "publisher": "VERITY Knowledge Base"}
            if capital in t:
                return {"found": True, "prediction": "REAL", "confidence": 99.0,
                        "method": "Basic Knowledge Check",
                        "rating": f"Correct — The capital of {country.title()} is {capital.title()}",
                        "publisher": "VERITY Knowledge Base"}

    for person in HISTORICAL_FIGURES:
        for activity in MODERN_ACTIVITIES:
            if person in t and activity in t:
                return {"found": True, "prediction": "FAKE", "confidence": 95.0,
                        "method": "Historical Context Check",
                        "rating": f"'{person.title()}' lived before '{activity}' existed",
                        "publisher": "VERITY Knowledge Base"}

    for triggers, is_real, explanation in SCIENCE_FACTS:
        if all(word in t for word in triggers):
            return {"found": True,
                    "prediction": "REAL" if is_real else "FAKE",
                    "confidence": 99.0,
                    "method": "Basic Knowledge Check",
                    "rating": explanation,
                    "publisher": "VERITY Knowledge Base"}

    for trigger, reason in MYTHS:
        if trigger in t:
            return {"found": True, "prediction": "FAKE", "confidence": 97.0,
                    "method": "Basic Knowledge Check",
                    "rating": reason,
                    "publisher": "VERITY Knowledge Base"}

    return {"found": False}