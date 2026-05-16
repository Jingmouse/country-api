def get_cost(city):

    url = f"https://www.numbeo.com/cost-of-living/in/{city}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=8)
    except:
        return [{"item": "No data", "price": "N/A"}]

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

    # 🛡️ fallback 2：城市数据为空时
    if not items:
        items = [{"item": "Data not available", "price": "-"}]

    return items
