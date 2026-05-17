import requests
from bs4 import BeautifulSoup
from flask import Flask
import os
import re

app = Flask(__name__)

# =========================
# 清理 [1] 引用
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
# 城市（固定稳定）
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
        "london": [("Meal", "£15"), ("Coffee", "£3"), ("Rent", "£2200")],
        "tokyo": [("Meal", "¥1000"), ("Coffee", "¥450"), ("Rent", "¥150000")],
        "beijing": [("Meal", "¥35"), ("Coffee", "¥25"), ("Rent", "¥6000")],
        "toronto": [("Meal", "C$20"), ("Coffee", "C$5"), ("Rent", "C$2500")],
        "sydney": [("Meal", "A$25"), ("Coffee", "A$5"), ("Rent", "A$3200")]
    }

    return [{"item": k, "price": v} for k, v in sample.get(city.lower(), [("No data", "")])]


# =========================
# FOOD（DBpedia + fallback ✔）
# =========================
def get_foods(country):

    foods = []

    # =========================
    # 1. DBpedia（核心）
    # =========================
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

    # =========================
    # 2. fallback Wikipedia
    # =========================
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

    # =========================
    # 3. still empty fallback
    # =========================
    if not foods:
        foods = ["Cuisine data not available"]

    return foods[:10]


# =========================
# CLIMATE（稳定）
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
