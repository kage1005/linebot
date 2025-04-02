from flask import Flask, request, jsonify

app = Flask(__name__)

reminders = []

@app.route('/set_reminder', methods=['POST'])
def set_reminder():
    data = request.get_json()
    task = data.get('task')
    date = data.get('date')
    time = data.get('time')
    
    if not task or not date or not time:
        return jsonify({"error": "缺少必要參數"}), 400

    reminders.append({"task": task, "date": date, "time": time})
    return jsonify({"message": f"已設定提醒: {task}，時間: {date} {time}"})
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import schedule
import time
import threading

import os  # 引入 os 模組來讀取環境變數

# 從環境變數讀取 LINE Bot 的 API Key 和 Secret
LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# 確保變數有成功讀取
if not LINE_ACCESS_TOKEN or not LINE_SECRET:
    raise ValueError("Missing LINE Bot API credentials")

# 設定 Line Bot API
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_SECRET)

# 建立 Flask 伺服器
app = Flask(__name__)

# 儲存提醒事項
reminders = []

# 處理 LINE 訊息
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK", 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text

    # 設定提醒格式：「提醒 設定時間 內容」
    if user_message.startswith("*"):
        try:
            _, time_str, task = user_message.split(" ", 2)
            reminders.append((time_str, task))
            schedule.every().day.at(time_str).do(send_reminder, task)
            reply_text = f"✅ 已設定提醒：{task}（時間：{time_str}）"
        except:
            reply_text = "⚠️ 設定提醒格式錯誤！請使用「*12:30 吃午餐」"
    else:
        reply_text = "💡 你可以輸入「*12:30 吃午餐」來設定提醒喔！"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# 這個函式會發送提醒
def send_reminder(task):
    line_bot_api.push_message(USER_ID, TextSendMessage(text=f"⏰ 記得哦！{task}"))

# 啟動排程執行緒
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# 讓排程在背景執行
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    app.run(port=5000)
