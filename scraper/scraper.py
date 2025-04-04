import os
import requests
from bs4 import BeautifulSoup
import json

# 📌 Directorios base
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
data_dir = os.path.join(base_dir, "data")

# 📌 Crear carpeta si no existe
os.makedirs(data_dir, exist_ok=True)

def extract_filtered_table(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="table table-striped")

    if not table:
        return None

    rows = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if len(tds) < 5:
            continue  # Saltar filas incompletas

        event_name = tds[0].find("a").text.strip() if tds[0].find("a") else tds[0].text.strip()
        date = tds[1].text.strip()

        # 📌 Separar fechas en "Init Date" y "Finish Date"
        date_parts = date.split(" — ")
        if len(date_parts) != 2:
            continue  # Saltar si la fecha no tiene el formato esperado

        init_date, finish_date = date_parts

        # 📌 Obtener peso y convertirlo a número
        try:
            prize_value = float(tds[4].text.strip())
        except ValueError:
            continue  # Si no es un número, saltar

        # 📌 Filtrar eventos con peso > 0
        if prize_value > 0:
            rows.append({
                "Event": event_name,
                "Init Date": init_date.strip(),
                "Finish Date": finish_date.strip(),
                "Weight": prize_value
            })

    return rows if rows else None


if __name__ == "__main__":
    url = "https://ctftime.org/event/list/upcoming"
    data = extract_filtered_table(url)

    if data:
        json_path = os.path.join(data_dir, "data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)