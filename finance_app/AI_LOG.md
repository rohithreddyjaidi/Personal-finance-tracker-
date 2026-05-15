# AI Log

| Tool | Prompt | AI Output Summary | My Modification or Verification |
| --- | --- | --- | --- |
| ChatGPT / Codex | Create a complete but simple Flask project for Project 3: Personal Finance Management System. | Generated the starter Flask project structure, app setup, templates, SQL files, requirements, README, normalization notes, and AI log. | Verified the project files existed and the app could import. |
| ChatGPT / Codex | Add the final 3NF database schema and SQLAlchemy models. | Added final users, accounts, categories, transactions, and budgets tables in SQL and matching SQLAlchemy models. | Verified models imported and relationships configured. |
| ChatGPT / Codex | Add safe database setup and seed data. | Added `flask init-db`, `flask seed-db`, sample data, and updated seed SQL. | Ran the CLI commands after MySQL was installed and verified row counts. |
| ChatGPT / Codex | Add CRUD pages for Users and Accounts. | Added routes, validation, templates, flash messages, dropdowns, and delete protection for users and accounts. | Verified routes, templates, and live pages. |
| ChatGPT / Codex | Handle confusing database errors when MySQL is not connected. | Added a friendly database error page and SQLAlchemy error handler while keeping real errors in the terminal. | Tested `/users` and `/accounts` without MySQL and confirmed the friendly error page appeared. |
| ChatGPT / Codex | Connect local MySQL and sync SQL setup. | Created the local `.env`, created the database, initialized tables, seeded data, and restarted Flask. | Verified homepage, users page, accounts page, and seeded table counts. |
| ChatGPT / Codex | Add Categories and Transactions CRUD. | Added category routes/templates and transaction routes/templates with Decimal money handling and account balance updates. | Tested category CRUD, transaction CRUD, bad input handling, and balance reversal logic. |
| ChatGPT / Codex | Add Budgets CRUD and Summary Dashboard. | Added budget routes/templates, duplicate budget validation, and dashboard aggregate queries using SQLAlchemy functions. | Verified budget CRUD, duplicate prevention, dashboard route, and live pages. |
| ChatGPT / Codex | Final cleanup and documentation for Project 3. | Updated README, normalization notes, and AI log for the completed project. | Ran final import, route, template, data, and requirements checks. |
