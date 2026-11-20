# GU LMS Notifier

> **Project status: Retired / Archived**
>
> GU LMS Notifier is no longer running. After nearly three years of operation, the bot was retired when the university introduced an official email notification system for LMS announcements.
>
> The repository is being kept as an archive of the project and its journey.

## About the Project

GU LMS Notifier was a Python-based automation tool that monitored public announcements on the university's LMS portal and automatically delivered new notices to students through a Telegram channel.

I built this project during my **first year of university** after noticing a simple problem: important announcements were being posted on the LMS, but there was no notification system to tell students when something new had appeared.

As a result, students would sometimes miss notices simply because they hadn't checked the LMS at the right time.

So I built something to fix that.

The bot periodically checked the LMS for new announcements and forwarded them—including their content, images, and attachments—to Telegram.

What started as a small solution to a problem I personally noticed ended up being used by **around 700 students over the course of two years**.

---

## The Journey

The project remained operational for almost **three years**.

During that time, it went through roughly **5,000 automated workflow runs**, along with bug fixes, maintenance, and updates whenever changes to the university's LMS affected the scraper.

It wasn't a particularly large or complicated product, but it was the **first thing I built that solved a real problem and was actually used by people**.

That makes this repository important to me.

Eventually, in my final year, the university introduced an official email notification system for LMS announcements. Students no longer needed a separate Telegram bot to know when a new notice had been posted.

At that point, the problem this project existed to solve had been solved properly at the source.

So, after almost three years, **GU LMS Notifier was shut down.**

It served its purpose.

---

## What It Did

* Scraped the latest public announcement from the GU LMS homepage.
* Extracted the announcement title, timestamp, content, attachments, and images.
* Automatically posted new announcements to a Telegram channel.
* Sent associated files and images as Telegram documents/photos.
* Used a GitHub Issue to keep track of the last announcement sent and prevent duplicates.
* Ran automatically through GitHub Actions.
* Could also be triggered manually when required.

---

## How It Worked

### 1. LMS Scraper

The Python script fetched the LMS portal homepage and parsed the latest available announcement.

It extracted information such as:

* Title
* Publication time
* Announcement content
* Attachments
* Images

### 2. Telegram Delivery

When a new announcement was detected, the bot sent it to a Telegram channel.

Text content was formatted into a notification, while associated files and images were separately uploaded as documents or photos.

### 3. Duplicate Prevention

Because the project ran automatically, it needed a way to remember which announcement had already been sent.

Instead of maintaining a separate database, the project used a **GitHub Issue as lightweight persistent state**.

The latest processed announcement was stored there and checked on subsequent runs, preventing the bot from repeatedly sending the same notice.

### 4. Automation

A GitHub Actions workflow periodically executed the scraper.

This allowed the entire system to run without maintaining a dedicated server.

```text
GU LMS
   │
   ▼
Python Scraper
   │
   ├── No new announcement ──► Stop
   │
   ▼
New announcement detected
   │
   ├──► Send text to Telegram
   ├──► Send images/files
   │
   ▼
Update tracking issue on GitHub
```

---

## Tech Stack

* **Python** — scraping and bot logic
* **Telegram Bot API** — announcement delivery
* **GitHub Actions** — scheduled automation
* **GitHub Issues / API** — lightweight state tracking

---

## Repository Structure

```text
gu-lms-notifier/
├── scrape_and_send.py
├── requirements.txt
└── .github/
    └── workflows/
        └── notifier.yml
```

**`scrape_and_send.py`**
Main application responsible for scraping announcements, checking whether they had already been sent, and publishing them to Telegram.

**`requirements.txt`**
Python dependencies required by the project.

**`.github/workflows/notifier.yml`**
GitHub Actions workflow that periodically ran the notifier.

---

## Historical Setup

> The following information is preserved for documentation purposes. The project is retired and is no longer actively maintained.

The bot expected the following environment variables / GitHub Actions secrets:

```text
BOT_TOKEN
CHANNEL_USERNAME
REPO_NAME
GH_PAT
```

Where:

* `BOT_TOKEN` — Telegram bot token
* `CHANNEL_USERNAME` — destination Telegram channel
* `REPO_NAME` — GitHub repository in `owner/repo` format
* `GH_PAT` — GitHub Personal Access Token used for issue tracking

The announcement tracking issue number was configured through `ANNOUNCEMENT_ISSUE_NUMBER` in `scrape_and_send.py`.

Dependencies could be installed with:

```sh
pip install -r requirements.txt
```

And the script could be run locally with the required environment variables configured:

```sh
python scrape_and_send.py
```

---

## Retirement

**Status:** 🛑 Retired
**Operational period:** ~3 years
**Students reached:** ~700
**Automated workflow runs:** ~5,000

GU LMS Notifier was created because LMS announcements had no reliable notification mechanism for students.

It is being retired because that is no longer the case.

With an official email notification system now available for LMS notices, continuing to operate a parallel scraper and notification service is unnecessary.

The code will remain here, but the service itself has been stopped and will no longer be maintained.

---

## A Small Keepsake

This repository is staying on my GitHub for a reason.

GU LMS Notifier was one of my earliest projects. I built it in my first year because I saw a problem affecting students around me and thought I could solve it with code.

For nearly three years, it quietly ran in the background—checking the LMS, sending notices, occasionally breaking when the LMS changed, getting fixed, and going back to work.

Around 700 students ended up using it.

By my final year, the university had introduced its own notification system, and the little workaround I had built was no longer necessary.

There is something satisfying about retiring software because the problem it was created to solve no longer exists.

So this repository isn't being deleted.

It stays here as a reminder of the first thing I built that went beyond being a project on my computer.

**It was useful to someone.**

And it served its purpose.

---

## Author

Developed and maintained by **Aafi04**.

---

*This repository is archived as a record of the project. The bot is no longer operational and the code is not actively maintained.*
