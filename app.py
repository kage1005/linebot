import os
import time
import threading
import schedule
from flask import Flask, request
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot import LineBotApi, WebhookHandler
import os
# 讀取環境變數
LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_SECRET = os.getenv("LINE_CHANNEL_SECRET")
USER_ID = os.getenv("LINE_USER_ID")

if not LINE_ACCESS_TOKEN or not LINE_SECRET:
    raise ValueError("Missing LINE Bot API credentials")

# 設定 Line Bot API
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_SECRET)


# 確保變數有成功讀取
if not LINE_ACCESS_TOKEN or not LINE_SECRET or not USER_ID:
    raise ValueError("Missing LINE Bot API credentials")

def send_reminder(task):
    try:
        print(f"📢 發送提醒：{task}")
        line_bot_api.push_message(USER_ID, TextSendMessage(text=f"⏰ 記得哦！{task}"))
        print("✅ 發送成功！")
    except Exception as e:
        print(f"🚨 發送失敗：{e}")  # ← 如果這裡有錯誤，請貼給我看
send_reminder("測試提醒")

# 設定 Line Bot API
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_SECRET)

# 建立 Flask 伺服器
app = Flask(__name__)

# 儲存提醒事項
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
    user_message = event.message.text

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

def send_reminder(task):
    line_bot_api.push_message(USER_ID, TextSendMessage(text=f"⏰ 記得哦！{task}"))

# 背景執行排程
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
import schedule
import time
import threading

# 這個函式會發送提醒
def send_reminder(task):
    print(f"發送提醒中：{task}")  # ← 這裡加上 debug 訊息
    line_bot_api.push_message(USER_ID, TextSendMessage(text=f"⏰ 記得哦！{task}"))

# 啟動排程執行緒
def run_scheduler():
    while True:
        print("🔄 定時排程執行中...")  # ← 這裡加上 debug 訊息
        schedule.run_pending()
        time.sleep(1)

# 讓排程在背景執行
threading.Thread(target=run_scheduler, daemon=True).start()

print(f"LINE_ACCESS_TOKEN: {LINE_ACCESS_TOKEN}")
print(f"LINE_SECRET: {LINE_SECRET}")