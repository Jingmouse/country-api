import requests
from bs4 import BeautifulSoup
from flask import Flask
import os

app = Flask(__name__)

# =========================
# 首页（避免404）
# =========================
@app.route("/")
def home():
    return "Country Website Running"


# =========================
# 国家简介
# =========================
def get_country_info(country):

    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
    except:
        return {"name": country, "intro": "Information unavailable"}

    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("h1")
    name = title.text.strip() if title else country

    intro = "Not found"

    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        if len(text) > 80:
            intro = text
            break

    return {"name": name, "intro": intro}


# =========================
# 城市
# =========================
def get_cities(country):

    country = country.strip().lower()

    data = {
        "united states": ["New York", "Los Angeles", "Chicago", "Houston"],
        "united kingdom": ["London", "Manchester", "Birmingham", "Liverpool"],
        "australia": ["Sydney", "Melbourne", "Brisbane", "Perth"],
        "china": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen"],
        "japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama"],
        "canada": ["Toronto", "Vancouver", "Montreal", "Calgary"]
    }

    return data.get(country, [])


# =========================
# 物价
# =========================
def get_cost(city):

    sample = {
        "New York": [("Meal", "$20"), ("Coffee", "$5"), ("Rent", "$3000")],
        "Los Angeles": [("Meal", "$18"), ("Coffee", "$5"), ("Rent", "$2700")],
        "Chicago": [("Meal", "$16"), ("Coffee", "$4"), ("Rent", "$2200")],
        "Houston": [("Meal", "$15"), ("Coffee", "$4"), ("Rent", "$1800")],

        "London": [("Meal", "£15"), ("Coffee", "£3"), ("Rent", "£2200")],
        "Manchester": [("Meal", "£12"), ("Coffee", "£3"), ("Rent", "£1400")],
        "Birmingham": [("Meal", "£11"), ("Coffee", "£3"), ("Rent", "£1300")],
        "Liverpool": [("Meal", "£10"), ("Coffee", "£2"), ("Rent", "£1100")],

        "Tokyo": [("Meal", "¥1000"), ("Coffee", "¥450"), ("Rent", "¥150000")],
        "Osaka": [("Meal", "¥900"), ("Coffee", "¥400"), ("Rent", "¥120000")],
        "Kyoto": [("Meal", "¥850"), ("Coffee", "¥400"), ("Rent", "¥100000")],
        "Yokohama": [("Meal", "¥950"), ("Coffee", "¥430"), ("Rent", "¥130000")],

        "Beijing": [("Meal", "¥35"), ("Coffee", "¥25"), ("Rent", "¥6000")],
        "Shanghai": [("Meal", "¥40"), ("Coffee", "¥30"), ("Rent", "¥8000")],
        "Guangzhou": [("Meal", "¥30"), ("Coffee", "¥22"), ("Rent", "¥5000")],
        "Shenzhen": [("Meal", "¥38"), ("Coffee", "¥28"), ("Rent", "¥7500")],

        "Sydney": [("Meal", "A$25"), ("Coffee", "A$5"), ("Rent", "A$2800")],
        "Melbourne": [("Meal", "A$22"), ("Coffee", "A$5"), ("Rent", "A$2400")],
        "Brisbane": [("Meal", "A$20"), ("Coffee", "A$4"), ("Rent", "A$2100")],
        "Perth": [("Meal", "A$21"), ("Coffee", "A$4"), ("Rent", "A$2200")],

        "Toronto": [("Meal", "C$20"), ("Coffee", "C$5"), ("Rent", "C$2500")],
        "Vancouver": [("Meal", "C$22"), ("Coffee", "C$5"), ("Rent", "C$2700")],
        "Montreal": [("Meal", "C$18"), ("Coffee", "C$4"), ("Rent", "C$1800")],
        "Calgary": [("Meal", "C$17"), ("Coffee", "C$4"), ("Rent", "C$1700")]
    }

    if city in sample:
        return [{"item": k, "price": v} for k, v in sample[city]]

    return [{"item": "Data", "price": "Not available"}]


# =========================
# 食物爬虫
# =========================
def get_foods(country):

    country = country.lower().strip()

    url = f"https://10dishes.com/{country}/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=8)
    except:
        return ["Food data unavailable"]

    if r.status_code != 200:
        return ["Food not found"]

    soup = BeautifulSoup(r.text, "html.parser")

    dishes = soup.find_all("h2")

    foods = []

    for d in dishes:
        name = d.get_text(strip=True)
        n = name.lower()

        if (
            "menu" in n or
            "national anthem" in n or
            "key flavors" in n or
            "cooking methods" in n or
            "regional variations" in n
        ):
            continue

        foods.append(name)

    return foods[:10] if foods else ["No data"]


# =========================
# 国家页面
# =========================
@app.route("/country-page/<country>")
def country_page(country):

    info = get_country_info(country)
    cities = get_cities(country)

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>{info['name']}</title>

        <style>
            body {{
                font-family: Arial;
                padding: 20px;
                background: #f5f5f5;
            }}

            h1 {{
                color: #2c3e50;
            }}

            .box {{
                margin-top: 20px;
                padding: 15px;
                background: white;
                border-radius: 10px;
            }}

            .city {{
                margin-top: 10px;
                padding: 10px;
                border-left: 4px solid #3498db;
                background: white;
            }}
        </style>

        <script>
        function sendHeight() {{
            window.parent.postMessage({{
                type: "setHeight",
                height: document.body.scrollHeight
            }}, "*");
        }}

        window.onload = sendHeight;
        window.onresize = sendHeight;
        setTimeout(sendHeight, 800);
        </script>

    </head>

    <body>

    <h1>{info['name']}</h1>

    <div class="box">
        <h2>Introduction</h2>
        <p>{info['intro']}</p>
    </div>

    <div class="box">
        <h2>Cities & Living Cost</h2>
    """

    for city in cities:
        html += f"<div class='city'><h3>{city}</h3>"
        for item in get_cost(city):
            html += f"<p>{item['item']} : {item['price']}</p>"
        html += "</div>"

    html += "</div></body></html>"

    return html


# =========================
# 食物独立页面（重点）
# =========================
@app.route("/food/<country>")
def food_page(country):

    foods = get_foods(country)

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Food</title>

        <style>
            body {{
                font-family: Arial;
                padding: 20px;
                background: #f5f5f5;
            }}

            .box {{
                background: white;
                padding: 20px;
                border-radius: 10px;
            }}

            .item {{
                margin-top: 10px;
                padding: 12px;
                border-left: 4px solid #e67e22;
                background: #fafafa;
            }}
        </style>

        <script>
        function sendHeight() {{
            window.parent.postMessage({{
                type: "setHeight",
                height: document.body.scrollHeight
            }}, "*");
        }}

        window.onload = sendHeight;
        setTimeout(sendHeight, 800);
        </script>

    </head>

    <body>

    <div class="box">
        <h2>Famous Food</h2>
    """

    for food in foods:
        html += f"<div class='item'>{food}</div>"

    html += "</div></body></html>"

    return html


# =========================
# Run
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
