# 💡 IdeaLink

**An educational social platform that connects people who are solving the same problem, without ever sharing their contact details.**

> ⚠️ **Prototype.** IdeaLink is an early working prototype built to explore the idea. It is not production-ready.

## Abstract
Great ideas often stay unfinished because the right teammate never shows up. IdeaLink lets learners post a problem statement and automatically matches them with others working on a similar one. Collaboration happens through anonymous private IDs, so emails, phone numbers and links are never exchanged. People can sharpen their problem statement together, publish what they build, and report any issues to a help desk.

## Features
- 💡 **Share ideas:** post a title and a problem statement with tags.
- 🤖 **Smart matching:** new ideas are compared with existing ones and the closest matches are shown with a "% similar" score.
- 🔒 **Anonymous by design:** every user appears only as a generated private ID (e.g. `IL-7F3A92`). Emails, phone numbers and links in ideas, chat and tickets are replaced with `[hidden]`.
- 💬 **Private chat:** send a connection request; chat opens only after the other person accepts.
- 🔥 **Trending projects:** publish projects and like others. Ranking uses likes and views with a time decay, so newer work gets a fair chance.
- 🛟 **Help desk:** file complaints (harassment, spam, idea theft, bug, other) and track their status.
- 🎨 **Calm interface:** soft, low-contrast colours, large click targets, instant feedback and keyboard-friendly focus styles.

## Tech stack
Python (Flask), MySQL, and a single-page HTML/CSS/JavaScript frontend.

## Project structure
```
idealink/
├── app.py            # Flask server and REST API
├── schema.sql        # MySQL database and tables
├── requirements.txt  # Python dependencies
├── static/
│   └── index.html    # Frontend (UI)
└── README.md
```

## Getting started

### 1. Prerequisites
- [Python 3.9+](https://www.python.org/downloads/) (tick **Add Python to PATH** on Windows)
- [MySQL 8+](https://dev.mysql.com/downloads/) with a user that can create a database

### 2. Clone the repository
```bash
git clone https://github.com/<your-username>/idealink.git
cd idealink
```

### 3. Create the database
```bash
mysql -u root -p < schema.sql
```
Or log in with `mysql -u root -p` and run `source schema.sql;`.

> If your MySQL user cannot create databases, load the tables into a database you already have: select it with `mysql -u <user> -p <database>`, run `source schema.sql;` (the first two lines will show "access denied", which is fine), and set `DB_NAME` below.

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure
The app reads these environment variables:

| Variable | Meaning | Default |
|---|---|---|
| `DB_HOST` | MySQL host | `localhost` |
| `DB_USER` | MySQL username | `root` |
| `DB_PASS` | MySQL password | *(empty)* |
| `DB_NAME` | Database name | `idealink` |
| `SECRET_KEY` | Session secret, use random text | `change-me` |

Windows (Command Prompt):
```
set DB_USER=root
set DB_PASS=yourpassword
set SECRET_KEY=some-random-words
```
Mac / Linux:
```bash
export DB_USER=root DB_PASS=yourpassword SECRET_KEY=some-random-words
```

### 6. Run
```bash
python app.py
```
Open **http://127.0.0.1:5000**.

## Try it out
1. Create an account in a normal browser window.
2. Create a second account in a private/incognito window.
3. Post similar problem statements from each. The second post shows the first as a match.
4. Click **Connect and collaborate**, accept the request from the other window, and start chatting.

## Handling complaints (admin)
Reports appear in the `tickets` table. To respond:
```sql
UPDATE tickets SET status='resolved', reply='Thanks, this is fixed.' WHERE id=1;
```
Status can be `open`, `in_review` or `resolved`. The user sees the reply on their Help desk page.

## How matching works
When an idea is posted, its text is turned into weighted word vectors (TF-IDF) and compared with other users' ideas using cosine similarity. Matches above a threshold are returned, best first. Your own ideas are never matched to you.

## Known limitations
- Matching is keyword-based, not meaning-based, and compares in memory, so it suits small datasets.
- Contact-detail filtering uses simple patterns and can be bypassed.
- No admin dashboard, notifications, group chats, blocking or email verification yet.
- Chat refreshes by polling, not live sockets.
- Run with a production server and HTTPS before any real deployment.

## Roadmap
- [ ] Embedding-based semantic matching with a vector index
- [ ] Admin dashboard for tickets and moderation
- [ ] Group chats and project team spaces
- [ ] Notifications, block and report in chat
- [ ] Email verification and password reset

## Contributing
Feedback and ideas are welcome. Open an issue or submit a pull request.

## License
Released under the MIT License. See `LICENSE`.
