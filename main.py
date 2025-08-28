# main.py
# Flask-сервер для подбора вентиляционной шахты
# Контракт: POST /api/select -> {results: [{article, name, quantity}]}

from flask import Flask, request, jsonify, send_from_directory
import json
import os
import re
from typing import Dict, Any, List

app = Flask(__name__)

# === Загрузка каталога ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOG_PATH = os.path.join(BASE_DIR, "data", "komplektuyushchie.json")

with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    raw = json.load(f)

if isinstance(raw, dict):
    code_mapping: Dict[str, str] = raw.get("_code_mapping", {})
    items: List[Dict[str, Any]] = raw.get("items")
    if not items:
        # fallback: если данные пришли «плоским» массивом внутри словаря
        items = [v for v in raw.values() if isinstance(v, dict)]
else:
    # fallback: если это список словарей без служебного блока
    items = raw
    code_mapping = {}

# Индексы
by_art: Dict[str, Dict[str, Any]] = {}
for it in items:
    art = str(it.get("artikul") or it.get("article") or "").strip()
    if art:
        by_art[art] = it


# === Утилиты ===

def _norm(s: Any) -> str:
    if s is None:
        return ""
    s = str(s).strip().lower()
    # без агрессивной замены букв — фронт шлёт нормализованные ключи
    return s


def _phase_from_motor(motor: str) -> str:
    # тип_мотора: '6e' -> 1, '6d' -> 3
    motor = _norm(motor)
    return {"6e": "1", "6d": "3"}.get(motor, "")


def _find(predicate):
    for it in items:
        try:
            if predicate(it):
                return it
        except Exception:
            continue
    return None


def _find_all(predicate):
    out = []
    for it in items:
        try:
            if predicate(it):
                out.append(it)
        except Exception:
            continue
    return out


def _name_has(it: Dict[str, Any], *need):
    name = _norm(it.get("name"))
    return all(w in name for w in need)


def pick_membrana_by_diam(diam: str):
    """Ищем мембрану строго под диаметр: сначала по полю diameter, затем по имени."""
    # по атрибуту diameter
    it = _find(lambda x: _norm(x.get("category")) == "мембрана" and str(x.get("diameter", "")).strip() == diam)
    if it:
        return it
    # по имени (например, "VB-710" или просто "710")
    return _find(lambda x: _norm(x.get("category")) == "мембрана" and (diam in _norm(x.get("name"))))


def pick_lenta():
    """Ищем универсальную битумную ленту по имени."""
    return _find(lambda x: "лента" in _norm(x.get("name")))


def pick_hermetic(membrana: bool, lenta: bool):
    out = []
    if membrana:
        it = _find(lambda x: _norm(x.get("category")) == "мембрана" or "мембран" in _norm(x.get("name")))
        if it:
            out.append(it)
    if lenta:
        it = _find(lambda x: "лента" in _norm(x.get("name")))  # иногда категория другая
        if it:
            out.append(it)
    return out


# === Формирование ключа для _code_mapping ===

def build_code_key(payload: Dict[str, Any]) -> str:
    tip = payload.get("tip")  # VBV/VBP/VBA/VBR
    diam = str(payload.get("diametr", "")).strip()
    klapan = payload.get("tip_klapana")  # pov/grav/dvustv
    rasp = payload.get("raspolozhenie")  # niz/verh (только для pov)
    grav_variant = payload.get("grav_variant")  # vnut/vnesh (только для grav)
    motor = payload.get("tip_motora")  # 6e/6d
    power = str(payload.get("moshchnost", "")).strip()  # 370/750

    if not tip or not diam:
        return ""

    tip = tip.upper()  # VBV/VBP/VBA/VBR

    # В большинстве ключей требуется мощность+фазность (для активных/вытяжных)
    phase = _phase_from_motor(motor) if motor else ""

    # Ветка по типу клапана
    if klapan == "pov":
        if not power or not phase or not rasp:
            return ""
        pos = {"niz": "niz", "verh": "verh"}.get(rasp)
        if not pos:
            return ""
        return f"{tip}_{diam}_{power}_{phase}_pov_{pos}"

    if klapan == "grav":
        if not power or not phase or not grav_variant:
            return ""
        gv = {"vnut": "grav_vnut", "vnesh": "grav_vnesh"}.get(grav_variant)
        if not gv:
            return ""
        return f"{tip}_{diam}_{power}_{phase}_{gv}"

    if klapan == "dvustv":
        # для двустворчатого клапана в ряде каталогов ключ может не требовать power/phase
        # оставляем консервативный вариант без них, при необходимости расширим
        return f"{tip}_{diam}_dvustv"

    return ""


# === Подбор доп.комплектующих ===

def pick_drive_for_pov(diam: str):
    # Заглушка: на текущей итерации приводы не подбираем вовсе
    return None


def pick_top_part(kind: str, diam: str):
    # kind: 'zont'|'rastrub' (универсальные, без привязки к диаметру)
    kind = _norm(kind)
    if kind == "zont":
        # сначала по категории, затем по имени
        if "89174" in by_art:
            return by_art["89174"]
        it = _find(lambda x: _name_has(x, "комплект", "зонт"))
        if it:
            return it    
        it = _find(lambda x: _norm(x.get("category")) == "зонт")
        if it:
            return it
        return _find(lambda x: _name_has(x, "зонт"))
    if kind == "rastrub":
        # часто в каталоге лежит в "прочее" — ищем по имени
        return _find(lambda x: _name_has(x, "раструб"))
    return None


def pick_udlinenie_sections(diam: str, meters: int):
    if not meters:
        return None, 0
    # Секции 1 м: category=='секция', type=='VB', diameter==diam
    it = _find(lambda x: _norm(x.get("category")) == "секция" and _norm(x.get("type")) == "vb" and str(x.get("diameter", "")).strip() == diam)
    if it:
        return it, int(meters)
    # fallback по имени
    it = _find(lambda x: _name_has(x, "секция") and ("vb" in _norm(x.get("type")) or " vb" in _norm(x.get("name"))) and diam in _norm(x.get("name")))
    return it, int(meters) if it else (None, 0)


def pick_hermetic(membrana: bool, lenta: bool):
    out = []
    if membrana:
        it = _find(lambda x: _norm(x.get("category")) == "мембрана" or "мембран" in _norm(x.get("name")))
        if it:
            out.append(it)
    if lenta:
        it = _find(lambda x: "лента" in _norm(x.get("name")))  # иногда категория другая
        if it:
            out.append(it)
    return out


def pick_avtomat(target_amps: float):
    """Выбираем автомат по номиналу тока: поддерживаются одиночные значения и диапазоны (например, 1.0-1.6A).
    Парсим ток из имени (форматы: "3 A", "3A", "2,4 A", т.п.).
    """
    candidates_exact = []   # (val, item)
    candidates_upper = []   # (upper_bound, item) for ranges and singles used as fallback

    for x in items:
        if not _name_has(x, "автомат"):
            continue
        name = x.get("name", "")
        # 1) Диапазон, например: "1.0-1.6А" (пробелы и разные дефисы допустимы)
        m_range = re.search(r"(\d+(?:[\.,]\d+)?)\s*[-–—]\s*(\d+(?:[\.,]\d+)?)(?:\s*A|A)?", name, flags=re.IGNORECASE)
        if m_range:
            try:
                v1 = float(m_range.group(1).replace(',', '.'))
                v2 = float(m_range.group(2).replace(',', '.'))
                lo, hi = (v1, v2) if v1 <= v2 else (v2, v1)
            except Exception:
                lo = hi = None
            if lo is not None and hi is not None:
                # если искомый ток внутри диапазона — это идеальное совпадение
                if lo - 1e-9 <= target_amps <= hi + 1e-9:
                    return x
                # иначе используем верхнюю границу как кандидат для "минимального большего"
                candidates_upper.append((hi, x))
                continue
        # 2) Одиночное значение: "3 A" или "3A"
        m_single = re.search(r"(\d+(?:[\.,]\d+)?)\s*A", name, flags=re.IGNORECASE) or \
                   re.search(r"(\d+(?:[\.,]\d+)?)A", name, flags=re.IGNORECASE)
        if m_single:
            try:
                val = float(m_single.group(1).replace(',', '.'))
            except Exception:
                continue
            # сначала попытаемся найти точное совпадение
            candidates_exact.append((val, x))
            candidates_upper.append((val, x))

    # точное совпадение среди одиночных
    for val, x in candidates_exact:
        if abs(val - target_amps) < 1e-6:
            return x

    # минимальный больший среди всех верхних границ (и одиночных значений)
    greater = [(val, x) for val, x in candidates_upper if val >= target_amps - 1e-9]
    if greater:
        val, x = sorted(greater, key=lambda t: t[0])[0]
        return x

    return None


def pick_kapleu(diam: str):
    # Универсальный подбор
    return _find(lambda x: _name_has(x, "каплеулав"))


def pick_korona():
    return _find(lambda x: _name_has(x, "корона"))


@app.route("/api/select", methods=["POST"])
def api_select():
    payload = request.get_json(silent=True) or {}
    messages: List[str] = []

    tip = payload.get("tip")
    diam = str(payload.get("diametr", "")).strip()
    klapan = payload.get("tip_klapana")

    # Бэкенд-ограничения: приведение параметров к допустимым
    # 2.1) Для VBA клапан всегда поворотный
    if tip == "VBA" and klapan != "pov":
        payload["tip_klapana"] = "pov"
        klapan = "pov"
        messages.append("Для VBA выбран поворотный клапан (гравитационного не бывает)")

    # 2.2) Для моторных типов (VBV/VBA/VBR) мощность определяется диаметром
    required_power = {"560": "370", "710": "370", "800": "750"}.get(diam)

    # валидация минимальных полей
    if not tip or not diam or not klapan:
        return jsonify({"results": [], "message": "Не хватает обязательных параметров"})

    # Доп.валидация: для VBV/VBP/VBR/VBA при pov/grav обязателен тип мотора; мощность можем выставить по диаметру
    needs_motor = tip in ("VBV", "VBP", "VBR", "VBA") and klapan in ("pov", "grav")
    if needs_motor:
        if not payload.get("tip_motora"):
            return jsonify({"results": [], "message": "Не хватает параметров: тип мотора обязателен для выбранной конфигурации"})
        # Приведём мощность к допустимой по диаметру, если нужно
        if required_power:
            cur_power = str(payload.get("moshchnost", "")).strip()
            if not cur_power:
                payload["moshchnost"] = required_power
                messages.append(f"Мощность автоматически установлена {required_power} Вт для D{diam}")
            elif cur_power != required_power:
                payload["moshchnost"] = required_power
                messages.append(f"Мощность скорректирована до {required_power} Вт для D{diam}")

    key = build_code_key(payload)

    result: Dict[str, Dict[str, Any]] = {}
    # messages: List[str] = []  # removed this line as messages declared earlier

    # 1) Комплект шахты (по _code_mapping)
    if key and code_mapping.get(key):
        art = code_mapping[key]
        base = by_art.get(art, {"artikul": art, "name": f"Комплект шахты ({key})"})
        result[art] = {"article": art, "name": base.get("name", ""), "quantity": 1}

    # 3) Верхняя часть: зонт/раструб
    top = payload.get("verhnyaya_chast")
    if top:
        it = pick_top_part(top, diam)
        if it:
            art = str(it.get("artikul") or it.get("article"))
            result[art] = {"article": art, "name": it.get("name", ""), "quantity": 1}

    # 4) Герметизация (мембрана/лента)
    g = payload.get("germetizatsiya") or {}
    if bool(g.get("membrana")):
        it = pick_membrana_by_diam(diam)
        if it:
            art = str(it.get("artikul") or it.get("article"))
            result[art] = {"article": art, "name": it.get("name", ""), "quantity": 1}
        else:
            messages.append(f"Мембрана для диаметра D{diam} не найдена в каталоге")
    if bool(g.get("lenta")):
        it = pick_lenta()
        if it:
            art = str(it.get("artikul") or it.get("article"))
            result[art] = {"article": art, "name": it.get("name", ""), "quantity": 1}
        else:
            messages.append("Лента битумная не найдена в каталоге")

    # 5) Автомат защиты (если запрошен)
    if bool(payload.get("avtomat")) and needs_motor:
        motor = _norm(payload.get("tip_motora"))
        power = str(payload.get("moshchnost", "")).strip()
        amps_map = {
            ("6e", "370"): 3.0,
            ("6e", "750"): 5.0,
            ("6d", "370"): 1.1,
            ("6d", "750"): 2.4,
        }
        target = amps_map.get((motor, power))
        if target is None:
            messages.append("Не удалось определить номинал автомата: неизвестная комбинация тип мотора × мощность")
        else:
            it = pick_avtomat(target)
            if it:
                art = str(it.get("artikul") or it.get("article"))
                result[art] = {"article": art, "name": it.get("name", ""), "quantity": 1}
            else:
                messages.append(f"Автомат защиты {target} A не найден в каталоге")

    # 6) Удлинение (в метрах) — секции VB 1 м по диаметру
    meters = int(payload.get("udlinenie_m") or 0)
    if meters:
        it, qty = pick_udlinenie_sections(diam, meters)
        if it and qty > 0:
            art = str(it.get("artikul") or it.get("article"))
            result[art] = {"article": art, "name": it.get("name", ""), "quantity": qty}

    # 7) Каплеулавливатель (опционально)
    if bool(payload.get("kapleulavlivatel")):
        tip_upper = str(tip).upper()
        if tip_upper in ("VBA", "VBP", "VBR"):
            messages.append("Каплеулавливатель не применяется для приточных шахт и будет проигнорирован")
        else:
            it = pick_kapleu(diam)
            if it:
                art = str(it.get("artikul") or it.get("article"))
                result[art] = {"article": art, "name": it.get("name", ""), "quantity": 1}

    # 8) Корона (распределитель воздуха)
    tip_upper = str(tip).upper()
    if klapan == "dvustv":
        # если двустворчатый — корона не ставится; если пользователь просил — сообщаем
        if payload.get("korona"):
            messages.append("Опция 'Корона' проигнорирована: для двустворчатого клапана не применяется")
    else:
        if tip_upper == "VBR":
            it = pick_korona()
            if it:
                art = str(it.get("artikul") or it.get("article"))
                result[art] = {"article": art, "name": it.get("name", ""), "quantity": 1}
        elif tip_upper in ("VBA", "VBP") and bool(payload.get("korona")):
            it = pick_korona()
            if it:
                art = str(it.get("artikul") or it.get("article"))
                result[art] = {"article": art, "name": it.get("name", ""), "quantity": 1}

    out = list(result.values())
    if not out:
        return jsonify({"results": [], "message": "Ничего не найдено" if not messages else "; ".join(messages)})
    if messages:
        return jsonify({"results": out, "message": "; ".join(messages)})
    return jsonify({"results": out})


@app.route("/", methods=["GET"])
def index():
    return send_from_directory("web", "index.html")


@app.route("/web/<path:filename>")
def static_files(filename):
    return send_from_directory("web", filename)


if __name__ == "__main__":
    # PROD: запускать через gunicorn/uwsgi; debug только локально
    app.run(host="0.0.0.0", port=5001, debug=True)