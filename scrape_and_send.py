import requests
import os
import re
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

    post_id = post.get('data-post-id') or (post.get('id')[1:] if post.get('id') and post.get('id').startswith('p') else None)
    title_el = post.select_one('h3[data-region-content="forum-post-core-subject"]')
    title = title_el.text.strip() if title_el else ''
    time_el = post.select_one('time')
    time = time_el.text.strip() if time_el else ''

    content_div = post.select_one('.post-content-container')

    attachment_links = []
    for a in post.find_all('a', href=True):
        href = a['href']
        if 'pluginfile.php' in href:
            full_url = href if href.startswith('http') else LMS_URL + href.lstrip('/')
            filename = a.get_text(strip=True)
            attachment_links.append((full_url, filename))

    image_links = []
    for img in content_div.find_all('img', src=True) if content_div else []:
        src = img['src']
        if 'pluginfile.php' in src or src.startswith('http'):
            full_url = src if src.startswith('http') else LMS_URL + src.lstrip('/')
            image_links.append(full_url)

    full_message = f"{title}\nTime: {time}\n\nLink: {LMS_URL}"
    return post_id, full_message, attachment_links, image_links


def get_last_sent_from_github_issue():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{ANNOUNCEMENT_ISSUE_NUMBER}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers)
    if not response.ok:
        return None, ""

    body = response.json().get("body", "")
    m = re.match(r'^ID:(\d+)\s*\n(.*)$', body, re.DOTALL)
    if m:
        return m.group(1), m.group(2).strip()
    else:
        return None, body.strip()


def save_last_sent_to_github_issue(text, post_id=None):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{ANNOUNCEMENT_ISSUE_NUMBER}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    body_to_save = f"ID:{post_id}\n\n{text}" if post_id else text
    response = requests.patch(url, headers=headers, json={"body": body_to_save})
    if response.ok:
        print("✅ Last announcement updated in GitHub Issue.")
    else:
        print("⚠️ Failed to update GitHub Issue.")


def send_telegram_message(text, files=None, images=None):
    if files is None:
        files = []
    if images is None:
        images = []

    msg_response = requests.post(
        f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
        data={'chat_id': TELEGRAM_CHAT_ID, 'text': text, 'parse_mode': 'Markdown'}
    )
    print("✅ Message sent to Telegram." if msg_response.ok else "⚠️ Failed to send Telegram message.")

    for file_url, file_name in files:
        file_data = requests.get(file_url)
        if file_data.ok:
            print(f"📄 Sending file: {file_name}")
            requests.post(
                f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument',
                data={'chat_id': TELEGRAM_CHAT_ID},
                files={'document': (file_name, file_data.content)}
            )

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

    latest_post_id, latest_message, attachments, images = result
    last_id, last_body = get_last_sent_from_github_issue()

    if last_id:
        if latest_post_id and str(latest_post_id) == str(last_id):
            print("ℹ️ No new announcement (same post id).")
            return
        else:
            print("✅ New announcement found (post id differs). Sending to Telegram...")
            send_telegram_message(latest_message, files=attachments, images=images)
            save_last_sent_to_github_issue(latest_message, latest_post_id)
    else:
        if latest_message != last_body:
            print("✅ New announcement found. Sending to Telegram...")
            send_telegram_message(latest_message, files=attachments, images=images)
            save_last_sent_to_github_issue(latest_message, latest_post_id)
        else:
            print("ℹ️ No new announcement.")


if __name__ == '__main__':
    main()
