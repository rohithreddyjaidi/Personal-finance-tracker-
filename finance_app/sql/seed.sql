INSERT INTO users (first_name, last_name, email, phone, join_date)
VALUES
    ('Alex', 'Taylor', 'alex.taylor@example.com', '555-0100', '2026-05-01');

INSERT INTO categories (category_name, category_type, description)
VALUES
    ('Salary', 'income', 'Regular job income'),
    ('Groceries', 'expense', 'Food and household supplies'),
    ('Rent', 'expense', 'Monthly housing payment'),
    ('Entertainment', 'expense', 'Movies, games, and events');

INSERT INTO accounts (user_id, account_name, account_type, bank_name, balance)
VALUES
    (1, 'Main Checking', 'checking', 'Sample Bank', 1200.00),
    (1, 'Emergency Savings', 'savings', 'Sample Bank', 2500.00);

INSERT INTO transactions (
    account_id,
    category_id,
    amount,
    transaction_type,
    description,
    merchant,
    transaction_date,
    posted_date,
    days_to_post,
    is_recurring
)
VALUES
    (1, 1, 1500.00, 'credit', 'Paycheck', 'Sample Employer', '2026-05-01', '2026-05-01', 0, 1),
    (1, 2, 85.42, 'debit', 'Weekly groceries', 'Grocery Store', '2026-05-03', '2026-05-04', 1, 0),
    (1, 3, 900.00, 'debit', 'Monthly rent', 'Apartment Office', '2026-05-05', '2026-05-05', 0, 1);

INSERT INTO budgets (user_id, category_id, monthly_limit, budget_month, notes)
VALUES
    (1, 2, 450.00, '2026-05-01', 'Monthly grocery budget'),
    (1, 4, 150.00, '2026-05-01', 'Monthly entertainment budget');
