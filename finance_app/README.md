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
- Starter database models
- SQL schema and seed files

CRUD features have not been added yet.

## Setup

Create a `.env` file from `.env.example`, then update the database username and password.

```powershell
copy .env.example .env
```

Create the MySQL database before running the app:

```sql
CREATE DATABASE finance_app_db;
```

Then run the schema and seed files in MySQL:

```sql
SOURCE sql/schema.sql;
SOURCE sql/seed.sql;
```

## Run the App

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask run
```
