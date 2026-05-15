from extensions import db


class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    join_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.text("CURRENT_TIMESTAMP"),
    )

    accounts = db.relationship("Account", back_populates="user")
    budgets = db.relationship("Budget", back_populates="user")


class Account(db.Model):
    __tablename__ = "accounts"

    account_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.String(30), nullable=False)
    bank_name = db.Column(db.String(100))
    balance = db.Column(db.Numeric(12, 2), nullable=False, server_default="0.00")
    currency = db.Column(db.CHAR(3), nullable=False, server_default="USD")
    is_active = db.Column(db.Boolean, nullable=False, server_default="1")
    last_updated = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )

    user = db.relationship("User", back_populates="accounts")
    transactions = db.relationship("Transaction", back_populates="account")


class Category(db.Model):
    __tablename__ = "categories"
    __table_args__ = (
        db.CheckConstraint(
            "category_type IN ('income', 'expense')",
            name="ck_categories_category_type",
        ),
    )

    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), nullable=False, unique=True)
    category_type = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.text("CURRENT_TIMESTAMP"),
    )

    transactions = db.relationship("Transaction", back_populates="category")
    budgets = db.relationship("Budget", back_populates="category")


class Transaction(db.Model):
    __tablename__ = "transactions"
    __table_args__ = (
        db.CheckConstraint("amount > 0", name="ck_transactions_amount"),
        db.CheckConstraint(
            "transaction_type IN ('debit', 'credit')",
            name="ck_transactions_transaction_type",
        ),
    )

    transaction_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(
        db.Integer,
        db.ForeignKey("accounts.account_id"),
        nullable=False,
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.category_id"),
        nullable=True,
    )
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(260))
    merchant = db.Column(db.String(100))
    transaction_date = db.Column(db.Date, nullable=False)
    posted_date = db.Column(db.Date)
    days_to_post = db.Column(db.Integer)
    is_recurring = db.Column(db.Boolean, nullable=False, server_default="0")
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.text("CURRENT_TIMESTAMP"),
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )

    account = db.relationship("Account", back_populates="transactions")
    category = db.relationship("Category", back_populates="transactions")


class Budget(db.Model):
    __tablename__ = "budgets"
    __table_args__ = (
        db.CheckConstraint("monthly_limit >= 0", name="ck_budgets_monthly_limit"),
        db.UniqueConstraint(
            "user_id",
            "category_id",
            "budget_month",
            name="uq_budgets_user_category_month",
        ),
    )

    budget_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.category_id"),
        nullable=False,
    )
    monthly_limit = db.Column(db.Numeric(10, 2), nullable=False)
    budget_month = db.Column(db.Date, nullable=False)
    notes = db.Column(db.String(255))
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.text("CURRENT_TIMESTAMP"),
    )

    user = db.relationship("User", back_populates="budgets")
    category = db.relationship("Category", back_populates="budgets")
