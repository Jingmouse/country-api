"""
GlobalBridge — Country Data Collector
Combines free APIs (numbers/facts) + Claude AI (culture/habits)
into one clean JSON file per country.

Usage:
    pip install requests anthropic
    export ANTHROPIC_API_KEY=your_key_here
    python collect_country_data.py Japan
    python collect_country_data.py France
"""

import requests
import anthropic
import json
import sys
import os
from datetime import datetime


# ── 1. FREE API: Basic country facts (REST Countries) ──────────────────────────

def fetch_basic_facts(country_name: str) -> dict:
    """Fetch currency, language, region, population from REST Countries API (free, no key needed)."""
    url = f"https://restcountries.com/v3.1/name/{country_name}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()[0]

        languages = list(data.get("languages", {}).values())
        currencies = [
            f"{v['name']} ({k})"
            for k, v in data.get("currencies", {}).items()
        ]
        capital = data.get("capital", ["Unknown"])[0]
        population = data.get("population", 0)
        region = data.get("region", "Unknown")

        return {
            "capital": capital,
            "region": region,
            "population": f"{population:,}",
            "languages": languages,
            "currencies": currencies,
        }
    except Exception as e:
        print(f"  [Warning] REST Countries API failed: {e}")
        return {}


# ── 2. FREE API: Climate data (Open-Meteo, no key needed) ─────────────────────

def fetch_climate(country_name: str, lat: float, lon: float) -> dict:
    """Fetch average monthly temperatures from Open-Meteo (free, no API key)."""
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        "&start_date=2023-01-01&end_date=2023-12-31"
        "&monthly=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=auto"
    )
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        data = res.json()
        monthly = data.get("monthly", {})

        temps_max = monthly.get("temperature_2m_max", [])
        temps_min = monthly.get("temperature_2m_min", [])
        precipitation = monthly.get("precipitation_sum", [])

        if temps_max and temps_min:
            avg_max = round(sum(t for t in temps_max if t) / len(temps_max), 1)
            avg_min = round(sum(t for t in temps_min if t) / len(temps_min), 1)
            hottest_month = temps_max.index(max(temps_max)) + 1
            coldest_month = temps_min.index(min(temps_min)) + 1
            total_rain = round(sum(p for p in precipitation if p), 0)

            month_names = ["Jan","Feb","Mar","Apr","May","Jun",
                           "Jul","Aug","Sep","Oct","Nov","Dec"]
            return {
                "avg_temp_range": f"{avg_min}°C to {avg_max}°C",
                "hottest_month": month_names[hottest_month - 1],
                "coldest_month": month_names[coldest_month - 1],
                "annual_rainfall_mm": total_rain,
            }
    except Exception as e:
        print(f"  [Warning] Open-Meteo API failed: {e}")
    return {}


# ── 3. FREE API: Cost of living (Numbeo — public data endpoint) ───────────────

def fetch_cost_of_living(country_name: str) -> dict:
    """
    Fetch cost of living index from Numbeo's public API.
    NOTE: Numbeo's full API requires a paid key. This uses the free public
    indices endpoint. For richer data, sign up at https://www.numbeo.com/api/
    and replace with: https://www.numbeo.com/api/country_prices?api_key=KEY&country=Japan
    """
    url = f"https://www.numbeo.com/api/indices?api_key=FREE&country={country_name}"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        return {
            "cost_of_living_index": data.get("cost_of_living_index"),
            "rent_index": data.get("rent_index"),
            "groceries_index": data.get("groceries_index"),
            "restaurant_price_index": data.get("restaurant_price_index"),
            "source": "Numbeo (index vs. NYC=100)",
        }
    except Exception as e:
        print(f"  [Warning] Numbeo API failed (may need paid key): {e}")
        return {"note": "Add your Numbeo API key for cost of living data"}


# ── 4. AI: Cultural data via Claude ───────────────────────────────────────────

def fetch_cultural_data(country_name: str) -> dict:
    """Use Claude to generate structured cultural data for the country."""
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    prompt = f"""You are a knowledgeable travel and culture researcher.
Generate accurate, practical cultural data for {country_name} for a country comparison website.

Respond with ONLY a valid JSON object — no explanation, no markdown, no backticks.
Use this exact structure:

{{
  "food": {{
    "staple_dishes": "3-4 most common everyday dishes",
    "meal_culture": "1-2 sentences on how people eat day to day",
    "avg_cheap_meal_usd": "price in USD for a cheap local restaurant meal",
    "dietary_notes": "vegetarian/halal/allergy situation in 1 sentence"
  }},
  "daily_habits": {{
    "work_culture": "work hours, overtime norms, punctuality in 1-2 sentences",
    "social_norms": "2-3 key social customs a visitor should know",
    "transport": "how people typically get around daily"
  }},
  "shopping": {{
    "major_supermarkets": "2-3 most common supermarket chains",
    "convenience_stores": "common convenience/corner stores if any",
    "popular_malls_or_markets": "most well-known shopping spots"
  }},
  "practical_info": {{
    "tipping_culture": "is tipping expected, normal, or unusual?",
    "healthcare": "1 sentence on public healthcare access",
    "safety": "general safety level for visitors"
  }}
}}"""

    try:
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        # Strip any accidental markdown fences
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [Warning] Claude returned invalid JSON: {e}")
        return {}
    except Exception as e:
        print(f"  [Warning] Claude API failed: {e}")
        return {}


# ── 5. Coordinate lookup (simple hardcoded dict — extend as needed) ────────────

COUNTRY_COORDS = {
    "Japan":         (35.68, 139.69),
    "France":        (48.85, 2.35),
    "United States": (38.89, -77.03),
    "China":         (39.90, 116.40),
    "Germany":       (52.52, 13.40),
    "Brazil":        (-15.78, -47.93),
    "India":         (28.61, 77.21),
    "Australia":     (-35.28, 149.13),
    "Mexico":        (19.43, -99.13),
    "South Korea":   (37.57, 126.98),
    "Thailand":      (13.75, 100.52),
    "Italy":         (41.90, 12.50),
    "Spain":         (40.42, -3.70),
    "Canada":        (45.42, -75.69),
    "United Kingdom":(51.51, -0.13),
}


# ── 6. Main collector ─────────────────────────────────────────────────────────

def collect_country(country_name: str) -> dict:
    print(f"\nCollecting data for: {country_name}")
    print("  [1/4] Fetching basic facts from REST Countries...")
    basic = fetch_basic_facts(country_name)

    coords = COUNTRY_COORDS.get(country_name, (0, 0))
    print(f"  [2/4] Fetching climate data from Open-Meteo (lat={coords[0]}, lon={coords[1]})...")
    climate = fetch_climate(country_name, coords[0], coords[1])

    print("  [3/4] Fetching cost of living from Numbeo...")
    cost = fetch_cost_of_living(country_name)

    print("  [4/4] Generating cultural data with Claude AI...")
    culture = fetch_cultural_data(country_name)

    result = {
        "country": country_name,
        "collected_at": datetime.now().isoformat(),
        "basic_facts": basic,
        "climate": climate,
        "cost_of_living": cost,
        **culture,   # food, daily_habits, shopping, practical_info
    }

    # Save to file
    filename = f"{country_name.lower().replace(' ', '_')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"  Saved to {filename}")
    return result


# ── 7. Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python collect_country_data.py <CountryName>")
        print("Example: python collect_country_data.py Japan")
        print("\nAvailable countries with coordinates:")
        for c in COUNTRY_COORDS:
            print(f"  - {c}")
        sys.exit(1)

    country = " ".join(sys.argv[1:])

    if country not in COUNTRY_COORDS:
        print(f"Warning: '{country}' not in COUNTRY_COORDS.")
        print("Climate data will be skipped. Add coordinates to COUNTRY_COORDS dict.")

    data = collect_country(country)
    print(f"\nDone! Preview:")
    print(json.dumps(data, indent=2, ensure_ascii=False)[:800] + "...")
