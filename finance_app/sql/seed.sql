INSERT INTO users (first_name, last_name, email)
VALUES
    ('Alex', 'Taylor', 'alex.taylor@example.com');

INSERT INTO categories (category_name, category_type)
VALUES
    ('Salary', 'Income'),
    ('Groceries', 'Expense'),
    ('Rent', 'Expense'),
    ('Entertainment', 'Expense');

INSERT INTO accounts (user_id, account_name, account_type, balance)
VALUES
    (1, 'Main Checking', 'Checking', 1200.00),
    (1, 'Emergency Savings', 'Savings', 2500.00);

INSERT INTO transactions (account_id, category_id, amount, transaction_date, description)
VALUES
    (1, 1, 1500.00, '2026-05-01', 'Paycheck'),
    (1, 2, -85.42, '2026-05-03', 'Weekly groceries'),
    (1, 3, -900.00, '2026-05-05', 'Monthly rent');
