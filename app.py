import requests
from bs4 import BeautifulSoup
from flask import Flask
import os

app = Flask(__name__)

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

    data = {
        "United States": ["New York", "Los Angeles", "Chicago", "Houston"],
        "United Kingdom": ["London", "Manchester", "Birmingham", "Liverpool"],
        "Australia": ["Sydney", "Melbourne", "Brisbane", "Perth"],
        "China": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen"],
        "Japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama"],
        "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary"]
    }

    return data.get(country.title().strip(), [])


# =========================
# 物价
# =========================
def get_cost(city):

    sample = {
        "New York": [("Meal", "$20"), ("Coffee", "$5"), ("Rent", "$3000")],
        "London": [("Meal", "£15"), ("Coffee", "£3"), ("Rent", "£2200")],
        "Tokyo": [("Meal", "¥1000"), ("Coffee", "¥450"), ("Rent", "¥150000")],
        "Beijing": [("Meal", "¥35"), ("Coffee", "¥25"), ("Rent", "¥6000")]
    }

    if city in sample:
        return [{"item": k, "price": v} for k, v in sample[city]]

    return [{"item": "Data", "price": "Not available"}]


# =========================
# 食物（独立模块）
# =========================
def get_foods(country):

    country = country.lower().strip().replace(" ", "-")
    url = f"https://10dishes.com/{country}/"

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=8)
    except:
        return ["Food data unavailable"]

    if r.status_code != 200:
        return ["Food data not found"]

    soup = BeautifulSoup(r.text, "html.parser")

    dishes = soup.find_all("h2")

    foods = []

    for d in dishes:
        name = d.get_text(strip=True)
        name_low = name.lower()

        if (
            "menu" in name_low or
            "national anthem" in name_low or
            "key flavors" in name_low or
            "cooking methods" in name_low or
            "regional variations" in name_low
        ):
            continue

        if len(name) > 2:
            foods.append(name)

    return foods[:10] if foods else ["No data"]


# =========================
# 页面
# =========================
@app.route("/country-page/<country>")
def country_page(country):

    info = get_country_info(country)
    cities = get_cities(country)
    foods = get_foods(country)

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
                border: 1px solid #ddd;
            }}

            .city {{
                margin-top: 10px;
                padding: 10px;
                border-left: 4px solid #3498db;
                background: white;
            }}

            .food-box {{
                margin-top: 20px;
                padding: 15px;
                background: white;
                border-radius: 10px;
                border-left: 5px solid #e67e22;
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

    # 城市
    for city in cities:

        html += f"<div class='city'><h3>{city}</h3>"

        for item in get_cost(city):
            html += f"<p>{item['item']} : {item['price']}</p>"

        html += "</div>"

    html += "</div>"

    # 食物（独立框）
    html += """
    <div class="food-box">
        <h2>Famous Food</h2>
    """

    for food in foods:
        html += f"<p>{food}</p>"

    html += """
    </div>

    </body>
    </html>
    """

    return html


# =========================
# Run (Render)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
