import requests
from bs4 import BeautifulSoup
from flask import Flask
import os

app = Flask(__name__)

# =========================
# 首页
# =========================
@app.route("/")
def home():
    return "Website Running"


# =========================
# 国家信息
# =========================
def get_country_info(country):

    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)

    except:
        return {
            "name": country,
            "intro": "Unavailable"
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
# 城市
# =========================
def get_cities(country):

    data = {

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

    return data.get(country.lower().strip(), [])


# =========================
# 物价
# =========================
def get_cost(city):

    sample = {

        "New York": [
            ("Meal", "$20"),
            ("Coffee", "$5"),
            ("Rent", "$3000")
        ],

        "London": [
            ("Meal", "£15"),
            ("Coffee", "£3"),
            ("Rent", "£2200")
        ],

        "Tokyo": [
            ("Meal", "¥1000"),
            ("Coffee", "¥450"),
            ("Rent", "¥150000")
        ],

        "Beijing": [
            ("Meal", "¥35"),
            ("Coffee", "¥25"),
            ("Rent", "¥6000")
        ]
    }

    return [
        {"item": k, "price": v}
        for k, v in sample.get(city, [("No data", "")])
    ]


# =========================
# 食物爬虫
# =========================
def get_foods(country):

    country = country.lower().strip().replace(" ", "-")

    url = f"https://10dishes.com/{country}/"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        r = requests.get(url, headers=headers, timeout=10)

    except:

        return ["Food unavailable"]

    if r.status_code != 200:

        return ["Food not found"]

    soup = BeautifulSoup(r.text, "html.parser")

    elements = soup.select(
        "h2, h3, li, article h2, article h3"
    )

    foods = []

    for e in elements:

        text = e.get_text(strip=True)

        t = text.lower()

        if any(x in t for x in [
            "menu",
            "national anthem",
            "key flavors",
            "cooking methods",
            "regional variations",
            "introduction",
            "about"
        ]):
            continue

        if len(text) > 2:
            foods.append(text)

    foods = list(dict.fromkeys(foods))

    return foods[:10] if foods else ["No food data"]


# =========================
# Climate Spider
# =========================
def get_climate_info(country):

    country_url = country.replace(" ", "_")

    url = f"https://en.wikipedia.org/wiki/{country_url}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:

        response = requests.get(url, headers=headers)

    except:

        return "Climate information unavailable."

    if response.status_code != 200:

        return "Climate page not found."

    soup = BeautifulSoup(response.text, "html.parser")

    paragraphs = soup.find_all("p")

    keywords = [
        "climate",
        "temperature",
        "rainfall",
        "weather",
        "season",
        "winter",
        "summer",
        "storm",
        "snow"
    ]

    climate_text = ""

    for p in paragraphs:

        text = p.get_text().strip()

        if any(word in text.lower() for word in keywords):

            climate_text += text + "\n\n"

    if climate_text == "":

        climate_text = "No climate information found."

    return climate_text[:4000]


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

<style>

body {{
    font-family: Arial;
    padding: 20px;
    background: #f5f5f5;
}}

.box {{
    background: white;
    padding: 15px;
    margin-top: 15px;
    border-radius: 10px;
}}

.city {{
    padding: 10px;
    margin-top: 10px;
    border-left: 4px solid #3498db;
    background: white;
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

    for city in cities:

        html += f"<div class='city'><h4>{city}</h4>"

        for item in get_cost(city):

            html += f"<p>{item['item']} : {item['price']}</p>"

        html += "</div>"

    html += """

</div>

</body>
</html>

"""

    return html


# =========================
# Food Page
# =========================
@app.route("/food/<country>")
def food_page(country):

    foods = get_foods(country)

    html = """

<html>

<head>

<meta charset="utf-8">

<style>

html, body {
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: transparent;
    font-family: Arial;
}

body {
    padding: 6px;
}

.item {
    padding: 10px;
    margin-bottom: 6px;
    border-left: 3px solid #e67e22;
}

</style>

<script>

function sendHeight() {

    window.parent.postMessage({
        type: "setHeight",
        height: document.body.scrollHeight
    }, "*");
}

window.onload = sendHeight;

setTimeout(sendHeight, 300);

</script>

</head>

<body>

"""

    for food in foods:

        html += f"<div class='item'>{food}</div>"

    html += """

</body>
</html>

"""

    return html


# =========================
# Climate Page
# =========================
@app.route("/climate/<country>")
def climate_page(country):

    climate = get_climate_info(country)

    html = f"""

<html>

<head>

<meta charset="utf-8">

<style>

html, body {{
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: transparent;
    font-family: Arial;
}}

body {{
    padding: 6px;
}}

.item {{
    padding: 10px;
    margin-bottom: 8px;
    border-left: 3px solid #3498db;
    line-height: 1.6;
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

setTimeout(sendHeight, 300);

</script>

</head>

<body>

<div class="item">

{climate.replace(chr(10), "<br>")}

</div>

</body>
</html>

"""

    return html


# =========================
# Run
# =========================
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
