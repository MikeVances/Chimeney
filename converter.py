"""
Скрипт конвертации Excel-файла с комплектующими вентиляционных шахт в JSON-формат.
Автоматически определяет строку с заголовками ['Артикул', 'Наименование', 'Цена'] и загружает данные ниже неё.
Используется на этапе локальной отладки и разработки интерфейса под Flask.
"""

import pandas as pd
import json

# Входной файл
input_file = 'data/catalog.xlsx'
output_file = 'data/komplektuyushchie.json'

# Загрузка Excel без заголовков
raw_df = pd.read_excel(input_file, header=None, dtype=str)

# Поиск строки с заголовками
header_row_index = None
for idx, row in raw_df.iterrows():
    if list(row[:3]) == ['Артикул', 'Наименование', 'Цена']:
        header_row_index = idx
        break

if header_row_index is None:
    raise ValueError('Заголовки не найдены. Убедитесь, что файл содержит "Артикул", "Наименование", "Цена".')

# Загрузка данных начиная со строки после заголовков
df = pd.read_excel(input_file, header=header_row_index, dtype=str)

# Удаление пустых строк
df = df.dropna(subset=['Артикул', 'Наименование', 'Цена'])

# Переименование столбцов
df = df.rename(columns={
    'Артикул': 'artikul',
    'Наименование': 'name',
    'Цена': 'price'
})

# Преобразование и сохранение
data = df.to_dict(orient='records')

import re

def replace_cyrillic_e_in_technical(name):
    # Заменяет кириллические е/Е на латинские в частях артикулов вида 6е/6Е (например AGVF370-6Е)
    return re.sub(r'6[еЕ](?=[\W_]|$)', lambda m: '6E' if m.group(0)[-1].isupper() else '6e', name)

for item in data:
    if 'name' in item and isinstance(item['name'], str):
        item['name'] = replace_cyrillic_e_in_technical(item['name'])
    if 'price' in item and isinstance(item['price'], str):
        item['price'] = item['price'].replace('\u00A0', '').replace(' ', '')

# Парсинг параметров из поля name
for item in data:
    if 'name' in item and isinstance(item['name'], str):
        name_lower = item['name'].lower()

        # type
        type_match = re.search(r'\b(vbv|vba|vbr|vbp)\b', name_lower)
        if type_match:
            item['type'] = type_match.group(1).upper()

        # diameter - число из 3 цифр
        diameter_match = re.search(r'\b(\d{3})\b', item['name'])
        if diameter_match:
            item['diameter'] = diameter_match.group(1)

        # power
        if 'agvf370' in name_lower:
            item['power'] = 'AGVF370'
        elif 'agvf750' in name_lower:
            item['power'] = 'AGVF750'

        # phase
        if '6d' in name_lower:
            item['phase'] = '3'
        elif '6e' in name_lower:
            item['phase'] = '1'

        # valve
        if 'поворотный' in name_lower:
            item['valve'] = 'поворотный'
        elif 'гравитационный' in name_lower:
            item['valve'] = 'гравитационный'
        elif 'двустворчатый' in name_lower:
            item['valve'] = 'двустворчатый'
        elif 'без' in name_lower:
            item['valve'] = 'без'

        # position
        if 'верх' in name_lower:
            item['position'] = 'верх'
        elif 'низ' in name_lower:
            item['position'] = 'низ'
        elif 'внутр' in name_lower:
            item['position'] = 'внутр'
        elif 'внешн' in name_lower:
            item['position'] = 'внешн'

        # category
        if 'секция' in name_lower:
            item['category'] = 'секция'
        elif 'автомат' in name_lower:
            item['category'] = 'автомат'
        elif 'мембрана' in name_lower:
            item['category'] = 'мембрана'
        elif 'лента' in name_lower:
            item['category'] = 'удлинение'
        elif 'зонт' in name_lower:
            item['category'] = 'зонт'
        elif 'раструб' in name_lower:
            item['category'] = 'раструб'
        elif 'каплеуловливатель' in name_lower:
            item['category'] = 'каплеулавливатель'
        elif 'корона' in name_lower:
            item['category'] = 'корона'
        elif 'привод' in name_lower or 'электропривод' in name_lower:
            item['category'] = 'привод'

import re

def replace_cyrillic_e_in_technical(name):
    # Заменяет кириллические е/Е на латинские в частях артикулов вида 6е/6Е (например AGVF370-6Е)
    return re.sub(r'6[еЕ](?=[\W_]|$)', lambda m: '6E' if m.group(0)[-1].isupper() else '6e', name)

for item in data:
    if 'name' in item and isinstance(item['name'], str):
        item['name'] = replace_cyrillic_e_in_technical(item['name'])
    if 'price' in item and isinstance(item['price'], str):
        item['price'] = item['price'].replace('\u00A0', '').replace(' ', '')

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'✅ Успешно конвертировано {len(data)} записей в файл: {output_file}')