# ECE444 PRA6 - Flaskr

A Flask blogging app developed step by step using test-driven development.
Based on https://github.com/shuruizUofT/flaskr-tdd.

## Local setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python create_db.py
python -m flask --app project.app run --port 5001
```

The local demo login is `admin` / `admin`.

## Tests

```sh
python -m pytest -v
```

Tests use a separate temporary SQLite database for each test.
`create_db.py` uses SQLAlchemy to create missing tables and preserves existing
posts. Tests create a fresh app and configure its database before `db.init_app`,
then create and drop tables only in that temporary database.

`Post` maps to the existing `entries` table so local SQLite posts are preserved.

## Render deployment

Create a Python Web Service from this repository, using these settings:

- Branch: `main`
- Build command: `pip install -r requirements.txt`
- Start command: `python create_db.py && gunicorn project.app:app --bind 0.0.0.0:$PORT`
- Instance type: Free
- Environment: set a random `SECRET_KEY`, plus `APP_USERNAME` and `APP_PASSWORD`.

Without DATABASE_URL, SQLite uses Render's ephemeral filesystem and posts can
be lost on restart. Configure PostgreSQL as described below for external storage.
Deleting posts requires a logged-in session.

## Progress

- Completed: SQLite, templates, login/logout, adding posts, CSS, JS deletion and Bootstrap styling, initial deployment, SQLAlchemy, search with custom tests, and login-required deletion.
- PostgreSQL deployment: reported successful; restart persistence check pending.
- Flake8 and Black: completed locally.
- Final online verification, TA demonstration and Quercus submission: pending.

Deployment URL: https://ece444-pra6-olivia.onrender.com/

Search uses `/search/?query=keyword`, matches title or body without case
sensitivity, and shows no articles for blank queries. Six parameterized search
cases check title/body matches, exclusions, no results and empty queries.

Deletion permission tests cover anonymous access, access after logout, and a
failed password login. Each checks HTTP 401, the JSON error, and that the post
remains stored. The existing successful deletion test covers logged-in access.

## PostgreSQL on Render

Create a Free Render Postgres database in the same region as the Web Service.
In the Web Service Environment settings, set `DATABASE_URL` to the database's
Internal Database URL, then save and redeploy. Keep the existing start command:
`python create_db.py && gunicorn project.app:app --bind 0.0.0.0:$PORT`.
This creates missing tables in PostgreSQL before starting the website.

Without DATABASE_URL, local development continues to use SQLite. With it, the
app uses the specified database. Render PostgreSQL URLs are normalized to use
psycopg 3, installed via `psycopg[binary]`. Existing SQLite posts are not migrated.
Never commit database credentials. Use the External Database URL only when
connecting from your own computer; the Internal URL works within Render.

To follow the tutorial's local table-creation step on macOS/zsh, enter the
External URL without putting it in shell history:

```sh
read -s 'DATABASE_URL?Paste External Database URL: '; echo
export DATABASE_URL
python create_db.py
python -m pytest -v
unset DATABASE_URL
```

Tests explicitly override the database URL with temporary SQLite databases;
they do not create or drop tables in the remote PostgreSQL database.
After deployment, publish a test article, restart the Web Service and verify
that the article remains. PostgreSQL deployment was reported successful; the
restart persistence check still needs to be confirmed.


## Linting and formatting

```sh
python -m flake8 .
python -m black --check .
python -m pytest -v
```

To apply formatting, use `python -m black .`. Configuration excludes virtual
environments from Flake8 and uses an 88-character line length.

## Final demonstration and submission

- Verify successful and unsuccessful login, logout, adding and deleting posts.
- Verify title/body search, case-insensitive matching and no matching results.
- Verify deletion fails after logout and the article remains.
- Verify a published article survives a Render Web Service restart.
- Explain Red-Green-Refactor, test fixtures and database isolation, Post/ORM,
  Flask session versus SQLAlchemy session, login_required, and Gunicorn.
- Show the custom search and deletion-permission tests to the TA.
- Submit the GitHub repository URL to Quercus and obtain the in-person TA evaluation.
