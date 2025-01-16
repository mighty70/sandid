import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# Храним последние lobby_id для pc1 и pc2 в памяти
latest_lobby_id = {
    "pc1": None,
    "pc2": None
}

# Храним историю обращений, чтобы показать в визуальной таблице
lobby_history = []

@app.route('/lobby_id', methods=['POST'])
def handle_lobby_id():
    """Маршрут для приёма lobby_id от ПК."""
    data = request.json
    pc = data.get("pc")       # pc_name (pc1 или pc2)
    lobby_id = data.get("lobby_id")

    # Текущее время
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # Сохраняем в память
    if pc in latest_lobby_id:
        latest_lobby_id[pc] = lobby_id
    else:
        return jsonify({"status": "error", "message": "Unknown PC name"})

    # Проверяем, есть ли lobby_id для обоих ПК
    pc1_id = latest_lobby_id["pc1"]
    pc2_id = latest_lobby_id["pc2"]

    # Если оба ПК что-то прислали
    if pc1_id and pc2_id:
        if pc1_id == pc2_id:
            # Лобби совпало
            lobby_history.append({
                "timestamp": timestamp,
                "pc1_id": pc1_id,
                "pc2_id": pc2_id,
                "status": "match"
            })
            return jsonify({"status": "game_accepted"})
        else:
            # Лобби не совпало
            lobby_history.append({
                "timestamp": timestamp,
                "pc1_id": pc1_id,
                "pc2_id": pc2_id,
                "status": "no_match"
            })
            # В зависимости от логики — можно сразу сбрасывать, а можно ждать
            # Здесь для примера вернём "search_again", чтобы клиенты отклонили
            return jsonify({"status": "search_again"})
    else:
        # Один из ПК ещё не прислал lobby_id
        lobby_history.append({
            "timestamp": timestamp,
            "pc1_id": pc1_id,
            "pc2_id": pc2_id,
            "status": "waiting"
        })
        return jsonify({"status": None})

@app.route('/reset', methods=['POST'])
def reset_state():
    """
    Сброс состояния.
    Например, если хотите сбросить ожидание после отклонения игры,
    чтобы не висели старые lobby_id.
    """
    latest_lobby_id["pc1"] = None
    latest_lobby_id["pc2"] = None
    return "OK"

@app.route('/status')
def status_page():
    """
    Возвращает HTML-страницу с историей отправленных lobby_id и статусом.
    """
    # Формируем HTML-таблицу
    # Для удобства новые записи можно вывести сверху, сделаем reversed(lobby_history)
    table_html = """
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        table, th, td {
            border: 1px solid #444;
            border-collapse: collapse;
            padding: 8px;
            text-align: center;
        }
        th {
            background-color: #efefef;
        }
        .match {
            background-color: #c8e6c9; /* light green */
        }
        .no_match {
            background-color: #ffcdd2; /* light red */
        }
        .waiting {
            background-color: #fff9c4; /* light yellow */
        }
      </style>
    </head>
    <body>
      <h1>Lobby History</h1>
      <table>
        <tr>
          <th>Timestamp</th>
          <th>PC1 Lobby ID</th>
          <th>PC2 Lobby ID</th>
          <th>Status</th>
        </tr>
    """

    # Самая свежая запись будет первой (reversed)
    for entry in reversed(lobby_history):
        row_class = entry["status"]  # match / no_match / waiting
        table_html += f"""
        <tr class="{row_class}">
          <td>{entry['timestamp']}</td>
          <td>{entry['pc1_id']}</td>
          <td>{entry['pc2_id']}</td>
          <td>{entry['status']}</td>
        </tr>
        """

    table_html += """
      </table>
    </body>
    </html>
    """
    return table_html

if __name__ == '__main__':
    # Запускаем Flask-сервер на порту 5000 (можно изменить по необходимости)
    app.run(host='0.0.0.0', port=5000, debug=True)
