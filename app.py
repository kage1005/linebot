from flask import Flask, request, jsonify
# 建立 Flask 伺服器
app = Flask(__name__)


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
import os

# 設定你的 LINE Bot 資訊
LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_SECRET = os.getenv("LINE_CHANNEL_SECRET")
USER_ID = os.getenv("LINE_USER_ID")

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_SECRET)

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

# 這個函式會發送提醒
def send_reminder(task):
    line_bot_api.push_message(USER_ID, TextSendMessage(text=f"⏰ 記得哦！{task}"))

import datetime

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()

    if user_message.startswith("*"):
        try:
            # 分割訊息，格式為：*時間 提醒內容
            _, time_str, task = user_message.split(" ", 2)
            reminders.append((time_str, task))
            schedule.every().day.at(time_str).do(send_reminder, task)
            reply_text = f"✅ 已設定提醒：{task}（時間：{time_str}）"
        except Exception as e:
            print(f"Error setting reminder: {e}")
            reply_text = "⚠️ 設定提醒格式錯誤！請使用「*12:30 吃午餐」"
    else:
        reply_text = "💡 你可以輸入「*12:30 吃午餐」來設定提醒喔！"

    # 取得目前伺服器時間並格式化
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reply_text += f"\n目前伺服器時間：{current_time}"
    # 回報LINE ID

    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text=reply_text),
            TextSendMessage(text=f"你的 User ID 是：{USER_ID}")
        ]
    )

# 啟動排程執行緒
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


# 讓排程在背景執行
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    app.run(port=5000)
