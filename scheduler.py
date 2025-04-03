import os
import time
import schedule
from linebot import LineBotApi
from linebot.models import TextSendMessage

# 從環境變數讀取 LINE Bot 設定
LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
USER_ID = os.getenv("LINE_USER_ID")

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

# 儲存提醒事項
reminders = [("12:30", "吃午餐"), ("18:00", "下班")]

# 發送提醒的函式
def send_reminder(task):
    try:
        line_bot_api.push_message(USER_ID, TextSendMessage(text=f"⏰ 記得哦！{task}"))
        print(f"提醒發送成功：{task}")
    except Exception as e:
        print(f"發送失敗：{e}")

# 設定排程
for time_str, task in reminders:
    schedule.every().day.at(time_str).do(send_reminder, task)

# 讓排程持續運行
if __name__ == "__main__":
    print("📢 提醒排程已啟動")
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每 60 秒檢查一次
import os
from linebot import LineBotApi
from linebot.models import TextSendMessage

LINE_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
USER_ID = os.getenv("LINE_USER_ID")

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

line_bot_api.push_message(USER_ID, TextSendMessage(text="測試訊息"))