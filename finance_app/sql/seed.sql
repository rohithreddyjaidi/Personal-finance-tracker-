INSERT INTO users (first_name, last_name, email, phone, join_date)
VALUES
    ('Alice', 'Johnson', 'alice.johnson@example.com', '555-1001', '2026-01-05'),
    ('Bob', 'Martinez', 'bob.martinez@example.com', '555-1002', '2026-01-10'),
    ('Carol', 'Thompson', 'carol.thompson@example.com', '555-1003', '2026-01-15'),
    ('David', 'Lee', 'david.lee@example.com', '555-1004', '2026-02-01'),
    ('Eva', 'Nguyen', 'eva.nguyen@example.com', '555-1005', '2026-02-08'),
    ('Frank', 'Garcia', 'frank.garcia@example.com', '555-1006', '2026-02-12');

INSERT INTO categories (category_name, category_type, description)
VALUES
    ('Salary', 'income', 'Regular job income'),
    ('Freelance', 'income', 'Contract or side project income'),
    ('Groceries', 'expense', 'Food and household supplies'),
    ('Rent', 'expense', 'Monthly housing payment'),
    ('Utilities', 'expense', 'Electric, water, internet, and phone bills'),
    ('Dining Out', 'expense', 'Restaurant and cafe purchases'),
    ('Transportation', 'expense', 'Gas, transit, and rideshare costs'),
    ('Entertainment', 'expense', 'Movies, games, and events'),
    ('Healthcare', 'expense', 'Medical and pharmacy costs'),
    ('Investment', 'income', 'Investment earnings');

INSERT INTO accounts (user_id, account_name, account_type, bank_name, balance)
VALUES
    (1, 'Alice Checking', 'checking', 'First City Bank', 2450.75),
    (1, 'Alice Savings', 'savings', 'First City Bank', 8200.00),
    (2, 'Bob Checking', 'checking', 'Community Bank', 1325.40),
    (3, 'Carol Credit Card', 'credit card', 'Metro Credit', 420.15),
    (4, 'David Savings', 'savings', 'Neighborhood Bank', 6100.00),
    (5, 'Eva Checking', 'checking', 'First City Bank', 1750.30),
    (6, 'Frank Investment', 'investment', 'Future Investments', 15400.25);

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
    (1, 1, 3200.00, 'credit', 'May paycheck', 'Alice Employer', '2026-05-01', '2026-05-01', 0, 1),
    (1, 3, 94.26, 'debit', 'Weekly groceries', 'Fresh Market', '2026-05-03', '2026-05-04', 1, 0),
    (1, 4, 1250.00, 'debit', 'May rent', 'Lakeview Apartments', '2026-05-05', '2026-05-05', 0, 1),
    (2, 10, 35.50, 'credit', 'Monthly interest', 'First City Bank', '2026-05-06', '2026-05-06', 0, 1),
    (3, 2, 750.00, 'credit', 'Website project', 'Local Client', '2026-05-07', '2026-05-08', 1, 0),
    (3, 6, 48.90, 'debit', 'Dinner with friends', 'Corner Bistro', '2026-05-08', '2026-05-09', 1, 0),
    (4, 5, 116.75, 'debit', 'Electric bill', 'City Power', '2026-05-09', '2026-05-10', 1, 1),
    (4, 9, 28.40, 'debit', 'Pharmacy purchase', 'HealthPlus Pharmacy', '2026-05-10', '2026-05-11', 1, 0),
    (5, 1, 2850.00, 'credit', 'May paycheck', 'David Employer', '2026-05-11', '2026-05-11', 0, 1),
    (6, 7, 62.30, 'debit', 'Gas refill', 'Quick Fuel', '2026-05-12', '2026-05-13', 1, 0),
    (6, 8, 39.99, 'debit', 'Streaming subscription', 'StreamWave', '2026-05-13', '2026-05-13', 0, 1),
    (7, 10, 210.45, 'credit', 'Dividend payment', 'Future Investments', '2026-05-14', '2026-05-15', 1, 0);

INSERT INTO budgets (user_id, category_id, monthly_limit, budget_month, notes)
VALUES
    (1, 3, 450.00, '2026-05-01', 'Alice grocery budget'),
    (1, 6, 180.00, '2026-05-01', 'Alice restaurant budget'),
    (2, 7, 220.00, '2026-05-01', 'Bob commute budget'),
    (2, 8, 150.00, '2026-05-01', 'Bob entertainment budget'),
    (3, 5, 300.00, '2026-05-01', 'Carol utility budget'),
    (3, 9, 125.00, '2026-05-01', 'Carol healthcare budget'),
    (4, 4, 1300.00, '2026-05-01', 'David rent budget'),
    (5, 3, 400.00, '2026-05-01', 'Eva grocery budget');
