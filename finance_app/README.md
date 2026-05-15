# Personal Finance Management System

## Project Description

This is a Flask and MySQL full-stack web application for managing personal finance data. The app tracks users, accounts, categories, transactions, and budgets. It also includes a summary dashboard with aggregate database results.

## Features

- Bootstrap homepage and navigation
- MySQL database connection through Flask-SQLAlchemy and PyMySQL
- SQLAlchemy models for users, accounts, categories, transactions, and budgets
- CRUD pages for users, accounts, categories, transactions, and budgets
- One-to-many display of a user and that user's accounts
- Transaction logic that updates account balances when transactions are created, edited, or deleted
- Server-side validation for required fields, money values, dates, duplicate budgets, and category/transaction types
- Friendly database error page when MySQL is not connected
- Summary dashboard using SQL aggregate functions
- SQL schema and seed data files
- Flask CLI commands for database setup and seed data

## Tech Stack

- Python 3
- Flask
- Flask-SQLAlchemy
- PyMySQL
- python-dotenv
- cryptography
- MySQL 8.0
- Jinja2 templates
- Bootstrap 5

## Installation

Open Windows PowerShell and move into the project folder:

```powershell
cd "C:\Users\jaidi\OneDrive\Desktop\Py2\DBMS Project\Finance tracker\finance_app"
```

Create and activate a virtual environment:

```powershell
py -3 -m venv venv
.\venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
pip install -r requirements.txt
```

## .env Setup

Create a local `.env` file:

```powershell
copy .env.example .env
```

Edit `.env` and set your MySQL username and password:

```text
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/finance_app_db?charset=utf8mb4
FLASK_APP=app.py
FLASK_DEBUG=1
```

Do not commit `.env` because it contains your database password.

## MySQL Database Creation

Start the MySQL service:

```powershell
Start-Service MySQL80
```

Create the database:

```powershell
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p -e "CREATE DATABASE IF NOT EXISTS finance_app_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

## Initialize and Seed the Database

Create the tables from the SQLAlchemy models:

```powershell
flask init-db
```

Insert sample data:

```powershell
flask seed-db
```

## Run the App

```powershell
flask run
```

Open the app:

```text
http://127.0.0.1:5000
```

## Usage Guide

- Use `Users` to add, view, edit, and delete users.
- Use `Accounts` to manage accounts and connect them to users.
- Use `Categories` to manage income and expense categories.
- Use `Transactions` to record debit and credit transactions. Transaction changes update the related account balance.
- Use `Budgets` to set monthly category limits for users.
- Use `Dashboard` to view totals and grouped summaries.

Users cannot be deleted if they still have accounts or budgets. Accounts cannot be deleted if they still have transactions. Categories cannot be deleted if they still have transactions or budgets.

## SQL Files

- `sql/schema.sql` contains the final MySQL schema.
- `sql/seed.sql` contains sample seed data.

The Flask commands use the SQLAlchemy models, while the SQL files are included for database class review and manual SQL setup.

## Git Commit Note

Before committing, make sure `.env` is not staged. The `.gitignore` file already excludes `.env`, `venv/`, `__pycache__/`, `*.pyc`, and `instance/`.

Suggested commit message:

```text
Complete Project 3 finance tracker app
```
