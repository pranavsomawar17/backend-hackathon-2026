import os
import re
import json
from functools import lru_cache
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ✅ FIXED: Read from .env file, never hardcode keys
api_key = os.getenv("OPENAI_API_KEY")

client = None
if api_key:
    client = OpenAI(api_key=api_key)
else:
    print("⚠️  WARNING: OPENAI_API_KEY not set. LLM fallback disabled. Using rule engine only.")

CATEGORIES = ["Travel", "Software", "Office", "Meals", "Other"]

# -----------------------------
# LOCATION DATABASE
# -----------------------------

LOCATIONS = [
    "airport", "station", "office", "hotel",
    "pune", "mumbai", "bangalore", "delhi",
    "hyderabad", "chennai", "kolkata", "ahmedabad",
    "jaipur", "surat", "lucknow", "nagpur", "home"
]

# -----------------------------
# NORMALIZE TEXT
# -----------------------------

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text

# -----------------------------
# ROUTE DETECTION
# -----------------------------

def detect_route_travel(desc: str) -> bool:
    desc = normalize(desc)

    pattern1 = r"\b\w+\s+to\s+\w+\b"
    pattern2 = r"\bfrom\s+\w+\s+to\s+\w+\b"

    if re.search(pattern1, desc) or re.search(pattern2, desc):
        for loc in LOCATIONS:
            if loc in desc:
                return True

    return False

# -----------------------------
# FALLBACK RULE ENGINE
# -----------------------------

def fallback_category(description: str) -> str:
    desc = normalize(description)

    # PRIORITY 1: ROUTE DETECTION
    if detect_route_travel(desc):
        return "Travel"

    # PRIORITY 2: TRAVEL KEYWORDS (expanded for Indian context)
    travel_keywords = [
        "airport", "flight", "uber", "ola", "rapido",
        "taxi", "cab", "train", "bus", "metro", "auto",
        "rickshaw", "fuel", "petrol", "diesel", "parking",
        "toll", "travel", "trip", "journey", "irctc",
        "railway", "bike taxi", "local train", "boarding pass",
        "luggage", "transit", "commute", "vehicle", "mileage"
    ]
    if any(word in desc for word in travel_keywords):
        return "Travel"

    # PRIORITY 3: SOFTWARE
    software_keywords = [
        "software", "license", "subscription", "cloud",
        "aws", "azure", "gcp", "zoom", "github", "slack",
        "figma", "notion", "jira", "confluence", "adobe",
        "microsoft 365", "google workspace", "saas", "api",
        "hosting", "domain", "vps", "server"
    ]
    if any(word in desc for word in software_keywords):
        return "Software"

    # PRIORITY 4: OFFICE
    office_keywords = [
        "chair", "desk", "printer", "paper", "stationery",
        "monitor", "keyboard", "mouse", "pen", "notebook",
        "whiteboard", "marker", "toner", "cartridge",
        "headphones", "webcam", "usb", "charger", "cable",
        "office supplies", "furniture", "lamp", "stand"
    ]
    if any(word in desc for word in office_keywords):
        return "Office"

    # PRIORITY 5: MEALS (keywords + vendors, expanded for India)
    meal_keywords = [
        "lunch", "dinner", "breakfast", "food", "meal",
        "coffee", "tea", "restaurant", "cafe", "snack",
        "beverages", "catering", "tiffin", "biryani",
        "pizza", "burger", "sandwich", "juice", "water bottle"
    ]
    meal_vendors = [
        "starbucks", "swiggy", "zomato", "dominos", "kfc",
        "mcdonald", "blinkit", "zepto", "box8", "faasos",
        "dunkin", "subway", "haldirams", "chaayos", "cafe coffee day",
        "barista", "naturals", "licious", "freshmenu"
    ]
    if any(word in desc for word in meal_keywords):
        return "Meals"
    if any(vendor in desc for vendor in meal_vendors):
        return "Meals"

    return "Other"

# -----------------------------
# LLM CATEGORIZATION (CACHED)
# Identical descriptions won't call the API twice
# -----------------------------

@lru_cache(maxsize=256)
def llm_category(description: str) -> str:
    """
    Calls OpenAI only for ambiguous 'Other' cases.
    Results are cached so the same description never hits the API twice.
    """
    if client is None:
        return "Other"

    try:
        prompt = f"""
You are an expense categorization assistant for an Indian company.
Categorize the following expense into EXACTLY one of these categories:
Travel, Software, Office, Meals, Other

Rules:
- Travel: transport, cabs, flights, fuel, toll, metro, train, route-based expenses
- Software: SaaS, subscriptions, licenses, cloud, hosting, domains
- Office: stationery, furniture, equipment, hardware peripherals
- Meals: food, drinks, restaurants, food delivery apps
- Other: anything that doesn't fit above

Examples:
"Airport to Pune cab" → Travel
"Zoom annual plan" → Software
"Office chair purchase" → Office
"Swiggy lunch order" → Meals
"Team building event" → Other

Expense: {description}

Respond with ONLY valid JSON, no explanation, no markdown:
{{"category": "Travel"}}
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        content = re.sub(r"```json|```", "", content).strip()

        data = json.loads(content)
        category = data.get("category", "").strip()

        if category not in CATEGORIES:
            print(f"⚠️  LLM returned unknown category '{category}', falling back to Other")
            return "Other"

        return category

    except json.JSONDecodeError as e:
        print(f"❌ JSON parse error from LLM: {e}")
        return "Other"
    except Exception as e:
        print(f"❌ LLM ERROR: {e}")
        return "Other"

# -----------------------------
# MAIN PUBLIC FUNCTION
# -----------------------------

def categorize_expense(description: str) -> str:
    """
    Categorize an expense description.
    1. Try deterministic rule engine first (fast, free)
    2. Fall back to LLM for ambiguous cases (cached)
    """
    if not description or not description.strip():
        return "Other"

    # Step 1: Rule engine
    rule_category = fallback_category(description)

    if rule_category != "Other":
        return rule_category

    # Step 2: LLM fallback (cached by description)
    return llm_category(description.strip().lower())


# -----------------------------
# QUICK TEST
# -----------------------------

if __name__ == "__main__":
    test_cases = [
        "Airport to Pune cab",
        "Ola ride from office to station",
        "Swiggy lunch order",
        "Zoom subscription renewal",
        "New office chair from Amazon",
        "Team outing dinner at Taj",
        "Fuel reimbursement for client visit",
        "AWS EC2 monthly bill",
        "Random team expense",
    ]

    print(f"\n{'Description':<40} {'Category'}")
    print("-" * 55)
    for desc in test_cases:
        cat = categorize_expense(desc)
        print(f"{desc:<40} {cat}")