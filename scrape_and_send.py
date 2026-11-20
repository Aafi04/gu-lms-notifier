import requests
import os
import re
from bs4 import BeautifulSoup


# === CONFIG ===

LMS_URL = os.getenv("LMS_URL", "https://lms.university.edu/")

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("CHANNEL_USERNAME")

GITHUB_REPO = os.getenv("REPO_NAME")
GITHUB_TOKEN = os.getenv("GH_PAT")

ANNOUNCEMENT_ISSUE_NUMBER = 3

# ==============


def get_latest_announcement():
    try:
        response = requests.get(LMS_URL, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Failed to fetch LMS: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    post = soup.select_one('article.forum-post-container')
    if not post:
        print("⚠️ No announcement post found on LMS.")
        return None

    post_id = post.get('data-post-id') or (
        post.get('id')[1:]
        if post.get('id') and post.get('id').startswith('p')
        else None
    )

    title_el = post.select_one(
        'h3[data-region-content="forum-post-core-subject"]'
    )
    title = title_el.text.strip() if title_el else ''

    time_el = post.select_one('time')
    time = time_el.text.strip() if time_el else ''

    content_div = post.select_one('.post-content-container')

    attachment_links = []

    for a in post.find_all('a', href=True):
        href = a['href']

        if 'pluginfile.php' in href:
            full_url = (
                href
                if href.startswith('http')
                else LMS_URL + href.lstrip('/')
            )

            filename = a.get_text(strip=True)

            attachment_links.append((full_url, filename))

    image_links = []

    if content_div:
        for img in content_div.find_all('img', src=True):
            src = img['src']

            if 'pluginfile.php' in src or src.startswith('http'):
                full_url = (
                    src
                    if src.startswith('http')
                    else LMS_URL + src.lstrip('/')
                )

                image_links.append(full_url)

    full_message = (
        f"{title}\n"
        f"Time: {time}\n\n"
        f"Link: {LMS_URL}"
    )

    print(f"Latest LMS post ID: {post_id}")
    print(f"Latest LMS title: {title}")
    print(f"Latest LMS time: {time}")

    return post_id, full_message, attachment_links, image_links


def get_last_sent_from_github_issue():
    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_REPO}/issues/{ANNOUNCEMENT_ISSUE_NUMBER}"
    )

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )
    except requests.RequestException as e:
        print(f"❌ Failed to read GitHub Issue: {e}")
        raise

    if not response.ok:
        print(
            f"❌ Failed to read GitHub Issue. "
            f"Status: {response.status_code}"
        )
        print(f"GitHub response: {response.text}")
        response.raise_for_status()

    body = response.json().get("body", "")

    m = re.match(
        r'^ID:(\d+)\s*\n(.*)$',
        body,
        re.DOTALL
    )

    if m:
        return m.group(1), m.group(2).strip()

    return None, body.strip()


def save_last_sent_to_github_issue(text, post_id=None):
    url = (
        f"https://api.github.com/repos/"
        f"{GITHUB_REPO}/issues/{ANNOUNCEMENT_ISSUE_NUMBER}"
    )

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    body_to_save = (
        f"ID:{post_id}\n\n{text}"
        if post_id
        else text
    )

    try:
        response = requests.patch(
            url,
            headers=headers,
            json={"body": body_to_save},
            timeout=30
        )
    except requests.RequestException as e:
        print(f"❌ Failed to update GitHub Issue: {e}")
        raise

    if response.ok:
        print("✅ Last announcement updated in GitHub Issue.")
    else:
        print(
            f"❌ Failed to update GitHub Issue. "
            f"Status: {response.status_code}"
        )
        print(f"GitHub response: {response.text}")
        response.raise_for_status()


def send_telegram_message(text, files=None, images=None):
    if files is None:
        files = []

    if images is None:
        images = []

    # -------------------------------------------------
    # Send main text message
    # -------------------------------------------------

    try:
        msg_response = requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
            data={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': text
            },
            timeout=30
        )
    except requests.RequestException as e:
        print(f"❌ Telegram request failed: {e}")
        return False

    print(f"Telegram status: {msg_response.status_code}")
    print(f"Telegram response: {msg_response.text}")

    if not msg_response.ok:
        print("❌ Failed to send Telegram message.")
        return False

    print("✅ Message sent to Telegram.")

    # -------------------------------------------------
    # Send attachments
    # -------------------------------------------------

    for file_url, file_name in files:
        try:
            file_data = requests.get(
                file_url,
                timeout=30
            )

            if not file_data.ok:
                print(
                    f"⚠️ Failed to download file: {file_name} "
                    f"(status {file_data.status_code})"
                )
                continue

            print(f"📄 Sending file: {file_name}")

            file_response = requests.post(
                f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument',
                data={
                    'chat_id': TELEGRAM_CHAT_ID
                },
                files={
                    'document': (
                        file_name,
                        file_data.content
                    )
                },
                timeout=60
            )

            if file_response.ok:
                print(f"✅ File sent: {file_name}")
            else:
                print(f"⚠️ Failed to send file: {file_name}")
                print(f"Telegram response: {file_response.text}")

        except requests.RequestException as e:
            print(
                f"⚠️ Failed to send file {file_name}: {e}"
            )

    # -------------------------------------------------
    # Send images
    # -------------------------------------------------

    for img_url in images:
        try:
            img_data = requests.get(
                img_url,
                timeout=30
            )

            if not img_data.ok:
                print(
                    f"⚠️ Failed to download image "
                    f"(status {img_data.status_code}): {img_url}"
                )
                continue

            print(f"🖼️ Sending image: {img_url}")

            image_response = requests.post(
                f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto',
                data={
                    'chat_id': TELEGRAM_CHAT_ID
                },
                files={
                    'photo': img_data.content
                },
                timeout=60
            )

            if image_response.ok:
                print("✅ Image sent.")
            else:
                print("⚠️ Failed to send image.")
                print(f"Telegram response: {image_response.text}")

        except requests.RequestException as e:
            print(f"⚠️ Failed to send image: {e}")

    return True


def main():
    # -------------------------------------------------
    # Get latest LMS announcement
    # -------------------------------------------------

    result = get_latest_announcement()

    if not result:
        print("⚠️ No announcement found.")
        return

    latest_post_id, latest_message, attachments, images = result

    # -------------------------------------------------
    # Get previously sent announcement
    # -------------------------------------------------

    last_id, last_body = get_last_sent_from_github_issue()

    print(f"Last stored post ID: {last_id}")

    # -------------------------------------------------
    # Check whether this is a new announcement
    # -------------------------------------------------

    if last_id:
        if (
            latest_post_id
            and str(latest_post_id) == str(last_id)
        ):
            print(
                "ℹ️ No new announcement "
                "(same post id)."
            )
            return

        print(
            "✅ New announcement found "
            "(post id differs)."
        )

    else:
        if latest_message == last_body:
            print("ℹ️ No new announcement.")
            return

        print("✅ New announcement found.")

    # -------------------------------------------------
    # Send to Telegram
    # -------------------------------------------------

    print("📨 Sending announcement to Telegram...")

    telegram_success = send_telegram_message(
        latest_message,
        files=attachments,
        images=images
    )

    # -------------------------------------------------
    # IMPORTANT:
    # Only update GitHub AFTER Telegram succeeds.
    # -------------------------------------------------

    if not telegram_success:
        print(
            "❌ Telegram notification failed."
        )
        print(
            "❌ GitHub Issue will NOT be updated."
        )
        raise RuntimeError(
            "Telegram notification failed."
        )

    # -------------------------------------------------
    # Telegram succeeded, so save the post ID.
    # -------------------------------------------------

    save_last_sent_to_github_issue(
        latest_message,
        latest_post_id
    )

    print("✅ Notification process completed successfully.")


if __name__ == '__main__':
    main()
