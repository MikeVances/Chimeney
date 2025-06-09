from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Сервер запущен. Готов к работе!"


# Новый маршрут /predict
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json

    # Путь к файлу Excel
    excel_path = os.path.join(os.getcwd(), 'Перечень и цены комплектующих шахт.xlsx')
    df = pd.read_excel(excel_path)

    # Пример фильтрации по ключевым словам в наименовании
    filtered = df[df['Наименование'].str.contains("VBV", case=False, na=False)]

    result = filtered[['Артикул', 'Наименование', 'Цена']].to_dict(orient='records')
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)