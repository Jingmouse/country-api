'''import requests
from bs4 import BeautifulSoup
import re
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_country_info(country):

    #处理 South Korea 这种国家名
    country = country.strip().replace(" ", "_")

    url = f"https://en.wikipedia.org/wiki/{country}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0",
        "Accept-Language": "en-US,en;q=0.9",
    }#用于把爬虫伪装为浏览器

    #防止请求失败直接崩溃
    try:

        response = requests.get(url, headers=headers, timeout=10)

    except requests.exceptions.RequestException:

        return {
            "Name": "Error",
            "Capital": "Error",
            "Language": "Error",
            "Introduction": "Request Failed"
        }

    if response.status_code != 200:

        return {
            "Name": "Not Found",
            "Capital": "Not Found",
            "Language": "Not Found",
            "Introduction": "Country not found"
        }

    soup = BeautifulSoup(response.text, "html.parser")

    #国家名称
    title = soup.find("h1", id="firstHeading")

    name = title.text.strip() if title else "Not found"

    #找infobox
    infobox = soup.find(
        "table",
        class_=lambda x: x and "infobox" in x
    )

    capital = "Not found"
    language = "Not found"

    if infobox:

        rows = infobox.find_all("tr")

        for row in rows:

            header = row.find("th")
            data = row.find("td")

            if header and data:

                header_text = header.text.strip().lower()

                data_text = data.get_text(" ", strip=True)

                #删除参考文献数字
                data_text = re.sub(r"\[.*?\]", "", data_text)

                #首都
                if "capital" in header_text and capital == "Not found":

                    #删除坐标
                    capital = re.sub(r"\d.*", "", data_text).strip()

                #官方语言
                if "official" in header_text and "language" in header_text:

                    language = data_text
                    break

                #国家语言
                if "national" in header_text and "language" in header_text:

                    language = data_text

    #简介段落
    paragraphs = soup.find_all("p")

    intro = "Not found"

    for p in paragraphs:

        text = p.get_text(" ", strip=True)

        #删除参考文献
        text = re.sub(r"\[.*?\]", "", text)

        #过滤太短内容
        if len(text) > 80:

            intro = text
            break

    return {
        "Name": name,
        "Capital": capital,
        "Language": language,
        "Introduction": intro
    }


#API接口
@app.route("/country/<country>")
def country_api(country):

    info = get_country_info(country)

    return jsonify(info)


if __name__ == "__main__":

    import os

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)'''

import requests
from bs4 import BeautifulSoup
import re
from flask import Flask
import os

app = Flask(__name__)

# =========================
# 国家简介
# =========================
def get_country_info(country):

    country = country.strip().replace(" ", "_")

    url = f"https://en.wikipedia.org/wiki/{country}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except:
        return {
            "Name": "Error",
            "Capital": "Error",
            "Language": "Error",
            "Introduction": "Request Failed"
        }

    if response.status_code != 200:
        return {
            "Name": "Not Found",
            "Capital": "Not Found",
            "Language": "Not Found",
            "Introduction": "Country not found"
        }

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find("h1", id="firstHeading")
    name = title.text.strip() if title else country

    infobox = soup.find("table", class_=lambda x: x and "infobox" in x)

    capital = "Not found"
    language = "Not found"

    if infobox:
        for row in infobox.find_all("tr"):
            header = row.find("th")
            data = row.find("td")

            if header and data:

                h = header.text.lower()
                d = data.get_text(" ", strip=True)

                d = re.sub(r"\[.*?\]", "", d)

                if "capital" in h and capital == "Not found":
                    capital = re.sub(r"\d.*", "", d).strip()

                if "official" in h and "language" in h:
                    language = d

                if "national" in h and "language" in h:
                    language = d

    intro = "Not found"
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        text = re.sub(r"\[.*?\]", "", text)
        if len(text) > 80:
            intro = text
            break

    return {
        "Name": name,
        "Capital": capital,
        "Language": language,
        "Introduction": intro
    }


# =========================
# 物价
# =========================
def get_cost_of_living(country):

    cities_map = {
        "China": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen"],
        "Japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama"],
        "France": ["Paris", "Lyon", "Marseille", "Nice"],
        "United States": ["New-York", "Los-Angeles", "Chicago", "Houston"],
        "South Korea": ["Seoul", "Busan", "Incheon", "Daegu"],
        "United Kingdom": ["London", "Manchester", "Birmingham", "Liverpool"]
    }

    country = country.strip().title()
    cities = cities_map.get(country, [])

    results = []

    for city in cities:

        url = f"https://www.numbeo.com/cost-of-living/in/{city}"

        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            r = requests.get(url, headers=headers, timeout=8)
        except:
            continue

        soup = BeautifulSoup(r.text, "html.parser")

        table = soup.find("table", class_="data_wide_table")

        items = []

        if table:
            for row in table.find_all("tr")[:8]:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    items.append({
                        "item": cols[0].get_text(strip=True),
                        "price": cols[1].get_text(strip=True)
                    })

        results.append({
            "city": city,
            "items": items
        })

    return results


# =========================
# 🌍 核心网页（给 Wix iframe）
# =========================
@app.route("/country-page/<country>")
def country_page(country):

    info = get_country_info(country)
    cities = get_cost_of_living(country)

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>{info['Name']}</title>
        <style>
            body {{
                font-family: Arial;
                padding: 20px;
            }}
            h1 {{
                color: #2c3e50;
            }}
            .box {{
                margin-top: 20px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 8px;
            }}
            .city {{
                margin-top: 15px;
                padding: 10px;
                border-left: 4px solid #3498db;
            }}
        </style>
    </head>
    <body>

    <h1>{info['Name']}</h1>

    <div class="box">
        <h2>📘 Introduction</h2>
        <p>{info['Introduction']}</p>

        <h3>🏛 Capital: {info['Capital']}</h3>
        <h3>🗣 Language: {info['Language']}</h3>
    </div>

    <div class="box">
        <h2>💰 Cost of Living</h2>
    """

    for city in cities:

        html += f"<div class='city'><h3>{city['city']}</h3>"

        for item in city["items"]:
            html += f"<p>{item['item']} : {item['price']}</p>"

        html += "</div>"

    html += """
    </div>
    </body>
    </html>
    """

    return html


# =========================
# Render 启动
# =========================
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
