question_flow = {
    "Тип шахты": {
        "question": "тип",
        "type": "select",
        "options": [
            {"label": "вытяжная", "value": "VBV"},
            {"label": "приточная активная", "value": "VBP"},
            {"label": "приточная пассивная", "value": "VBA"},
            {"label": "приточная с подмешиванием", "value": "VBR"}
        ],
        "param": "tip"
    },
    "Диаметр": {
        "question": "диаметр",
        "type": "select",
        "options": ["560", "710", "800", "1100"],
        "depends_on": {"Тип шахты": ["VBV", "VBP", "VBA", "VBR"]},
        "param": "diametr"
    },
    "Тип клапана": {
        "question": "тип_клапана",
        "type": "select",
        "options": [
            {"label": "поворотный", "value": "pov"},
            {"label": "гравитационный", "value": "grav"},
            {"label": "двустворчатый", "value": "dvustv"}
        ],
        "depends_on": {"Тип шахты": ["VBV", "VBP", "VBA", "VBR"]},
        "param": "tip_klapana"
    },
    "Расположение (для поворотного)": {
        "question": "расположение_клапана",
        "type": "select",
        "options": [
            {"label": "низ", "value": "niz"},
            {"label": "верх", "value": "verh"}
        ],
        "depends_on": {"Тип клапана": ["pov"]},
        "param": "raspolozhenie"
    },
    "Тип гравитационного": {
        "question": "тип_гравитационного",
        "type": "select",
        "options": [
            {"label": "внутренний", "value": "vnut"},
            {"label": "внешний", "value": "vnesh"}
        ],
        "depends_on": {"Тип клапана": ["grav"]},
        "param": "grav_variant"
    },
    "Тип мотора": {
        "question": "тип_мотора",
        "type": "select",
        "options": [
            {"label": "6E (однофазный)", "value": "6e"},
            {"label": "6D (трёхфазный)", "value": "6d"}
        ],
        "depends_on": {"Тип шахты": ["VBV", "VBP", "VBR"], "Тип клапана": ["pov", "grav"]},
        "param": "tip_motora"
    },
    "Мощность": {
        "question": "мощность",
        "type": "select",
        "options": ["370", "750"],
        "depends_on": {"Тип шахты": ["VBV", "VBP", "VBR"], "Тип клапана": ["pov", "grav"]},
        "param": "moshchnost"
    },
    "Верхняя часть": {
        "question": "верхняя_часть",
        "type": "select",
        "options": [
            {"label": "зонт", "value": "zont"},
            {"label": "раструб", "value": "rastrub"}
        ],
        "param": "verhnyaya_chast"
    },
    "Герметизация": {
        "question": "герметизация",
        "type": "checkbox-group",
        "options": [
            {"label": "мембрана", "value": "membrana"},
            {"label": "лента", "value": "lenta"}
        ],
        "param": "germetizatsiya"
    },
    "Автомат защиты": {
        "question": "автомат",
        "type": "checkbox",
        "param": "avtomat"
    },
    "Каплеулавливатель": {
        "question": "каплеулавливатель",
        "type": "checkbox",
        "param": "kapleulavlivatel"
    },
    "Корона": {
        "question": "корона",
        "type": "checkbox",
        "depends_on": {"Тип шахты": ["VBA", "VBP", "VBR"], "Тип клапана": ["pov", "grav"]},
        "param": "korona"
    },
    "Удлинение (м)": {
        "question": "удлинение",
        "type": "number",
        "param": "udlinenie_m"
    }
}
