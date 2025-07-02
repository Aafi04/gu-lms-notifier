import requests
import os
from bs4 import BeautifulSoup

# === CONFIG ===
LMS_URL = 'https://gulms.galgotiasuniversity.org/'
TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHANNEL_USERNAME")
GITHUB_REPO = os.getenv("REPO_NAME")
GITHUB_TOKEN = os.getenv("GH_PAT")
ANNOUNCEMENT_ISSUE_NUMBER = 3
# ==============

def get_latest_announcement():
    response = requests.get(LMS_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    post = soup.select_one('article.forum-post-container')
    if not post:
        return None

    # Title and time
    title = post.select_one('h3[data-region-content="forum-post-core-subject"]').text.strip()
    time = post.select_one('time').text.strip()

    # Content body text
    content_div = post.select_one('.post-content-container')
    content_text = content_div.get_text(separator='\n', strip=True) if content_div else ''

    # File links
    attachment_links = []
    for a in post.find_all('a', href=True):
        href = a['href']
        if 'pluginfile.php' in href:
            full_url = href if href.startswith('http') else LMS_URL + href.lstrip('/')
            filename = a.get_text(strip=True)
            attachment_links.append((full_url, filename))

    # Embedded images
    image_links = []
    for img in content_div.find_all('img', src=True) if content_div else []:
        src = img['src']
        if 'pluginfile.php' in src or src.startswith('http'):
            full_url = src if src.startswith('http') else LMS_URL + src.lstrip('/')
            image_links.append(full_url)

    full_message = f"## {title}\nTime: {time}\n\n{content_text}\n\nLink: {LMS_URL}"
    return full_message, attachment_links, image_links

def get_last_sent_from_github_issue():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{ANNOUNCEMENT_ISSUE_NUMBER}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers)
    return response.json().get("body", "").strip() if response.ok else ""

def save_last_sent_to_github_issue(text):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{ANNOUNCEMENT_ISSUE_NUMBER}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.patch(url, headers=headers, json={"body": text})
    if response.ok:
        print("✅ Last announcement updated in GitHub Issue.")
    else:
        print("⚠️ Failed to update GitHub Issue.")

def send_telegram_message(text, files=[], images=[]):
    # Send main message
    msg_response = requests.post(
        f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
        data={'chat_id': TELEGRAM_CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}
    )
    print("✅ Message sent to Telegram." if msg_response.ok else "⚠️ Failed to send Telegram message.")

    # Send attachments as documents
    for file_url, file_name in files:
        file_data = requests.get(file_url)
        if file_data.ok:
            print(f"📄 Sending file: {file_name}")
            requests.post(
                f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument',
                data={'chat_id': TELEGRAM_CHAT_ID},
                files={'document': (file_name, file_data.content)}
            )

    # Send images as photos
    for img_url in images:
        img_data = requests.get(img_url)
        if img_data.ok:
            print(f"🖼️ Sending image: {img_url}")
            requests.post(
                f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto',
                data={'chat_id': TELEGRAM_CHAT_ID},
                files={'photo': img_data.content}
            )

def main():
    result = get_latest_announcement()
    if not result:
        print("⚠️ No announcement found.")
        return

    latest_message, attachments, images = result
    last_sent = get_last_sent_from_github_issue()

    if latest_message != last_sent:
        print("✅ New announcement found. Sending to Telegram...")
        send_telegram_message(latest_message, files=attachments, images=images)
        save_last_sent_to_github_issue(latest_message)
    else:
        print("ℹ️ No new announcement.")

if __name__ == '__main__':
    main()
