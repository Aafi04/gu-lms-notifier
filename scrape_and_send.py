import requests
import os
from bs4 import BeautifulSoup

# === CONFIG ===
LMS_URL = 'https://gulms.galgotiasuniversity.org/'
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHANNEL_USERNAME")
GITHUB_REPO = os.getenv("REPO_NAME")  # e.g., username/repo
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")      # Automatically set in GitHub Actions
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

def get_last_sent_from_github_issue():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/1"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers)
    if response.ok:
        return response.json().get("body", "").strip()
    else:
        print("⚠️ Failed to fetch last sent announcement from GitHub Issue.")
        return ""

def save_last_sent_to_github_issue(text):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/1"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    data = {"body": text}
    response = requests.patch(url, headers=headers, json=data)
    if response.ok:
        print("✅ Last announcement updated in GitHub Issue.")
    else:
        print("⚠️ Failed to update GitHub Issue.")

def send_telegram_message(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }
    response = requests.post(url, data=payload)
    if response.ok:
        print("✅ Message sent to Telegram.")
    else:
        print("⚠️ Failed to send Telegram message.")

def main():
    latest = get_latest_announcement()
    if latest is None:
        print("⚠️ No announcement found.")
        return

    last_sent = get_last_sent_from_github_issue()

    if latest != last_sent:
        print("✅ New announcement found. Sending to Telegram...")
        send_telegram_message(latest)
        save_last_sent_to_github_issue(latest)
    else:
        print("ℹ️ No new announcement.")

if __name__ == '__main__':
    main()
