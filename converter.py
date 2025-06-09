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

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'✅ Успешно конвертировано {len(data)} записей в файл: {output_file}')