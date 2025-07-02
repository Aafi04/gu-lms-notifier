import requests
import os
from bs4 import BeautifulSoup

# === CONFIG ===
LMS_URL = 'https://gulms.galgotiasuniversity.org/'
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHANNEL_USERNAME")
GITHUB_REPO = os.getenv("REPO_NAME")
GITHUB_TOKEN = os.getenv("GH_PAT")
ISSUE_NUMBER = 3  # GitHub Issue number
# ==============

def get_latest_announcement():
    response = requests.get(LMS_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    title_element = soup.select_one('h3[data-region-content="forum-post-core-subject"]')
    time_element = soup.select_one('time')

    if not title_element or not time_element:
        return None, []

    title = title_element.text.strip()
    timestamp = time_element.text.strip()
    full_announcement = f"## TEST -- {title}\nTime: {timestamp}\nLink: {LMS_URL}"


    # Find all file attachments
    attachments = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith("/pluginfile"):
            file_url = "https://gulms.galgotiasuniversity.org" + href
            attachments.append(file_url)

    return full_announcement, attachments

def get_last_sent_from_github_issue():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{ISSUE_NUMBER}"
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
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{ISSUE_NUMBER}"
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

def send_text_message(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'Markdown'
    }
    requests.post(url, data=payload)

def send_attachments(attachments):
    for file_url in attachments:
        filename = file_url.split('/')[-1].split('?')[0]
        ext = filename.lower().split('.')[-1]

        api_url = ''
        payload_key = ''
        if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            api_url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto'
            payload_key = 'photo'
        else:
            api_url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument'
            payload_key = 'document'

        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            payload_key: file_url
        }
        r = requests.post(api_url, data=payload)
        if r.ok:
            print(f"✅ Sent {filename}")
        else:
            print(f"⚠️ Failed to send {filename}: {r.text}")

def main():
    latest, attachments = get_latest_announcement()
    if latest is None:
        print("⚠️ No announcement found.")
        return

    last_sent = get_last_sent_from_github_issue()

    if latest != last_sent:
        print("✅ New announcement found. Sending to Telegram...")
        send_text_message(latest)
        send_attachments(attachments)
        save_last_sent_to_github_issue(latest)
    else:
        print("ℹ️ No new announcement.")

if __name__ == '__main__':
    main()
