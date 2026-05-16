import requests
from bs4 import BeautifulSoup
from flask import Flask
import os

app = Flask(__name__)

# =========================
# 📘 国家简介（Wikipedia）
# =========================
def get_country_info(country):

    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
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
# 🌍 国家 + 城市
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
# 💰 完整物价体系（核心升级）
# =========================
def get_cost(city):

    return [
        {"item": "🍔 Meal at Inexpensive Restaurant", "price": "varies"},
        {"item": "🍟 Fast Food Combo Meal", "price": "varies"},
        {"item": "☕ Cappuccino (regular)", "price": "varies"},
        {"item": "🥛 Milk (1L)", "price": "varies"},
        {"item": "🍞 Bread (500g)", "price": "varies"},
        {"item": "🍚 Rice (1kg)", "price": "varies"},
        {"item": "🥚 Eggs (12)", "price": "varies"},
        {"item": "🍎 Apples (1kg)", "price": "varies"},
        {"item": "🚕 Taxi (1 km)", "price": "varies"},
        {"item": "🚇 Public Transport Ticket", "price": "varies"},
        {"item": "⛽ Gasoline (1L)", "price": "varies"},
        {"item": "🏠 Rent (1 bedroom city center)", "price": "varies"},
        {"item": "🏠 Rent (1 bedroom outside center)", "price": "varies"},
        {"item": "💡 Utilities (monthly)", "price": "varies"},
        {"item": "📶 Internet (monthly)", "price": "varies"},
        {"item": "👕 Jeans (Levis or similar)", "price": "varies"},
        {"item": "👟 Sneakers (Nike or similar)", "price": "varies"}
    ]


# =========================
# 🌍 页面（Wix友好版）
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
                border: 1px solid #ddd;
            }}

            .city {{
                margin-top: 15px;
                padding: 12px;
                border-left: 4px solid #3498db;
                background: white;
            }}
        </style>

        <!-- ⭐ Wix 自动高度 -->
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

    <h1>🌍 {info['name']}</h1>

    <div class="box">
        <h2>📘 Introduction</h2>
        <p>{info['intro']}</p>
    </div>

    <div class="box">
        <h2>🏙 Cities & Cost of Living</h2>
    """

    for city in cities:

        html += f"<div class='city'><h3>{city}</h3>"

        items = get_cost(city)

        for item in items:
            html += f"<p>{item['item']} : {item['price']}</p>"

        html += "</div>"

    html += """
    </div>
    </body>
    </html>
    """

    return html


# =========================
# 🚀 Render启动
# =========================
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
