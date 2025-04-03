import os
import time
import threading
import schedule
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 讀取環境變數
LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_SECRET = os.getenv("LINE_CHANNEL_SECRET")
USER_ID = os.getenv("LINE_USER_ID")

if not LINE_ACCESS_TOKEN or not LINE_SECRET or not USER_ID:
    raise ValueError("Missing LINE Bot API credentials")

print(f"LINE_ACCESS_TOKEN: {LINE_ACCESS_TOKEN}")
print(f"LINE_SECRET: {LINE_SECRET}")

# 設定 LINE Bot API
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_SECRET)

# 建立 Flask 應用程式
app = Flask(__name__)

# 儲存提醒事項（避免重複設定）
reminders = []

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
    user_message = event.message.text.strip()

    if user_message.startswith("*"):
        try:
            # 分割訊息，格式為：*時間 提醒內容
            _, time_str, task = user_message.split(" ", 2)
            # 將提醒存入清單，避免重複設定（可依需求做擴充）
            reminders.append((time_str, task))
            # 設定每天於指定時間發送提醒
            schedule.every().day.at(time_str).do(send_reminder, task)
            reply_text = f"✅ 已設定提醒：{task}（時間：{time_str}）"
        except Exception as e:
            print(f"Error in handle_message: {e}")
            reply_text = "⚠️ 設定提醒格式錯誤！請使用「*12:30 吃午餐」"
    else:
        reply_text = "💡 你可以輸入「*12:30 吃午餐」來設定提醒喔！"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

def send_reminder(task):
    try:
        print(f"📢 發送提醒：{task}")
        line_bot_api.push_message(USER_ID, TextSendMessage(text=f"⏰ 記得哦！{task}"))
        print("✅ 發送成功！")
    except Exception as e:
        print(f"🚨 發送失敗：{e}")

def run_scheduler():
    while True:
        print("🔄 定時排程執行中...")
        schedule.run_pending()
        time.sleep(1)

# 啟動排程背景執行緒
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
