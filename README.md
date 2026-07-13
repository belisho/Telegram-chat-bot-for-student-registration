# MHSS-KIDDS Registration Bot

A Telegram bot for **MHSS-KIDDS** Sunday school that lets you check a student's
registration status and register new students. Data is stored in a Google Sheet
that is shared with a Google Form, so entries from both the form and the bot
live in the same place.

## Features

- `/start` shows the logo and a welcome message, then asks for a student name.
- Fuzzy name search against the Google Sheet; similar students are shown as
  inline buttons, along with a **Register new student** button.
- Selecting a student shows their **full name**, **level of education** and
  **assigned class**.
- New registration is gated by a configurable limit (default **270** rows).
- Multi-step registration form: First Name, Father Name, Phone, Age, Level of
  Education (inline buttons) and Waiting Family (Yes/No).
- Input validation:
  - Name: exactly three names separated by spaces (First Middle Last).
  - Phone: starts with `09`, `07`, `2519`, `2517`, `+2519` or `+2517` followed
    by 8 digits.
  - Age: between 7 and 16 inclusive.
- All user-facing text lives in [`config/messages.py`](config/messages.py) and is
  easy to edit/translate.

## Project structure

```
Telegram Bot/
  run.py                     # entry point: python run.py
  requirements.txt
  .env.example  .gitignore
  assets/logo.png            # placeholder logo (replace with the real one)
  config/
    settings.py              # env loading, limit, sheet schema
    messages.py              # all bot text + EDUCATION_LEVELS list
  src/
    bot.py                   # builds the Application and registers handlers
    handlers/
      start.py               # /start, /help, /cancel
      status.py              # name search + result selection
      register.py            # registration form
      states.py              # conversation state constants
    services/
      sheets.py              # Google Sheets read/count/append (gspread)
      matching.py            # fuzzy name matching (rapidfuzz)
    keyboards/inline.py      # inline keyboards
    utils/validators.py      # name / phone / age validation
```

## 1. Prerequisites

- Python 3.11+
- A Telegram bot token
- A Google Cloud service account with access to your Google Sheet

## 2. Set up the virtual environment

From the project root (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Create the Telegram bot

1. Open Telegram and talk to [@BotFather](https://t.me/BotFather).
2. Send `/newbot`, set the name **MHSS-KIDDS** and choose a username.
3. Copy the token BotFather gives you into `BOT_TOKEN` in your `.env`.

## 4. Set up Google Sheets access (service account)

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and
   create (or pick) a project.
2. Enable the **Google Sheets API** and the **Google Drive API** for the project
   (APIs & Services -> Library).
3. Go to **APIs & Services -> Credentials -> Create credentials -> Service
   account**. Give it a name and create it.
4. Open the service account -> **Keys -> Add key -> Create new key -> JSON**.
   Download the JSON file.
5. Save that JSON file into the project root as `credentials.json` (this name is
   already in `.gitignore` so it will not be committed).
6. Open the downloaded JSON and copy the `client_email` value.
7. Open your Google Sheet, click **Share**, and share it with that
   `client_email` as an **Editor**.
8. Copy the Sheet ID from its URL. In
   `https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit`, the ID is the
   part between `/d/` and `/edit`. Put it in `GOOGLE_SHEET_ID` in your `.env`.

### Expected sheet columns

The bot expects the first row to contain these headers (it will create them if
the sheet is empty). Order matters for appended rows:

```
First Name | Father Name | Grand Father Name | Phone Number | Age | Level of Education | Waiting Family | Assigned Class | Source | Timestamp
```

If your headers differ, edit `SHEET_HEADERS` and the `COL_*` constants in
[`config/settings.py`](config/settings.py).

## 5. Configure environment variables

Copy the example file and fill it in:

```powershell
Copy-Item .env.example .env
```

```env
BOT_TOKEN=123456789:ABCDEF_your_bot_token_here
GOOGLE_SHEET_ID=your_google_sheet_id_here
GOOGLE_WORKSHEET_NAME=Sheet1
GOOGLE_CREDENTIALS_FILE=credentials.json
REGISTRATION_LIMIT=270
```

Optional tuning variables (have sensible defaults):

- `NAME_MATCH_THRESHOLD` (default `70`) - fuzzy match cutoff, 0-100.
- `MAX_MATCH_RESULTS` (default `5`) - how many match buttons to show.

## 6. Add the logo

Replace `assets/logo.png` with the real MHSS-KIDDS logo (PNG). It is sent on
`/start`.

## 7. Run the bot

```powershell
python run.py
```

You should see `Starting MHSS-KIDDS bot...`. Open your bot in Telegram and send
`/start`.

## Commands

- `/start` - welcome screen + check a student's status
- `/status` - same as `/start`
- `/register` - jump straight to the registration form
- `/cancel` - cancel the current operation
- `/help` - list commands

## Customizing text and options

- Change any message: edit [`config/messages.py`](config/messages.py).
- Change the education levels: edit the `EDUCATION_LEVELS` list in the same file.
