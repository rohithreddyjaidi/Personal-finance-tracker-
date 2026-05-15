# Personal Finance Management System

A simple Flask starter project for a database class project.

## Project Topic

Personal Finance Management System

## Tech Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- PyMySQL
- python-dotenv
- MySQL
- Jinja2 templates
- Bootstrap 5

## Current Features

- Basic Flask application
- Bootstrap homepage
- SQLAlchemy database configuration
- Final 3NF database models
- Flask CLI commands for database setup and seed data

CRUD features have not been added yet.

## Setup

Create and activate a virtual environment:

```powershell
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the project requirements:

```powershell
pip install -r requirements.txt
```

Create a `.env` file from `.env.example`:

```powershell
copy .env.example .env
```

Set `DATABASE_URL` in `.env` with your MySQL username, password, host, and database name:

```text
DATABASE_URL=mysql+pymysql://username:password@localhost/finance_app_db
FLASK_APP=app.py
FLASK_DEBUG=1
```

## Create The MySQL Database

Log in to MySQL and create the database:

```sql
CREATE DATABASE finance_app_db;
```

## Initialize Tables

This command drops the existing tables and recreates them from the SQLAlchemy models:

```powershell
flask init-db
```

## Insert Seed Data

This command inserts sample users, categories, accounts, transactions, and budgets. If users already exist, it skips inserting data to avoid duplicates.

```powershell
flask seed-db
```

The same sample data is also available in `sql/seed.sql`.

## Run The App

```powershell
flask run
```

Open the app at:

```text
http://127.0.0.1:5000
```
