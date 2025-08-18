# GU LMS Notifier

A Python-based automation tool that scrapes the latest public announcements from Galgotias University's LMS homepage and posts them to a Telegram channel. It also tracks sent announcements using a GitHub Issue to avoid duplicate notifications.

---

## Features

- Scrapes the latest announcement from the GU LMS homepage.
- Sends announcement details, attachments, and images to a Telegram channel.
- Tracks the last sent announcement using a GitHub Issue (prevents duplicate posts).
- Automated via GitHub Actions (runs every 5 minutes or on manual trigger).

---

## How It Works

1. **Scraping:**
   - The script fetches the LMS homepage and parses the latest announcement, including title, time, content, attachments, and images.
2. **Telegram Notification:**
   - Sends the announcement to a specified Telegram channel using a bot.
   - Files and images are sent as documents/photos.
3. **GitHub Issue Tracking:**
   - Stores the last sent announcement in a GitHub Issue to prevent reposting the same content.
4. **Automation:**
   - GitHub Actions workflow runs the script every 5 minutes or on manual request.

---

## Setup Instructions

### 1. Fork/Clone the Repository

```sh
git clone https://github.com/<your-username>/gu-lms-notifier.git
cd gu-lms-notifier
```

### 2. Create a Telegram Bot & Channel

- Create a bot via [BotFather](https://t.me/BotFather) and get the token.
- Create a Telegram channel and add your bot as an admin.
- Get your channel username (e.g., `@your_channel_name`).

### 3. Prepare GitHub Secrets

Go to your repository's **Settings > Secrets and variables > Actions** and add the following secrets:

- `BOT_TOKEN` — Telegram bot token
- `CHANNEL_USERNAME` — Telegram channel username (e.g., `@your_channel_name`)
- `REPO_NAME` — Your repo name in the format `owner/repo` (e.g., `Aafi04/gu-lms-notifier`)
- `GH_PAT` — GitHub Personal Access Token (with `repo` scope)

### 4. Set Up Announcement Issue

- Create a public issue in your repo (e.g., Issue #3) to store the last sent announcement.
- Update `ANNOUNCEMENT_ISSUE_NUMBER` in `scrape_and_send.py` if you use a different issue number.

### 5. Install Dependencies Locally (Optional)

```sh
pip install -r requirements.txt
```

### 6. Run Locally (Optional)

Set environment variables (or use a `.env` file):

```sh
set BOT_TOKEN=your_bot_token
set CHANNEL_USERNAME=@your_channel_name
set REPO_NAME=owner/repo
set GH_PAT=your_github_pat
python scrape_and_send.py
```

### 7. GitHub Actions Automation

- The workflow in `.github/workflows/notifier.yml` will run the script every 5 minutes using the secrets you configured.

---

## File Overview

- `scrape_and_send.py` — Main script for scraping and notification.
- `requirements.txt` — Python dependencies.
- `.github/workflows/notifier.yml` — GitHub Actions workflow for automation.

---

## Security & Privacy

- **No secrets are stored in code.** All credentials are passed via environment variables or GitHub secrets.
- **Do not commit your `.env` file or secret values.**
- **Check the LMS terms of service** before scraping or redistributing content.

---

## License

Specify your license here (e.g., MIT, Apache-2.0).

---

## Contributing

Pull requests and suggestions are welcome! Please open an issue for major changes.

---

## Troubleshooting

- Ensure all secrets are set correctly in GitHub.
- Check the issue number in `scrape_and_send.py` matches your tracking issue.
- Telegram bot must be an admin in your channel.
- For errors, check GitHub Actions logs and Telegram bot messages.

---

## Credits

Developed by [Aafi04](https://github.com/Aafi04) and contributors.
