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
# 🌍 国家 + 城市（完全稳定）
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
# 💰 物价（稳定数据层：替代Numbeo）
# =========================
def get_cost(city):

    # ✔ 稳定示例数据（可后期扩展/替换为API）
    sample = {
        "New York": [
            ("Meal (cheap restaurant)", "$20"),
            ("Coffee", "$5"),
            ("Rent (1 bedroom)", "$3000")
        ],
        "London": [
            ("Meal (cheap restaurant)", "£15"),
            ("Coffee", "£3"),
            ("Rent (1 bedroom)", "£2200")
        ],
        "Tokyo": [
            ("Meal (cheap restaurant)", "¥1000"),
            ("Coffee", "¥450"),
            ("Rent (1 bedroom)", "¥150000")
        ],
        "Beijing": [
            ("Meal (cheap restaurant)", "¥35"),
            ("Coffee", "¥25"),
            ("Rent (1 bedroom)", "¥6000")
        ]
    }

    if city in sample:
        return [{"item": k, "price": v} for k, v in sample[city]]

    # fallback（保证永远有内容）
    return [
        {"item": "Living Cost Data", "price": "Available soon"},
        {"item": "Food", "price": "N/A"},
        {"item": "Rent", "price": "N/A"}
    ]


# =========================
# 🌍 页面
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
# 🚀 Render
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
