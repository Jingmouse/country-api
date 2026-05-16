import requests
from bs4 import BeautifulSoup
from flask import Flask
import os

app = Flask(__name__)

# =========================
# 首页
# =========================
@app.route("/")
def home():
    return "Website Running"


# =========================
# 国家信息
# =========================
def get_country_info(country):

    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=10)
    except:
        return {"name": country, "intro": "Unavailable"}

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
        "china": ["Beijing", "Shanghai", "Guangzhou", "Shenzhen"],
        "japan": ["Tokyo", "Osaka", "Kyoto", "Yokohama"],
        "united states": ["New York", "Los Angeles", "Chicago", "Houston"],
        "united kingdom": ["London", "Manchester", "Birmingham", "Liverpool"],
        "canada": ["Toronto", "Vancouver", "Montreal", "Calgary"],
        "australia": ["Sydney", "Melbourne", "Brisbane", "Perth"]
    }

    return data.get(country.lower().strip(), [])


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

    return [{"item": k, "price": v} for k, v in sample.get(city, [("No data", "")])]


# =========================
# 🍜 食物爬虫（🔥修复稳定版）
# =========================
def get_foods(country):

    # 👉 关键修复：统一格式
    country = country.lower().strip().replace(" ", "-")

    url = f"https://10dishes.com/{country}/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        r = requests.get(url, headers=headers, timeout=10)
    except:
        return ["Food unavailable"]

    # 👉 如果网站不存在
    if r.status_code != 200:
        return fallback_foods(country)

    soup = BeautifulSoup(r.text, "html.parser")

    # =========================
    # 🔥 改进点1：扩大抓取范围
    # =========================
    elements = soup.select("h2, h3, li, article h2, article h3")

    foods = []

    for e in elements:

        name = e.get_text(strip=True)
        n = name.lower()

        # =========================
        # 🔥 改进点2：更合理过滤
        # =========================
        if any(x in n for x in [
            "menu",
            "national anthem",
            "key flavors",
            "cooking methods",
            "regional variations",
            "introduction",
            "about"
        ]):
            continue

        if len(name) > 2:
            foods.append(name)

    # 去重
    foods = list(dict.fromkeys(foods))

    # =========================
    # 🔥 改进点3：防止空输出
    # =========================
    if not foods:
        return fallback_foods(country)

    return foods[:10]


# =========================
# 🍜 fallback（保证一定有数据）
# =========================
def fallback_foods(country):

    data = {
        "china": ["Dumplings", "Hot Pot", "Peking Duck", "Noodles"],
        "japan": ["Sushi", "Ramen", "Tempura", "Udon"],
        "united-states": ["Burger", "Hot Dog", "BBQ Ribs"],
        "united-kingdom": ["Fish and Chips", "Pie", "Roast"],
        "canada": ["Poutine", "Pancakes"],
        "australia": ["Meat Pie", "BBQ"]
    }

    return data.get(country, ["No food data available"])


# =========================
# 国家页面
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

.box {{
    background: white;
    padding: 15px;
    margin-top: 15px;
    border-radius: 10px;
}}

.city {{
    padding: 10px;
    margin-top: 10px;
    border-left: 4px solid #3498db;
    background: white;
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
setTimeout(sendHeight, 500);
</script>

</head>

<body>

<h1>{info['name']}</h1>

<div class="box">
<h3>Introduction</h3>
<p>{info['intro']}</p>
</div>

<div class="box">
<h3>Cities & Cost</h3>
"""

    for city in cities:
        html += f"<div class='city'><h4>{city}</h4>"
        for item in get_cost(city):
            html += f"<p>{item['item']} : {item['price']}</p>"
        html += "</div>"

    html += """
</div>

</body>
</html>
"""

    return html


# =========================
# 食物页面
# =========================
@app.route("/food/<country>")
def food_page(country):

    foods = get_foods(country)

    html = f"""
<html>
<head>
<meta charset="utf-8">
<title>Food</title>

<style>
body {{
    font-family: Arial;
    padding: 20px;
    background: #f5f5f5;
}}

.box {{
    background: white;
    padding: 15px;
    border-radius: 10px;
}}

.item {{
    margin-top: 10px;
    padding: 10px;
    border-left: 4px solid #e67e22;
    background: #fafafa;
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
setTimeout(sendHeight, 500);
</script>

</head>

<body>

<div class="box">
<h3>Famous Food</h3>
"""

    for food in foods:
        html += f"<div class='item'>{food}</div>"

    html += """
</div>

</body>
</html>
"""

    return html


# =========================
# Run
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
