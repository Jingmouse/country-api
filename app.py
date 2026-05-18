import requests
from bs4 import BeautifulSoup
from flask import Flask
import os
import re

app = Flask(__name__)

# =========================
# ⭐ 超强清理（彻底去除所有 [xxx]）
# =========================
def clean_text(text):

    # 删除所有 [xxx]（数字/字母/句子全部支持）
    text = re.sub(r"\[[^\]]*\]", "", text)

    # 删除多余空格
    text = re.sub(r"\s+", " ", text)

    return text.strip()


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

    intro = "No introduction found."

    for p in soup.find_all("p"):
        text = clean_text(p.get_text(" ", strip=True))
        if len(text) > 80:
            intro = text
            break

    return {"name": name, "intro": intro}


# =========================
# 城市（稳定）
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
# 物价（稳定）
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
# FOOD（DBpedia + fallback）
# =========================
def get_foods(country):

    foods = []

    # -------------------------
    # DBpedia（主数据源）
    # -------------------------
    endpoint = "https://dbpedia.org/sparql"

    query = f"""
    SELECT DISTINCT ?foodLabel WHERE {{
      ?country rdfs:label "{country}"@en.
      ?country dbo:cuisine ?food.
      ?food rdfs:label ?foodLabel.
      FILTER (lang(?foodLabel) = "en")
    }}
    LIMIT 10
    """

    try:
        r = requests.get(
            endpoint,
            params={"query": query, "format": "json"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10
        )

        data = r.json()

        for item in data["results"]["bindings"]:
            foods.append(item["foodLabel"]["value"])

    except:
        pass

    # -------------------------
    # Wikipedia fallback
    # -------------------------
    if not foods:

        url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"

        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")

            content = soup.find("div", class_="mw-parser-output")

            if content:
                for p in content.find_all("p"):
                    text = clean_text(p.get_text())

                    if any(k in text.lower() for k in ["cuisine", "food", "dish"]):
                        if len(text) > 30:
                            foods.append(text)

        except:
            pass

    # -------------------------
    # final fallback
    # -------------------------
    if not foods:
        foods = ["Cuisine data not available"]

    return foods[:10]


# =========================
# CLIMATE
# =========================
def get_climate_info(country):

    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
    except:
        return "Unavailable"

    soup = BeautifulSoup(r.text, "html.parser")

    keywords = ["climate", "weather", "temperature", "rainfall", "season"]

    result = ""

    for p in soup.find_all("p"):
        text = clean_text(p.get_text())

        if any(k in text.lower() for k in keywords):
            result += text + "\n\n"

    return result[:4000] if result else "No climate info"


# =========================
# COUNTRY PAGE
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

        for item in get_cost(city.lower()):
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
}

body {
    padding: 8px;
}

.item {
    padding: 10px;
    margin-bottom: 6px;
    border-left: 3px solid #e67e22;
    background: #fafafa;
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

    return f"""
<html>
<head>
<meta charset="utf-8">

<style>
html, body {{
    margin: 0;
    padding: 0;
    overflow: hidden;
    font-family: Arial;
}}

body {{
    padding: 8px;
}}

.item {{
    padding: 10px;
    border-left: 3px solid #3498db;
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


# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
