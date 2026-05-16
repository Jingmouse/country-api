import requests
from bs4 import BeautifulSoup
from flask import Flask
import os

app = Flask(__name__)

# =========================
# 国家简介（Wikipedia）
# =========================
def get_country_info(country):

    country = country.strip().replace(" ", "_")

    url = f"https://en.wikipedia.org/wiki/{country}"

    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
    except:
        return {
            "name": country,
            "intro": "Request failed"
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
# 城市列表
# =========================
def get_cities(country):

    cities_map = {
        "China": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen"],
        "Japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama"],
        "France": ["Paris", "Lyon", "Marseille", "Nice"],
        "United States": ["New-York", "Los-Angeles", "Chicago", "Houston"],
        "South Korea": ["Seoul", "Busan", "Incheon", "Daegu"],
        "United Kingdom": ["London", "Manchester", "Birmingham", "Liverpool"]
    }

    return cities_map.get(country.title().strip(), [])


# =========================
# 物价
# =========================
def get_cost(city):

    url = f"https://www.numbeo.com/cost-of-living/in/{city}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=8)
    except:
        return []

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

    return items


# =========================
# 🌍 页面（最终合并版）
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
            }}
            .box {{
                margin-top: 20px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 10px;
            }}
            .city {{
                margin-top: 15px;
                padding: 10px;
                border-left: 4px solid #3498db;
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
        <h2>💰 Cost of Living</h2>
    """

    if not cities:
        html += "<p>Country not supported</p>"

    for city in cities:

        html += f"<div class='city'><h3>{city}</h3>"

        items = get_cost(city)

        if not items:
            html += "<p>No data</p>"
        else:
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
# Render启动
# =========================
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
