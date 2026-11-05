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
`create_db.py` preserves existing posts. `init_db()` resets the database and is
used in tests; do not run it against data you want to keep.

## Render deployment (current SQLite stage)

Create a Python Web Service from this repository, using these settings:

- Branch: `main`
- Build command: `pip install -r requirements.txt`
- Start command: `python create_db.py && gunicorn project.app:app --bind 0.0.0.0:$PORT`
- Instance type: Free
- Environment: set a random `SECRET_KEY`, plus `APP_USERNAME` and `APP_PASSWORD`.

This stage uses SQLite on Render's ephemeral filesystem. Posts can be lost on
restart, redeploy or spin-down. The later PRA6 PostgreSQL stage provides external
database storage. Deletion permissions are also added in a later tutorial stage.

## Progress

- Completed: SQLite, templates, login/logout, adding posts, CSS, JS deletion and Bootstrap styling.
- Remaining: SQLAlchemy, search and custom tests,
  login-required deletion and tests, PostgreSQL, linting and formatting.

Deployment URL: https://ece444-pra6-olivia.onrender.com/
