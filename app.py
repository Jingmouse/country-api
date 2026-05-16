import requests
from bs4 import BeautifulSoup
from flask import Flask
import os

app = Flask(__name__)

# =========================
# 🌍 城市（稳定方案B）
# =========================
def get_cities(country):

    data = {
        "China": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen"],
        "Japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama"],
        "France": ["Paris", "Lyon", "Marseille", "Nice"],
        "United States": ["New-York", "Los-Angeles", "Chicago", "Houston"],
        "South Korea": ["Seoul", "Busan", "Incheon", "Daegu"],
        "United Kingdom": ["London", "Manchester", "Birmingham", "Liverpool"],
        "Germany": ["Berlin", "Munich", "Hamburg", "Frankfurt"],
        "Italy": ["Rome", "Milan", "Naples", "Florence"],
        "Spain": ["Madrid", "Barcelona", "Valencia", "Seville"],
        "Canada": ["Toronto", "Vancouver", "Montreal", "Calgary"]
    }

    cities = data.get(country.title().strip(), [])

    # 🛡️ 保底：绝不为空
    if not cities:
        cities = ["Capital City"]

    return cities


# =========================
# 💰 物价（安全版）
# =========================
def get_cost(city):

    url = f"https://www.numbeo.com/cost-of-living/in/{city}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=8)
    except:
        return [{"item": "Data unavailable", "price": "-"}]

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

    # 🛡️ 保底：避免空城市
    if not items:
        items = [{"item": "No data available", "price": "-"}]

    return items


# =========================
# 🌍 主页面（Wix iframe）
# =========================
@app.route("/country-page/<country>")
def country_page(country):

    cities = get_cities(country)

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>{country}</title>

        <style>
            body {{
                font-family: Arial;
                padding: 20px;
                background: #fafafa;
            }}

            h1 {{
                color: #2c3e50;
            }}

            .city {{
                margin-top: 15px;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 10px;
                background: white;
            }}

            .box {{
                margin-top: 20px;
                padding: 15px;
                border-radius: 10px;
                border: 1px solid #ccc;
                background: white;
            }}
        </style>

        <!-- ⭐ 自动高度系统 -->
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

    <h1>🌍 {country} Cost of Living</h1>

    <div class="box">
        <h2>🏙 Cities</h2>
    """

    # =========================
    # 城市循环（保证一定有）
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
