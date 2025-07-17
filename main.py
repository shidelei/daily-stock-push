import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import requests
import tushare as ts
from datetime import datetime

# 获取环境变量
tushare_token = os.getenv("TUSHARE_TOKEN")
email_pass = os.getenv("EMAIL_PASS")
email_to = os.getenv("EMAIL_TO")
dingtalk_webhook = os.getenv("DINGTALK_WEBHOOK")

# 初始化 tushare
ts.set_token(tushare_token)
pro = ts.pro_api()

def fetch_top_stocks(limit=5):
    df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market,list_date')
    df = df[df['list_date'] < datetime.now().strftime("%Y%m%d")]
    return df.head(limit)

def send_email(content):
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['From'] = Header("Stock Bot", 'utf-8')
    msg['To'] = Header("User", 'utf-8')
    msg['Subject'] = Header('每日优选股票推送', 'utf-8')

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(email_to, email_pass)
        server.sendmail(email_to, [email_to], msg.as_string())
        server.quit()
    except Exception as e:
        print("邮件发送失败:", e)

def send_dingtalk(content):
    headers = {"Content-Type": "application/json"}
    data = {"msgtype": "text", "text": {"content": content}}
    try:
        requests.post(dingtalk_webhook, json=data, headers=headers)
    except Exception as e:
        print("钉钉发送失败:", e)

if __name__ == "__main__":
    stocks = fetch_top_stocks()
    text = "【今日优选股票】\n" + "\n".join(stocks['name'] + " (" + stocks['symbol'] + ")")
    send_email(text)
    send_dingtalk(text)
