import requests
from bs4 import BeautifulSoup
from flask import Flask
import os
import re

app = Flask(__name__)

# =========================
# 清理 Wikipedia 引用 [1]
# =========================
def clean_text(text):
    return re.sub(r"\[\d+\]", "", text)


# =========================
# 首页
# =========================
@app.route("/")
def home():
    return "Website Running"


# =========================
# 国家简介
# =========================
def get_country_info(country):

    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
    except:
        return {"name": country, "intro": "Unavailable"}

    soup = BeautifulSoup(r.text, "html.parser")

    title = soup.find("h1")
    name = title.text.strip() if title else country

    intro = "Not found"

    for p in soup.find_all("p"):

        text = clean_text(p.get_text(" ", strip=True))

        if len(text) > 80:
            intro = text
            break

    return {"name": name, "intro": intro}


# =========================
# 城市列表
# =========================
def get_cities(country):

    data = {
        "china": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen"],
        "japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama"],
        "united states": ["New York", "Los Angeles", "Chicago", "Houston"],
        "united kingdom": ["London", "Manchester", "Birmingham", "Liverpool"],
        "canada": ["Toronto", "Vancouver", "Montreal", "Calgary"],
        "australia": ["Sydney", "Melbourne", "Brisbane", "Perth"]
    }

    return data.get(country.lower().strip(), [])


# =========================
# 物价（已修复 key 不匹配问题）
# =========================
def get_cost(city):

    sample = {
        "new york": [("Meal", "$20"), ("Coffee", "$5"), ("Rent", "$3000")],
        "los angeles": [("Meal", "$18"), ("Coffee", "$5"), ("Rent", "$2600")],
        "chicago": [("Meal", "$16"), ("Coffee", "$4"), ("Rent", "$2100")],
        "houston": [("Meal", "$15"), ("Coffee", "$4"), ("Rent", "$1800")],

        "london": [("Meal", "£15"), ("Coffee", "£3"), ("Rent", "£2200")],
        "manchester": [("Meal", "£12"), ("Coffee", "£3"), ("Rent", "£1400")],
        "birmingham": [("Meal", "£11"), ("Coffee", "£3"), ("Rent", "£1300")],
        "liverpool": [("Meal", "£10"), ("Coffee", "£2"), ("Rent", "£1200")],

        "tokyo": [("Meal", "¥1000"), ("Coffee", "¥450"), ("Rent", "¥150000")],
        "osaka": [("Meal", "¥900"), ("Coffee", "¥400"), ("Rent", "¥110000")],
        "kyoto": [("Meal", "¥850"), ("Coffee", "¥380"), ("Rent", "¥100000")],
        "yokohama": [("Meal", "¥950"), ("Coffee", "¥420"), ("Rent", "¥120000")],

        "beijing": [("Meal", "¥35"), ("Coffee", "¥25"), ("Rent", "¥6000")],
        "shanghai": [("Meal", "¥40"), ("Coffee", "¥30"), ("Rent", "¥7500")],
        "guangzhou": [("Meal", "¥32"), ("Coffee", "¥24"), ("Rent", "¥5000")],
        "shenzhen": [("Meal", "¥38"), ("Coffee", "¥28"), ("Rent", "¥7000")],

        "toronto": [("Meal", "C$20"), ("Coffee", "C$5"), ("Rent", "C$2500")],
        "vancouver": [("Meal", "C$22"), ("Coffee", "C$5"), ("Rent", "C$2800")],
        "montreal": [("Meal", "C$18"), ("Coffee", "C$4"), ("Rent", "C$1700")],
        "calgary": [("Meal", "C$17"), ("Coffee", "C$4"), ("Rent", "C$1600")],

        "sydney": [("Meal", "A$25"), ("Coffee", "A$5"), ("Rent", "A$3200")],
        "melbourne": [("Meal", "A$23"), ("Coffee", "A$5"), ("Rent", "A$2800")],
        "brisbane": [("Meal", "A$21"), ("Coffee", "A$4"), ("Rent", "A$2400")],
        "perth": [("Meal", "A$20"), ("Coffee", "A$4"), ("Rent", "A$2300")]
    }

    key = city.lower().strip()

    return [
        {"item": k, "price": v}
        for k, v in sample.get(key, [("No data", "")])
    ]


# =========================
# FOOD（稳定版）
# =========================
def get_foods(country):

    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}_(cuisine)"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
    except:
        return ["Food unavailable"]

    if r.status_code != 200:
        return ["Food page not found"]

    soup = BeautifulSoup(r.text, "html.parser")

    foods = []

    for li in soup.find_all("li"):

        text = clean_text(li.get_text(" ", strip=True))

        if 2 < len(text) < 60:
            foods.append(text)

    foods = list(dict.fromkeys(foods))

    return foods[:12] if foods else ["No food data"]


# =========================
# CLIMATE（稳定版）
# =========================
def get_climate_info(country):

    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
    except:
        return "Unavailable"

    soup = BeautifulSoup(r.text, "html.parser")

    keywords = [
        "climate", "temperature", "rainfall",
        "weather", "season", "winter",
        "summer", "storm", "snow"
    ]

    result = ""

    for p in soup.find_all("p"):

        text = clean_text(p.get_text())

        if any(k in text.lower() for k in keywords):
            result += text + "\n\n"

    return result[:4000] if result else "No climate info"


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

    # =========================
    # ✅ 关键修复点（循环标准化）
    # =========================
    for city in cities:

        city_key = city.lower().strip()

        html += f"<div class='city'><h4>{city}</h4>"

        costs = get_cost(city_key)

        for item in costs:
            html += f"<p>{item['item']} : {item['price']}</p>"

        html += "</div>"

    html += """
</div>

</body>
</html>
"""

    return html


# =========================
# FOOD iframe page
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
    font-family: Arial;
    background: transparent;
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
# CLIMATE iframe page
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
    font-family: Arial;
    background: transparent;
}}

body {{
    padding: 6px;
}}

.item {{
    padding: 10px;
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
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
