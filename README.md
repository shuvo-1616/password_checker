# password_checker
# Password Checker Pro+

Web-based password strength, breach, reuse & predictive checker.

## Features

- Password strength & live meter (zxcvbn)
- HIBP pwned check
- Fuzzy similarity check
- Password reuse detection
- MFA status flag
- Predictive crack time
- Admin dashboard (user password stats)
- Docker & Gunicorn ready

## Setup

### Local (SQLite)
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

Open: http://127.0.0.1:5000

Docker

docker-compose build
docker-compose up

Admin Dashboard

Visit: http://127.0.0.1:5000/admin

Notes

For production, set debug=False

Use SSL & authentication for admin access

Large leaked DBs → use indexed search / background tasks 
password_checker/
├─ app.py
├─ core.py
├─ fuzzy.py
├─ context.py
├─ predictive.py
├─ templates/
│   └─ index.html
│   └─ admin.html
├─ requirements.txt
├─ Dockerfile
├─ docker-compose.yml
├─ README.md

# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port
EXPOSE 5000

# Run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "4"]


---

docker-compose.yml (optional Postgres)

version: "3.9"
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: password_user
      POSTGRES_PASSWORD: password_pass
      POSTGRES_DB: password_db
    ports:
      - "5432:5432"


---

requirements.txt

Flask>=2.3
requests>=2.28
python-Levenshtein; platform_system!="Windows"
zxcvbn
gunicorn
psycopg2-binary
