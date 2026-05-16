import requests
from bs4 import BeautifulSoup
from flask import Flask
import os

app = Flask(__name__)

# =========================
# 首页（防止 Render 404）
# =========================
@app.route("/")
def home():
    return "Country Website Running"


# =========================
# 国家简介（Wikipedia）
# =========================
def get_country_info(country):

    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(
            url,
            headers=headers,
            timeout=10
        )

    except:
        return {
            "name": country,
            "intro": "Information unavailable"
        }

    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("h1")

    name = title.text.strip() if title else country

    intro = "Not found"

    for p in soup.find_all("p"):

        text = p.get_text(" ", strip=True)

        if len(text) > 80:
            intro = text
            break

    return {
        "name": name,
        "intro": intro
    }


# =========================
# 国家 + 城市
# =========================
def get_cities(country):

    country = country.strip().lower()

    data = {

        "united states": [
            "New York",
            "Los Angeles",
            "Chicago",
            "Houston"
        ],

        "united kingdom": [
            "London",
            "Manchester",
            "Birmingham",
            "Liverpool"
        ],

        "australia": [
            "Sydney",
            "Melbourne",
            "Brisbane",
            "Perth"
        ],

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

        "canada": [
            "Toronto",
            "Vancouver",
            "Montreal",
            "Calgary"
        ]
    }

    return data.get(country, [])


# =========================
# 物价
# =========================
def get_cost(city):

    sample = {

        "New York": [
            ("Meal (cheap restaurant)", "$20"),
            ("Coffee", "$5"),
            ("Rent (1 bedroom)", "$3000")
        ],

        "Los Angeles": [
            ("Meal (cheap restaurant)", "$18"),
            ("Coffee", "$5"),
            ("Rent (1 bedroom)", "$2700")
        ],

        "Chicago": [
            ("Meal (cheap restaurant)", "$16"),
            ("Coffee", "$4"),
            ("Rent (1 bedroom)", "$2200")
        ],

        "Houston": [
            ("Meal (cheap restaurant)", "$15"),
            ("Coffee", "$4"),
            ("Rent (1 bedroom)", "$1800")
        ],

        "London": [
            ("Meal (cheap restaurant)", "£15"),
            ("Coffee", "£3"),
            ("Rent (1 bedroom)", "£2200")
        ],

        "Manchester": [
            ("Meal (cheap restaurant)", "£12"),
            ("Coffee", "£3"),
            ("Rent (1 bedroom)", "£1400")
        ],

        "Birmingham": [
            ("Meal (cheap restaurant)", "£11"),
            ("Coffee", "£3"),
            ("Rent (1 bedroom)", "£1300")
        ],

        "Liverpool": [
            ("Meal (cheap restaurant)", "£10"),
            ("Coffee", "£2"),
            ("Rent (1 bedroom)", "£1100")
        ],

        "Tokyo": [
            ("Meal (cheap restaurant)", "¥1000"),
            ("Coffee", "¥450"),
            ("Rent (1 bedroom)", "¥150000")
        ],

        "Osaka": [
            ("Meal (cheap restaurant)", "¥900"),
            ("Coffee", "¥400"),
            ("Rent (1 bedroom)", "¥120000")
        ],

        "Kyoto": [
            ("Meal (cheap restaurant)", "¥850"),
            ("Coffee", "¥400"),
            ("Rent (1 bedroom)", "¥100000")
        ],

        "Yokohama": [
            ("Meal (cheap restaurant)", "¥950"),
            ("Coffee", "¥430"),
            ("Rent (1 bedroom)", "¥130000")
        ],

        "Beijing": [
            ("Meal (cheap restaurant)", "¥35"),
            ("Coffee", "¥25"),
            ("Rent (1 bedroom)", "¥6000")
        ],

        "Shanghai": [
            ("Meal (cheap restaurant)", "¥40"),
            ("Coffee", "¥30"),
            ("Rent (1 bedroom)", "¥8000")
        ],

        "Guangzhou": [
            ("Meal (cheap restaurant)", "¥30"),
            ("Coffee", "¥22"),
            ("Rent (1 bedroom)", "¥5000")
        ],

        "Shenzhen": [
            ("Meal (cheap restaurant)", "¥38"),
            ("Coffee", "¥28"),
            ("Rent (1 bedroom)", "¥7500")
        ],

        "Sydney": [
            ("Meal (cheap restaurant)", "A$25"),
            ("Coffee", "A$5"),
            ("Rent (1 bedroom)", "A$2800")
        ],

        "Melbourne": [
            ("Meal (cheap restaurant)", "A$22"),
            ("Coffee", "A$5"),
            ("Rent (1 bedroom)", "A$2400")
        ],

        "Brisbane": [
            ("Meal (cheap restaurant)", "A$20"),
            ("Coffee", "A$4"),
            ("Rent (1 bedroom)", "A$2100")
        ],

        "Perth": [
            ("Meal (cheap restaurant)", "A$21"),
            ("Coffee", "A$4"),
            ("Rent (1 bedroom)", "A$2200")
        ],

        "Toronto": [
            ("Meal (cheap restaurant)", "C$20"),
            ("Coffee", "C$5"),
            ("Rent (1 bedroom)", "C$2500")
        ],

        "Vancouver": [
            ("Meal (cheap restaurant)", "C$22"),
            ("Coffee", "C$5"),
            ("Rent (1 bedroom)", "C$2700")
        ],

        "Montreal": [
            ("Meal (cheap restaurant)", "C$18"),
            ("Coffee", "C$4"),
            ("Rent (1 bedroom)", "C$1800")
        ],

        "Calgary": [
            ("Meal (cheap restaurant)", "C$17"),
            ("Coffee", "C$4"),
            ("Rent (1 bedroom)", "C$1700")
        ]
    }

    if city in sample:

        return [
            {"item": k, "price": v}
            for k, v in sample[city]
        ]

    return [
        {"item": "Living Cost Data", "price": "Available soon"},
        {"item": "Food", "price": "N/A"},
        {"item": "Rent", "price": "N/A"}
    ]


# =========================
# 页面
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
                margin-top: 15px;
                padding: 10px;
                border-left: 4px solid #3498db;
                background: white;
            }}

        </style>

        <script>

        function sendHeight() {{

            const height = document.body.scrollHeight;

            window.parent.postMessage({{
                type: "setHeight",
                height: height
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

        html += f"""

        <div class='city'>

            <h3>{city}</h3>
        """

        items = get_cost(city)

        for item in items:

            html += f"""

            <p>{item['item']} : {item['price']}</p>
            """

        html += "</div>"

    html += """

    </div>

    </body>

    </html>
    """

    return html


# =========================
# Render
# =========================
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
