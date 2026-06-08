import os
import re
import requests
from functools import lru_cache
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

# =========================
# 工具函数
# =========================
def clean_text(text):
    text = re.sub(r"\[[^\]]*\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================
# Wikipedia 缓存
# =========================
@lru_cache(maxsize=100)
def fetch_wiki(country):

    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"

    try:
        r = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        return BeautifulSoup(r.text, "html.parser")

    except:
        return None


# =========================
# 国家简介
# =========================
def get_country_info(country):

    soup = fetch_wiki(country)
    if not soup:
       return {
        "name": country,
        "intro": "Unavailable"
       }
    title = soup.find("h1")

    name = title.text.strip() if title else country

    intro = "No introduction found."

    for p in soup.find_all("p"):

        text = clean_text(
            p.get_text(" ", strip=True)
        )

        if len(text) > 80:
            intro = text
            break

    return {
        "name": name,
        "intro": intro
    }


# =========================
# 城市
# =========================
CITY_MAP = {

    "china": [
        "Beijing",
        "Shanghai",
        "Guangzhou",
        "Shenzhen"
    ],

    "japan": [
        "Tokyo",
        "Osaka",
        "Kyoto",
        "Yokohama"
    ],

    "usa": [
        "New York",
        "Los Angeles",
        "Chicago",
        "Houston"
    ],

    "us": [
        "New York",
        "Los Angeles",
        "Chicago",
        "Houston"
    ],

    "united states": [
        "New York",
        "Los Angeles",
        "Chicago",
        "Houston"
    ],

    "uk": [
        "London",
        "Manchester",
        "Birmingham",
        "Liverpool"
    ],

    "united kingdom": [
        "London",
        "Manchester",
        "Birmingham",
        "Liverpool"
    ],

    "canada": [
        "Toronto",
        "Vancouver",
        "Montreal",
        "Calgary"
    ],

    "australia": [
        "Sydney",
        "Melbourne",
        "Brisbane",
        "Perth"
    ]
}


def get_cities(country):
    return CITY_MAP.get(
        country.lower().strip(),
        []
    )


# =========================
# 物价数据库
# =========================
COST_DB = {

    "new york": [
        ("Meal", "$20"),
        ("Coffee", "$5"),
        ("Rent", "$3000")
    ],

    "los angeles": [
        ("Meal", "$18"),
        ("Coffee", "$5"),
        ("Rent", "$2600")
    ],

    "chicago": [
        ("Meal", "$16"),
        ("Coffee", "$4"),
        ("Rent", "$2100")
    ],

    "houston": [
        ("Meal", "$15"),
        ("Coffee", "$4"),
        ("Rent", "$1800")
    ],

    "london": [
        ("Meal", "£15"),
        ("Coffee", "£3"),
        ("Rent", "£2200")
    ],

    "manchester": [
        ("Meal", "£12"),
        ("Coffee", "£3"),
        ("Rent", "£1400")
    ],

    "birmingham": [
        ("Meal", "£11"),
        ("Coffee", "£3"),
        ("Rent", "£1300")
    ],

    "liverpool": [
        ("Meal", "£10"),
        ("Coffee", "£2"),
        ("Rent", "£1200")
    ],

    "tokyo": [
        ("Meal", "¥1000"),
        ("Coffee", "¥450"),
        ("Rent", "¥150000")
    ],

    "osaka": [
        ("Meal", "¥900"),
        ("Coffee", "¥400"),
        ("Rent", "¥110000")
    ],

    "kyoto": [
        ("Meal", "¥850"),
        ("Coffee", "¥380"),
        ("Rent", "¥100000")
    ],

    "yokohama": [
        ("Meal", "¥950"),
        ("Coffee", "¥420"),
        ("Rent", "¥120000")
    ],

    "beijing": [
        ("Meal", "¥35"),
        ("Coffee", "¥25"),
        ("Rent", "¥6000")
    ],

    "shanghai": [
        ("Meal", "¥40"),
        ("Coffee", "¥30"),
        ("Rent", "¥7500")
    ],

    "guangzhou": [
        ("Meal", "¥32"),
        ("Coffee", "¥24"),
        ("Rent", "¥5000")
    ],

    "shenzhen": [
        ("Meal", "¥38"),
        ("Coffee", "¥28"),
        ("Rent", "¥7000")
    ],

    "toronto": [
        ("Meal", "C$20"),
        ("Coffee", "C$5"),
        ("Rent", "C$2500")
    ],

    "vancouver": [
        ("Meal", "C$22"),
        ("Coffee", "C$5"),
        ("Rent", "C$2800")
    ],

    "montreal": [
        ("Meal", "C$18"),
        ("Coffee", "C$4"),
        ("Rent", "C$1700")
    ],

    "calgary": [
        ("Meal", "C$17"),
        ("Coffee", "C$4"),
        ("Rent", "C$1600")
    ],

    "sydney": [
        ("Meal", "A$25"),
        ("Coffee", "A$5"),
        ("Rent", "A$3200")
    ],

    "melbourne": [
        ("Meal", "A$23"),
        ("Coffee", "A$5"),
        ("Rent", "A$2800")
    ],

    "brisbane": [
        ("Meal", "A$21"),
        ("Coffee", "A$4"),
        ("Rent", "A$2400")
    ],

    "perth": [
        ("Meal", "A$20"),
        ("Coffee", "A$4"),
        ("Rent", "A$2300")
    ]
}


def get_cost(city):

    return [
        {
            "item": item,
            "price": price
        }
        for item, price
        in COST_DB.get(
            city.lower(),
            [("No data", "")]
        )
    ]


# =========================
# FOOD
# =========================
def get_foods(country):

    soup = fetch_wiki(country)

    if not soup:
        return ["Cuisine data not available"]

    foods = []

    for p in soup.find_all("p"):

        text = clean_text(p.get_text())

        if any(
            k in text.lower()
            for k in ["cuisine", "food", "dish"]
        ):

            if len(text) > 50:

                if len(text) > 500:
                    text = text[:500] + "..."

                foods.append(text)

        if len(foods) >= 3:
            break

    return foods if foods else ["Cuisine data not available"]


# =========================
# CLIMATE
# =========================
def get_climate_info(country):

    soup = fetch_wiki(country)

    if not soup:
        return "Unavailable"

    keywords = [
        "climate",
        "weather",
        "temperature",
        "rainfall",
        "season"
    ]

    result = []

    for p in soup.find_all("p"):

        text = clean_text(p.get_text())

        if any(k in text.lower() for k in keywords):
            result.append(text)

    climate = "\n\n".join(result)

    # 限制长度
    return (
        climate[:800] + "..."
        if len(climate) > 800
        else climate
) if climate else "No climate info"


# =========================
# API
# =========================
@app.route("/api/country/<country>")
def api_country(country):

    info = get_country_info(country)

    city_data = []

    for city in get_cities(country):

        city_data.append({
            "city": city,
            "cost": get_cost(city)
        })

    return jsonify({
        "country": info,
        "cities": city_data,
        "foods": get_foods(country),
        "climate": get_climate_info(country)
    })


# =========================
# 首页
# =========================
@app.route("/")
def home():
    return "Website Running OK"


# =========================
# 国家页面（Wix iframe）
# =========================
@app.route("/country-page/<country>")
def country_page(country):

    info = get_country_info(country)

    html = f"""
    <html>
    <head>
    <meta charset="utf-8">

    <script>
    function sendHeight() {{
        window.parent.postMessage({{
            type:'setHeight',
            height:document.body.scrollHeight + 50
        }}, '*');
    }}

    window.onload = function() {{
        sendHeight();
        setTimeout(sendHeight,500);
        setTimeout(sendHeight,1000);
        setTimeout(sendHeight,2000);
    }};
    </script>

    <style>
    body {{
        font-family:Arial;
        padding:20px;
        background:#f5f5f5;
    }}

    .box {{
        background:white;
        padding:15px;
        margin-top:15px;
        border-radius:10px;
    }}

    .city {{
        padding:10px;
        margin-top:10px;
        border-left:4px solid #3498db;
        background:white;
    }}
    </style>

    </head>
    <body>

    <h1>{info['name']}</h1>

    <div class="box">
    <h3>Introduction</h3>
    <p>{info['intro']}</p>
    </div>

    <div class="box">
    <h3>Cities & Cost</h3>
    """

    for city in get_cities(country):

        html += f"<div class='city'><h4>{city}</h4>"

        for item in get_cost(city):

            html += (
                f"<p>{item['item']} : "
                f"{item['price']}</p>"
            )

        html += "</div>"

    html += """
    </div>

    </body>
    </html>
    """

    return html


# =========================
# FOOD iframe
# =========================
@app.route("/food/<country>")
def food_page(country):

    foods = get_foods(country)

    html = """
    <html>
    <body style="font-family:Arial;padding:10px;">
    """

    for food in foods:
        html += f"<p>{food}</p>"

    html += """
    </body>
    </html>
    """

    return html


# =========================
# CLIMATE iframe
# =========================
@app.route("/climate/<country>")
def climate_page(country):

    climate = get_climate_info(country)

    return f"""
    <html>
    <body style="font-family:Arial;padding:10px;">
    {climate.replace(chr(10), "<br>")}
    </body>
    </html>
    """


# =========================
# Render
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
