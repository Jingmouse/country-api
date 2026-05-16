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
# 🌍 固定国家 + 城市
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
# 💰 物价
# =========================
def get_cost(city):

    url = f"https://www.numbeo.com/cost-of-living/in/{city.replace(' ', '-')}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.numbeo.com/"
    }

    try:
        r = requests.get(url, headers=headers, timeout=8)
    except:
        return [{"item": "No data", "price": "-"}]

    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table", class_="data_wide_table")

    items = []

    if table:
        for row in table.find_all("tr")[:6]:
            cols = row.find_all("td")
            if len(cols) >= 2:
                items.append({
                    "item": cols[0].get_text(strip=True),
                    "price": cols[1].get_text(strip=True)
                })

    if not items:
        return [{"item": "Data unavailable", "price": "-"}]

    return items


# =========================
# 🌍 页面（最终完整版）
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
                background: #fafafa;
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
                padding: 10px;
                border-left: 4px solid #3498db;
                background: white;
            }}
        </style>

        <!-- ⭐ 自动高度 -->
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
        <h2>🏙 Cities + Cost of Living</h2>
    """

    # =========================
    # 城市 + 物价
    # =========================
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
