from flask import Flask, request, jsonify, render_template_string
import time

app = Flask(__name__)

# ======================================
#  Глобальные переменные в памяти
# ======================================
# Храним последние Lobby ID от PC1 и PC2
latest_lobby_id = {
    "pc1": None,
    "pc2": None
}

# Храним историю обращений, чтобы отобразить
lobby_history = []


# ======================================
#  Маршрут: Приём Lobby ID
# ======================================
@app.route('/lobby_id', methods=['POST'])
def handle_lobby_id():
    """
    Принимает JSON вида:
    {
      "pc": "pc1",
      "lobby_id": "12345"
    }
    """
    data = request.json
    pc = data.get("pc")
    lobby_id = data.get("lobby_id")

    # Фиксируем текущее время (чтобы записать в историю)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    # Проверяем, что pc корректное (pc1 / pc2)
    if pc not in latest_lobby_id:
        return jsonify({"status": "error", "message": "Unknown PC name"})

    # Запоминаем для pc1/pc2
    latest_lobby_id[pc] = lobby_id

    # Извлекаем текущее состояние для обоих
    pc1_id = latest_lobby_id["pc1"]
    pc2_id = latest_lobby_id["pc2"]

    # Если оба ПК уже что-то прислали
    if pc1_id and pc2_id:
        if pc1_id == pc2_id:
            # Совпало - записываем в историю как match
            lobby_history.append({
                "timestamp": timestamp,
                "pc1_id": pc1_id,
                "pc2_id": pc2_id,
                "status": "match"
            })
            return jsonify({"status": "game_accepted"})
        else:
            # Не совпало - записываем в историю как no_match
            lobby_history.append({
                "timestamp": timestamp,
                "pc1_id": pc1_id,
                "pc2_id": pc2_id,
                "status": "no_match"
            })
            # Возвращаем «search_again», чтобы клиент отклонил
            return jsonify({"status": "search_again"})
    else:
        # Один из ПК ещё не прислал Lobby ID - статус waiting
        lobby_history.append({
            "timestamp": timestamp,
            "pc1_id": pc1_id,
            "pc2_id": pc2_id,
            "status": "waiting"
        })
        return jsonify({"status": None})


# ======================================
#  Маршрут: Сброс состояния
# ======================================
@app.route('/reset', methods=['POST'])
def reset_state():
    """
    Сбрасываем последние Lobby ID,
    чтобы начать «с чистого листа».
    """
    latest_lobby_id["pc1"] = None
    latest_lobby_id["pc2"] = None
    return "OK"


# ======================================
#  Маршрут: Шикарная визуализация
# ======================================
@app.route('/status')
def fancy_status():
    """
    Страница с крупными панелями для PC1 и PC2,
    а снизу блок «History» (последние записи).
    """
    # Текущий lobby_id (или «—», если None)
    pc1_id = latest_lobby_id["pc1"] or "—"
    pc2_id = latest_lobby_id["pc2"] or "—"

    # Для примера - показываем последние 5 записей в истории
    recent_history = lobby_history[-5:] if lobby_history else []

    # HTML-шаблон
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Lobby Status</title>
  <style>
    body {
      background: #f0f0f0;
      font-family: "Segoe UI", Arial, sans-serif;
      margin: 0; 
      padding: 0;
      display: flex; 
      flex-direction: column;
      align-items: center; 
      justify-content: flex-start;
    }
    h1 {
      margin-top: 30px; 
      font-size: 28px;
    }
    .board {
      display: flex;
      gap: 50px;
      margin-top: 20px;
    }
    .panel {
      background: #222;
      color: #fff;
      width: 300px;
      border-radius: 15px;
      padding: 20px;
      box-shadow: 0 0 10px rgba(0,0,0,0.3);
      display: flex;
      flex-direction: column;
      align-items: center;
    }
    .circle {
      width: 100px; 
      height: 100px;
      border: 4px solid #555;
      border-radius: 50%;
      display: flex; 
      align-items: center; 
      justify-content: center;
      font-size: 32px;
      margin-bottom: 15px;
      background: linear-gradient(to bottom, #333, #111);
    }
    .label {
      font-size: 14px;
      color: #bbb;
      margin-top: 8px;
    }
    .value {
      font-size: 18px; 
      margin-top: 4px;
      color: #0f0;  /* Зеленый для контраста */
    }
    .history-panel {
      margin-top: 30px;
      background: #fff;
      width: 650px;
      border-radius: 15px;
      padding: 20px;
      box-shadow: 0 0 10px rgba(0,0,0,0.2);
    }
    .history-panel h2 {
      margin-top: 0;
      color: #333;
    }
    .history {
      margin-top: 10px;
      width: 100%;
      border-top: 1px solid #ccc;
      padding-top: 10px;
    }
    .history-item {
      font-size: 14px;
      margin: 5px 0;
      line-height: 1.4;
    }
    .status-match { color: #4caf50; }   /* зеленый */
    .status-no_match { color: #e53935; } /* красный */
    .status-waiting { color: #ffb300; }  /* желтый */
  </style>
</head>
<body>
  <h1>Dota Lobby Status</h1>
  
  <!-- Две «панели» - для PC1 и PC2 -->
  <div class="board">
    <!-- Левая панель: PC1 -->
    <div class="panel">
      <div class="circle">PC1</div>
      <div class="label">Last Found Lobby ID</div>
      <div class="value">{{ pc1_id }}</div>
    </div>

    <!-- Правая панель: PC2 -->
    <div class="panel">
      <div class="circle">PC2</div>
      <div class="label">Last Found Lobby ID</div>
      <div class="value">{{ pc2_id }}</div>
    </div>
  </div>

  <!-- Блок истории -->
  <div class="history-panel">
    <h2>Recent History</h2>
    <div class="history">
      {% if recent_history %}
        {% for entry in recent_history %}
          <div class="history-item">
            <strong>{{ entry.timestamp }}</strong> — 
            PC1: {{ entry.pc1_id or '—' }}, 
            PC2: {{ entry.pc2_id or '—' }}
            <span class="status-{{ entry.status }}">[{{ entry.status }}]</span>
          </div>
        {% endfor %}
      {% else %}
        <p>Нет записей</p>
      {% endif %}
    </div>
  </div>

</body>
</html>
"""
    return render_template_string(
        html_template,
        pc1_id=pc1_id,
        pc2_id=pc2_id,
        recent_history=recent_history
    )


# ======================================
#  Точка входа
# ======================================
if __name__ == '__main__':
    # Запускаем Flask-сервер на 5000 порту (можно изменить)
    app.run(host='0.0.0.0', port=5000, debug=True)
