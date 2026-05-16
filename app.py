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
from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# =====================================
# 国家简介
# =====================================
def get_country_info(country):

    country = country.strip().replace(" ", "_")

    url = f"https://en.wikipedia.org/wiki/{country}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

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

    title = soup.find("h1", id="firstHeading")

    name = title.text.strip() if title else "Not found"

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

                data_text = data.get_text(
                    " ",
                    strip=True
                )

                data_text = re.sub(
                    r"\[.*?\]",
                    "",
                    data_text
                )

                if (
                    "capital" in header_text
                    and capital == "Not found"
                ):

                    capital = re.sub(
                        r"\d.*",
                        "",
                        data_text
                    ).strip()

                if (
                    "official" in header_text
                    and "language" in header_text
                ):

                    language = data_text
                    break

                if (
                    "national" in header_text
                    and "language" in header_text
                ):

                    language = data_text

    paragraphs = soup.find_all("p")

    intro = "Not found"

    for p in paragraphs:

        text = p.get_text(
            " ",
            strip=True
        )

        text = re.sub(
            r"\[.*?\]",
            "",
            text
        )

        if len(text) > 80:

            intro = text
            break

    return {
        "Name": name,
        "Capital": capital,
        "Language": language,
        "Introduction": intro
    }


# =====================================
# 国家主要城市
# =====================================
def get_major_cities(country):

    country = country.strip().title()
    
    cities_data = {

        "China": [
            "Beijing",
            "Shanghai",
            "Guangzhou",
            "Shenzhen"
        ],

        "Japan": [
            "Tokyo",
            "Osaka",
            "Kyoto",
            "Yokohama"
        ],

        "France": [
            "Paris",
            "Lyon",
            "Marseille",
            "Nice"
        ],

        "United States": [
            "New-York",
            "Los-Angeles",
            "Chicago",
            "Houston"
        ],

        "South Korea": [
            "Seoul",
            "Busan",
            "Incheon",
            "Daegu"
        ],

        "United Kingdom": [
            "London",
            "Manchester",
            "Birmingham",
            "Liverpool"
        ]
    }

    return cities_data.get(country, [])


# =====================================
# 获取城市物价
# =====================================
def get_cost_of_living(city):

    city = city.strip().replace(" ", "-")

    url = f"https://www.numbeo.com/cost-of-living/in/{city}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            timeout=5
        )

        response.raise_for_status()

    except:

        return {
            "city": city,
            "status": "error"
        }

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    table = soup.find(
        "table",
        class_="data_wide_table"
    )

    if not table:

        return {
            "city": city,
            "status": "error"
        }

    rows = table.find_all("tr")

    items = []

    for row in rows[:10]:

        cols = row.find_all("td")

        if len(cols) >= 2:

            items.append({
                "item": cols[0].get_text(strip=True),
                "price": cols[1].get_text(strip=True)
            })

    return {
        "city": city,
        "status": "success",
        "items": items
    }


# =====================================
# 首页
# =====================================
@app.route("/")
def home():

    return "Country API is running!"


# =====================================
# 国家简介 API
# =====================================
@app.route("/country/<country>")
def country_api(country):

    info = get_country_info(country)

    return jsonify(info)


# =====================================
# 国家物价 API
# =====================================
@app.route("/country-cost/<country>")
def country_cost(country):

    cities = get_major_cities(country)

    if not cities:

        return jsonify({
            "status": "error",
            "message": "Country not supported"
        })

    results = []

    for city in cities:

        city_data = get_cost_of_living(city)

        results.append(city_data)

    return jsonify({
        "country": country,
        "cities": results
    })


# =====================================
# Render 启动
# =====================================
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
