# main.py
# Flask-сервер для обработки запросов по подбору вентиляционной шахты
# Использует данные из JSON-файла комплектующих

from flask import Flask, request, jsonify, send_from_directory
import json
import os

app = Flask(__name__)

# Загрузка каталога комплектующих
CATALOG_PATH = os.path.join("data", "komplektuyushchie.json")
with open(CATALOG_PATH, encoding="utf-8") as f:
    catalog = json.load(f)


# Функция нормализации пользовательского ввода
def normalize(user_input):
    mapping = {
        "тип": {
            "вытяжная": "vbv",
            "приточная": "vba",
            "подмешивающая": "vbr",
            "прямоточная": "vbp",
            "vbv": "vbv",
            "vbp": "vbp",
            "vba": "vba",
            "vbr": "vbr"
        },
        "клапан": {
            "поворотный": "поворотный",
            "гравитационный": "гравитац.",
            "двустворчатый": "двустворчатый",
            "нет": "нет"
        }
    }

    def get_expected(key, val):
        return mapping.get(key, {}).get(val.lower(), val.lower())

    normalized = {}
    for key in user_input:
        val = user_input[key]
        normalized[key] = get_expected(key, val)
    if "фазность" in normalized:
        normalized["фазность"] = normalized["фазность"].replace("е", "e").replace("Е", "E")
    return normalized

def find_matches(user_input: dict):
    print("user_input:", user_input)
    results = []

    normalized_input = normalize(user_input)
    print(f"normalized_input: {normalized_input}")

    tip = normalized_input.get("тип", "")
    dia = normalized_input.get("диаметр", "")
    klapan = normalized_input.get("клапан", "")
    faza = normalized_input.get("фазность", "")
    power = normalized_input.get("мощность", "")
    position = normalized_input.get("расположение", "")  # новое поле, например "верх" или "низ"

    for item in catalog:
        name = item.get("name", "").lower()
        print("checking:", name)

        if tip in name and dia in name:
            if faza and faza not in name:
                continue
            if power and power not in name:
                continue
            if klapan and klapan not in name and klapan not in ["нет", "двустворчатый"]:
                continue
            if position and position not in name:
                continue
            results.append({
                "article": item.get("article"),
                "price": item.get("price"),
                "name": item.get("name")
            })

    print("matched:", len(results))
    return results

@app.route("/search", methods=["POST"])
def search():
    user_input = request.json
    if not user_input:
        return jsonify({"error": "Нет данных"}), 400

    results = find_matches(user_input)
    if not results:
        return jsonify({"results": [], "message": "Ничего не найдено"})
    return jsonify({"results": results})

@app.route("/", methods=["GET"])
def index():
    return send_from_directory("web", "index.html")


@app.route("/web/<path:filename>")
def static_files(filename):
    return send_from_directory("web", filename)


# Новый маршрут для получения опций
@app.route("/options", methods=["GET"])
def options():
    types = set()
    diameters = set()

    for item in catalog:
        name = item["name"].lower()

        if "vbv" in name:
            types.add("VBV")
        elif "vbp" in name:
            types.add("VBP")
        elif "vba" in name:
            types.add("VBA")
        elif "vbr" in name:
            types.add("VBR")

        if "560" in name:
            diameters.add("560")
        if "710" in name:
            diameters.add("710")
        if "800" in name:
            diameters.add("800")

    req_type = request.args.get("тип", "").lower()

    valve_map = {
        "vbv": ["поворотный", "гравитационный"],
        "vba": ["поворотный"],
        "vbp": ["двустворчатый", "поворотный"],
        "vbr": ["поворотный"]
    }

    valves = set(valve_map.get(req_type, []))

    return jsonify({
        "тип": sorted(types),
        "диаметр": sorted(diameters),
        "клапан": sorted(valves)
    })

if __name__ == "__main__":
    app.run(debug=True)