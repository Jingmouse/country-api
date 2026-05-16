import requests
from bs4 import BeautifulSoup
from flask import Flask
import os

app = Flask(__name__)

# =========================
# 🌍 自动获取城市（通用版）
# =========================
def get_cities(country):

    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
    except:
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    infobox = soup.find("table", class_=lambda x: x and "infobox" in x)

    cities = []

    if infobox:

        for row in infobox.find_all("tr"):

            th = row.find("th")
            td = row.find("td")

            if th and td:

                key = th.text.lower()
                value = td.get_text(" ", strip=True)

                # 首都
                if "capital" in key:
                    cities.append(value.split(",")[0])

                # 最大城市
                if "largest city" in key:
                    cities.append(value.split(",")[0])

    # 去重
    return list(dict.fromkeys(cities))


# =========================
# 💰 获取物价
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
# 🌍 主页面（Wix嵌入版）
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
            }}
            h1 {{
                color: #2c3e50;
            }}
            .city {{
                margin-top: 15px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 8px;
            }}
            .box {{
                margin-top: 20px;
                padding: 15px;
                border-radius: 10px;
                border: 1px solid #ccc;
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
    # 城市 + 物价
    # =========================
    if not cities:
        html += "<p>No cities found</p>"

    for city in cities:

        html += f"<div class='city'><h3>{city}</h3>"

        items = get_cost(city)

        if not items:
            html += "<p>No data available</p>"
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
# 🚀 Render启动
# =========================
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
