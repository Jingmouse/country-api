import requests
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

    app.run(host="0.0.0.0", port=port)
