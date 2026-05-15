# Normalization Notes

## Original Functional Dependencies

At first, the finance data could have been stored in one large table with user, account, category, transaction, and budget information mixed together. The main functional dependencies were:

- user_id determines first_name, last_name, email, phone, join_date, and created_at.
- account_id determines user_id, account_name, account_type, bank_name, balance, currency, is_active, and last_updated.
- category_id determines category_name, category_type, description, and created_at.
- transaction_id determines account_id, category_id, amount, transaction_type, description, merchant, transaction_date, posted_date, days_to_post, is_recurring, created_at, and updated_at.
- budget_id determines user_id, category_id, monthly_limit, budget_month, notes, and created_at.
- user_id, category_id, and budget_month together determine one budget for that user, category, and month.

## Anomaly Identification

If all of the data was kept in one large table, the database would have repeated information and update problems.

- Insert anomaly: A category could not be added unless a transaction already used it.
- Update anomaly: If a user's email changed, it might need to be updated in many rows.
- Delete anomaly: Deleting the last transaction for an account or category could remove important account or category information.
- Repetition problem: User names, account names, and category names would be repeated across many transaction rows.

## Decomposition Steps

1. Move user information into the users table.
2. Move account information into the accounts table and connect each account to one user.
3. Move category information into the categories table so category names and types are stored once.
4. Move transaction information into the transactions table and connect each transaction to one account and optionally one category.
5. Move budget information into the budgets table and connect each budget to one user and one category.
6. Add a unique rule on user_id, category_id, and budget_month so the same monthly budget is not repeated.

## Final Relational Schema

users(user_id, first_name, last_name, email, phone, join_date, created_at)

accounts(account_id, user_id, account_name, account_type, bank_name, balance, currency, is_active, last_updated)

categories(category_id, category_name, category_type, description, created_at)

transactions(transaction_id, account_id, category_id, amount, transaction_type, description, merchant, transaction_date, posted_date, days_to_post, is_recurring, created_at, updated_at)

budgets(budget_id, user_id, category_id, monthly_limit, budget_month, notes, created_at)

## 3NF Explanation

The database is in First Normal Form because each table has a primary key and each field stores one value.

The database is in Second Normal Form because the tables use single-column primary keys, and the non-key columns depend on the full key for that table.

The database is in Third Normal Form because non-key columns do not depend on other non-key columns. For example, category_type depends on category_id, not on transaction_id. Account details are stored in accounts instead of being repeated inside transactions. User details are stored in users instead of being repeated inside accounts or budgets.

This design reduces duplicate data and helps prevent insert, update, and delete anomalies.
