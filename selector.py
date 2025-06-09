import pandas as pd

# Загрузка справочника
catalog = pd.read_excel("data/catalog.xlsx")

# Загрузка опросника
form = pd.read_excel("data/input.xlsx", header=None).set_index(0)[1].to_dict()

# Пример структуры input:
# {
#   "Тип шахты": "вытяжная",
#   "Диаметр": 710,
#   "Тип клапана": "поворотный",
#   ...
# }

result = []

if form["Тип шахты"].strip().lower() == "вытяжная":
    if form['Тип клапана'].strip().lower() == 'двустворчатый':
        name = f"Секция VB-{form['Диаметр']} (1м)"
        result.append(name)
    else:
        moshnost = str(form['Мощность мотора']).strip().lower()
        tip_motora = str(form.get('Тип мотора', '')).replace(" ", "").replace("-", "").strip().lower()
        tip_klapana = form['Тип клапана'].strip().lower()
        tip_klapana = "гравитац." if "гравитац" in tip_klapana else tip_klapana
        расположение = form.get('Расположение клапана', '').strip().lower()
        suffix = f"_{расположение}" if расположение else ""

        name = f"Секция камина VBV-{form['Диаметр']} (2м_agvf{moshnost}-{tip_motora}_{tip_klapana} клапан{suffix})"
        result.append(name)

    if form.get("Герметизация", "").strip().lower() == "да":
        result.append(f"Мембрана шахтная прорезиненная (1,5х1,5 метра) VB-{form['Диаметр']}")
        result.append("Лента битумная (кровельная-10м) ширина 10см")

    if form.get("Автомат защиты", "").strip().lower() == "да":
        result.append("Автоматический выключатель М611 1.6-2.5А")

    if form.get("Каплеулавливатель", "").strip().lower() == "да":
        result.append("Каплеулавливатель 1100")

    if form.get("Верхняя часть", "").strip().lower() == "зонт":
        result.append("Комлект зонта вентиляционной шахты")

    # Добавление секций удлинения
    try:
        удлинение = int(form.get("Итоговая длина шахты (м)", 2)) - 2
        if удлинение > 0:
            result.append(f"Секция VB-{form['Диаметр']} (1м)")
            if удлинение > 1:
                result[-1] = [result[-1]] * удлинение  # Добавить нужное количество
    except:
        pass

flat_result = []
for item in result:
    if isinstance(item, list):
        flat_result.extend(item)
    else:
        flat_result.append(item)

print("Сформированные позиции:")
for item in flat_result:
    print("-", item)
    print("DEBUG lowercased item for match:", item.lower())

print("\nКаталог: поиск совпадений...")
for name in flat_result:
    found = False
    for row in catalog["Наименование"]:
        try:
            if name.lower().strip() in str(row).lower().strip():
                print(f"  ✅ Найдено совпадение: {row}")
                found = True
        except Exception as e:
            print(f"Ошибка при сравнении '{name}' и '{row}': {e}")
    if not found:
        print(f"  ⚠️ Нет совпадений для: {name}")


matched_rows = []
for name in flat_result:
    for idx, row in catalog["Наименование"].items():
        try:
            if name.lower().strip() in str(row).lower().strip():
                matched_rows.append(catalog.loc[idx])
        except Exception as e:
            print(f"Ошибка при поиске совпадения: {e}")

if not matched_rows:
    print("❌ Совпадений не найдено. Возможно, проблема в расхождении регистра, формата или структуры строки.")

df = pd.DataFrame(matched_rows)
df.to_excel("output/result.xlsx", index=False)
