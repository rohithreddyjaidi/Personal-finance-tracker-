# Normalization Notes

## Project Topic

The database stores information for a Personal Finance Management System. The main idea is to track users, their accounts, spending categories, transactions, and monthly budgets.

## Original Functional Dependencies

If everything was stored in one large finance table, the main dependencies would be:

- user_id determines first_name, last_name, email, phone, join_date, and created_at.
- account_id determines user_id, account_name, account_type, bank_name, balance, currency, is_active, and last_updated.
- category_id determines category_name, category_type, description, and created_at.
- transaction_id determines account_id, category_id, amount, transaction_type, merchant, transaction dates, and recurring status.
- budget_id determines user_id, category_id, monthly_limit, budget_month, notes, and created_at.
- The combination of user_id, category_id, and budget_month determines one budget for that month.

## Anomalies

A single large table would create problems:

- Insert anomaly: A new category could not be added unless there was already a transaction using it.
- Update anomaly: If a user's email was repeated in many rows, every row would need to be updated.
- Delete anomaly: Deleting the last transaction for a category could also remove the only copy of that category information.
- Repetition: Account, user, and category details would be repeated across many transaction rows.

## Decomposition Steps

1. Separate user details into the users table.
2. Separate account details into the accounts table and connect each account to a user.
3. Separate category details into the categories table so category names and types are stored once.
4. Store each transaction in the transactions table and connect it to an account and optional category.
5. Store monthly spending limits in the budgets table and connect each budget to a user and category.

## Final Relational Schema

users(user_id, first_name, last_name, email, phone, join_date, created_at)

accounts(account_id, user_id, account_name, account_type, bank_name, balance, currency, is_active, last_updated)

categories(category_id, category_name, category_type, description, created_at)

transactions(transaction_id, account_id, category_id, amount, transaction_type, description, merchant, transaction_date, posted_date, days_to_post, is_recurring, created_at, updated_at)

budgets(budget_id, user_id, category_id, monthly_limit, budget_month, notes, created_at)

## Why This Design Is In 3NF

The design is in First Normal Form because every table has a primary key and every field stores one value.

The design is in Second Normal Form because each table uses a single-column primary key, so every non-key column depends on the whole primary key.

The design is in Third Normal Form because non-key columns do not depend on other non-key columns. For example, category_name and category_type are stored in categories, not repeated inside transactions. Account details are stored in accounts, not repeated inside budgets or transactions. User details are stored in users, not repeated in accounts or budgets.

This reduces duplicate data and helps prevent insert, update, and delete anomalies.
