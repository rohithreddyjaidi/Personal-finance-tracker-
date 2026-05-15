DROP TABLE IF EXISTS budgets;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    join_date DATE NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    account_type VARCHAR(30) NOT NULL,
    bank_name VARCHAR(100),
    balance DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    currency CHAR(3) NOT NULL DEFAULT 'USD',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    last_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_accounts_users
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
);

CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    category_type VARCHAR(20) NOT NULL,
    description VARCHAR(200),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_categories_category_type
        CHECK (category_type IN ('income', 'expense'))
);

CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT NOT NULL,
    category_id INT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL,
    description VARCHAR(260),
    merchant VARCHAR(100),
    transaction_date DATE NOT NULL,
    posted_date DATE NULL,
    days_to_post INT NULL,
    is_recurring TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_transactions_accounts
        FOREIGN KEY (account_id)
        REFERENCES accounts(account_id),
    CONSTRAINT fk_transactions_categories
        FOREIGN KEY (category_id)
        REFERENCES categories(category_id),
    CONSTRAINT ck_transactions_amount
        CHECK (amount > 0),
    CONSTRAINT ck_transactions_transaction_type
        CHECK (transaction_type IN ('debit', 'credit'))
);

CREATE TABLE budgets (
    budget_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    monthly_limit DECIMAL(10, 2) NOT NULL,
    budget_month DATE NOT NULL,
    notes VARCHAR(255),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_budgets_users
        FOREIGN KEY (user_id)
        REFERENCES users(user_id),
    CONSTRAINT fk_budgets_categories
        FOREIGN KEY (category_id)
        REFERENCES categories(category_id),
    CONSTRAINT ck_budgets_monthly_limit
        CHECK (monthly_limit >= 0),
    CONSTRAINT uq_budgets_user_category_month
        UNIQUE (user_id, category_id, budget_month)
);
