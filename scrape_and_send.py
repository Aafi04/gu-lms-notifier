import os
import requests
from bs4 import BeautifulSoup

# === CONFIG ===
LMS_URL = 'https://gulms.galgotiasuniversity.org/'
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHANNEL_USERNAME")
STATE_FILE = 'last_announcement.txt'
# ==============

def get_latest_announcement():
    response = requests.get(LMS_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the announcement title and date
    title_element = soup.select_one('h3[data-region-content="forum-post-core-subject"]')
    time_element = soup.select_one('time')

    if not title_element or not time_element:
        return None

    title = title_element.text.strip()
    timestamp = time_element.text.strip()
    full_announcement = f"## {title}\nTime: {timestamp}\nLink: https://gulms.galgotiasuniversity.org/"


    return full_announcement

def get_last_sent():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return f.read().strip()
    return ''

def save_last_sent(text):
    with open(STATE_FILE, 'w') as f:
        f.write(text)

def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }
    requests.post(url, data=payload)

def main():
    latest = get_latest_announcement()
    if latest is None:
        print("⚠️ No announcement found.")
        return

    last_sent = get_last_sent()

    if latest != last_sent:
        print("✅ New announcement found. Sending to Telegram...")
        send_telegram_message(latest)
        save_last_sent(latest)
    else:
        print("ℹ️ No new announcement.")

if __name__ == '__main__':
    main()
