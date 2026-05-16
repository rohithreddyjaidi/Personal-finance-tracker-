from datetime import date
from decimal import Decimal, InvalidOperation

import click
from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from config import Config
from extensions import db
from models import Account, Budget, Category, Transaction, User


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(SQLAlchemyError)
def handle_database_error(error):
    db.session.rollback()
    app.logger.exception("Database error: %s", error)
    return render_template("database_error.html"), 503

def get_user_form_data():
    join_date_value = request.form.get("join_date", "").strip()

    try:
        join_date = date.fromisoformat(join_date_value) if join_date_value else date.today()
    except ValueError:
        join_date = date.today()

    return {
        "first_name": request.form.get("first_name", "").strip(),
        "last_name": request.form.get("last_name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "phone": request.form.get("phone", "").strip() or None,
        "join_date": join_date,
    }


def validate_user_data(data, user_id=None):
    errors = []

    if not data["first_name"]:
        errors.append("First name is required.")
    if not data["last_name"]:
        errors.append("Last name is required.")
    if not data["email"]:
        errors.append("Email is required.")

    if data["email"]:
        existing_user = User.query.filter_by(email=data["email"]).first()
        if existing_user and existing_user.user_id != user_id:
            errors.append("Email must be unique.")

    return errors


def get_account_form_data():
    balance_text = request.form.get("balance", "").strip()
    currency = request.form.get("currency", "USD").strip().upper() or "USD"
    data = {
        "user_id": None,
        "account_name": request.form.get("account_name", "").strip(),
        "account_type": request.form.get("account_type", "").strip(),
        "bank_name": request.form.get("bank_name", "").strip() or None,
        "balance": None,
        "currency": currency[:3],
        "is_active": "is_active" in request.form,
    }
    errors = []

    user_id_text = request.form.get("user_id", "").strip()
    if not user_id_text:
        errors.append("User is required.")
    else:
        try:
            data["user_id"] = int(user_id_text)
        except ValueError:
            errors.append("Please select a valid user.")

    if data["user_id"] and db.session.get(User, data["user_id"]) is None:
        errors.append("Please select a valid user.")

    if not data["account_name"]:
        errors.append("Account name is required.")
    if not data["account_type"]:
        errors.append("Account type is required.")
    if not balance_text:
        errors.append("Balance is required.")
    else:
        try:
            balance = Decimal(balance_text)
            if not balance.is_finite():
                raise InvalidOperation
            data["balance"] = balance
        except (InvalidOperation, ValueError):
            errors.append("Balance must be a valid decimal number.")

    return data, errors


def user_form_values(user=None, data=None):
    if data:
        return {
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "email": data["email"],
            "phone": data["phone"] or "",
            "join_date": data["join_date"].isoformat(),
        }

    if user:
        return {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone": user.phone or "",
            "join_date": user.join_date.isoformat(),
        }

    return {
        "first_name": "",
        "last_name": "",
        "email": "",
        "phone": "",
        "join_date": date.today().isoformat(),
    }


def account_form_values(account=None, data=None):
    if data:
        return {
            "user_id": data["user_id"],
            "account_name": data["account_name"],
            "account_type": data["account_type"],
            "bank_name": data["bank_name"] or "",
            "balance": request.form.get("balance", "").strip(),
            "currency": data["currency"] or "USD",
            "is_active": data["is_active"],
        }

    if account:
        return {
            "user_id": account.user_id,
            "account_name": account.account_name,
            "account_type": account.account_type,
            "bank_name": account.bank_name or "",
            "balance": account.balance,
            "currency": account.currency or "USD",
            "is_active": account.is_active,
        }

    return {
        "user_id": "",
        "account_name": "",
        "account_type": "",
        "bank_name": "",
        "balance": "",
        "currency": "USD",
        "is_active": True,
    }


def get_category_form_data():
    return {
        "category_name": request.form.get("category_name", "").strip(),
        "category_type": request.form.get("category_type", "").strip().lower(),
        "description": request.form.get("description", "").strip() or None,
    }


def validate_category_data(data, category_id=None):
    errors = []

    if not data["category_name"]:
        errors.append("Category name is required.")
    if data["category_type"] not in ["income", "expense"]:
        errors.append("Category type must be income or expense.")

    if data["category_name"]:
        existing_category = Category.query.filter_by(
            category_name=data["category_name"]
        ).first()
        if existing_category and existing_category.category_id != category_id:
            errors.append("Category name must be unique.")

    return errors


def category_form_values(category=None, data=None):
    if data:
        return {
            "category_name": data["category_name"],
            "category_type": data["category_type"],
            "description": data["description"] or "",
        }

    if category:
        return {
            "category_name": category.category_name,
            "category_type": category.category_type,
            "description": category.description or "",
        }

    return {
        "category_name": "",
        "category_type": "expense",
        "description": "",
    }


def parse_form_date(value, field_name, required=False):
    value = value.strip()
    if not value:
        if required:
            return None, f"{field_name} is required."
        return None, None

    try:
        return date.fromisoformat(value), None
    except ValueError:
        return None, f"{field_name} must be a valid date."


def get_transaction_form_data():
    data = {
        "account_id": None,
        "category_id": None,
        "amount": None,
        "transaction_type": request.form.get("transaction_type", "").strip().lower(),
        "description": request.form.get("description", "").strip() or None,
        "merchant": request.form.get("merchant", "").strip() or None,
        "transaction_date": None,
        "posted_date": None,
        "days_to_post": None,
        "is_recurring": "is_recurring" in request.form,
    }
    errors = []

    account_id_text = request.form.get("account_id", "").strip()
    if not account_id_text:
        errors.append("Account is required.")
    else:
        try:
            data["account_id"] = int(account_id_text)
        except ValueError:
            errors.append("Please select a valid account.")

    if data["account_id"] and db.session.get(Account, data["account_id"]) is None:
        errors.append("Please select a valid account.")

    category_id_text = request.form.get("category_id", "").strip()
    if category_id_text:
        try:
            data["category_id"] = int(category_id_text)
        except ValueError:
            errors.append("Please select a valid category.")

    if data["category_id"] and db.session.get(Category, data["category_id"]) is None:
        errors.append("Please select a valid category.")

    amount_text = request.form.get("amount", "").strip()
    if not amount_text:
        errors.append("Amount is required.")
    else:
        try:
            amount = Decimal(amount_text)
            if not amount.is_finite() or amount <= 0:
                raise InvalidOperation
            data["amount"] = amount
        except (InvalidOperation, ValueError):
            errors.append("Amount must be a valid number greater than 0.")

    if data["transaction_type"] not in ["debit", "credit"]:
        errors.append("Transaction type must be debit or credit.")

    transaction_date, date_error = parse_form_date(
        request.form.get("transaction_date", ""),
        "Transaction date",
        required=True,
    )
    if date_error:
        errors.append(date_error)
    data["transaction_date"] = transaction_date

    posted_date, posted_date_error = parse_form_date(
        request.form.get("posted_date", ""),
        "Posted date",
    )
    if posted_date_error:
        errors.append(posted_date_error)
    data["posted_date"] = posted_date

    if data["transaction_date"] and data["posted_date"]:
        data["days_to_post"] = (
            data["posted_date"] - data["transaction_date"]
        ).days

    return data, errors


def transaction_form_values(transaction=None, data=None):
    if data:
        return {
            "account_id": data["account_id"],
            "category_id": data["category_id"] or "",
            "amount": request.form.get("amount", "").strip(),
            "transaction_type": data["transaction_type"],
            "description": data["description"] or "",
            "merchant": data["merchant"] or "",
            "transaction_date": request.form.get("transaction_date", "").strip(),
            "posted_date": request.form.get("posted_date", "").strip(),
            "is_recurring": data["is_recurring"],
        }

    if transaction:
        posted_date = ""
        if transaction.posted_date:
            posted_date = transaction.posted_date.isoformat()

        return {
            "account_id": transaction.account_id,
            "category_id": transaction.category_id or "",
            "amount": transaction.amount,
            "transaction_type": transaction.transaction_type,
            "description": transaction.description or "",
            "merchant": transaction.merchant or "",
            "transaction_date": transaction.transaction_date.isoformat(),
            "posted_date": posted_date,
            "is_recurring": transaction.is_recurring,
        }

    return {
        "account_id": "",
        "category_id": "",
        "amount": "",
        "transaction_type": "debit",
        "description": "",
        "merchant": "",
        "transaction_date": date.today().isoformat(),
        "posted_date": "",
        "is_recurring": False,
    }


def apply_transaction_to_balance(account, amount, transaction_type):
    if transaction_type == "credit":
        account.balance = Decimal(account.balance or 0) + amount
    else:
        account.balance = Decimal(account.balance or 0) - amount


def reverse_transaction_from_balance(account, amount, transaction_type):
    if transaction_type == "credit":
        account.balance = Decimal(account.balance or 0) - amount
    else:
        account.balance = Decimal(account.balance or 0) + amount


def get_budget_form_data():
    data = {
        "user_id": None,
        "category_id": None,
        "monthly_limit": None,
        "budget_month": None,
        "notes": request.form.get("notes", "").strip() or None,
    }
    errors = []

    user_id_text = request.form.get("user_id", "").strip()
    if not user_id_text:
        errors.append("User is required.")
    else:
        try:
            data["user_id"] = int(user_id_text)
        except ValueError:
            errors.append("Please select a valid user.")

    if data["user_id"] and db.session.get(User, data["user_id"]) is None:
        errors.append("Please select a valid user.")

    category_id_text = request.form.get("category_id", "").strip()
    if not category_id_text:
        errors.append("Category is required.")
    else:
        try:
            data["category_id"] = int(category_id_text)
        except ValueError:
            errors.append("Please select a valid category.")

    if data["category_id"] and db.session.get(Category, data["category_id"]) is None:
        errors.append("Please select a valid category.")

    monthly_limit_text = request.form.get("monthly_limit", "").strip()
    if not monthly_limit_text:
        errors.append("Monthly limit is required.")
    else:
        try:
            monthly_limit = Decimal(monthly_limit_text)
            if not monthly_limit.is_finite() or monthly_limit < 0:
                raise InvalidOperation
            data["monthly_limit"] = monthly_limit
        except (InvalidOperation, ValueError):
            errors.append("Monthly limit must be a valid number that is 0 or greater.")

    budget_month, date_error = parse_form_date(
        request.form.get("budget_month", ""),
        "Budget month",
        required=True,
    )
    if date_error:
        errors.append(date_error)
    data["budget_month"] = budget_month

    return data, errors


def validate_budget_duplicate(data, budget_id=None):
    if not data["user_id"] or not data["category_id"] or not data["budget_month"]:
        return None

    existing_budget = Budget.query.filter_by(
        user_id=data["user_id"],
        category_id=data["category_id"],
        budget_month=data["budget_month"],
    ).first()

    if existing_budget and existing_budget.budget_id != budget_id:
        return "A budget already exists for this user, category, and month."

    return None


def budget_form_values(budget=None, data=None):
    if data:
        return {
            "user_id": data["user_id"],
            "category_id": data["category_id"],
            "monthly_limit": request.form.get("monthly_limit", "").strip(),
            "budget_month": request.form.get("budget_month", "").strip(),
            "notes": data["notes"] or "",
        }

    if budget:
        return {
            "user_id": budget.user_id,
            "category_id": budget.category_id,
            "monthly_limit": budget.monthly_limit,
            "budget_month": budget.budget_month.isoformat(),
            "notes": budget.notes or "",
        }

    return {
        "user_id": "",
        "category_id": "",
        "monthly_limit": "",
        "budget_month": date.today().replace(day=1).isoformat(),
        "notes": "",
    }


@app.route("/users")
def users_list():
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template("users/list.html", users=users)


@app.route("/users/new", methods=["GET", "POST"])
def users_new():
    if request.method == "POST":
        data = get_user_form_data()
        errors = validate_user_data(data)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "users/form.html",
                form_title="Add User",
                form_values=user_form_values(data=data),
                user=None,
            )

        user = User(**data)
        db.session.add(user)

        try:
            db.session.commit()
            flash("User created successfully.", "success")
            return redirect(url_for("user_detail", user_id=user.user_id))
        except Exception as error:
            db.session.rollback()
            flash(f"Error creating user: {error}", "danger")

    return render_template(
        "users/form.html",
        form_title="Add User",
        form_values=user_form_values(),
        user=None,
    )


@app.route("/users/<int:user_id>")
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("users/detail.html", user=user)


@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def users_edit(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        data = get_user_form_data()
        errors = validate_user_data(data, user_id=user.user_id)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "users/form.html",
                form_title="Edit User",
                form_values=user_form_values(data=data),
                user=user,
            )

        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.email = data["email"]
        user.phone = data["phone"]
        user.join_date = data["join_date"]

        try:
            db.session.commit()
            flash("User updated successfully.", "success")
            return redirect(url_for("user_detail", user_id=user.user_id))
        except Exception as error:
            db.session.rollback()
            flash(f"Error updating user: {error}", "danger")

    return render_template(
        "users/form.html",
        form_title="Edit User",
        form_values=user_form_values(user=user),
        user=user,
    )


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def users_delete(user_id):
    user = User.query.get_or_404(user_id)

    if user.accounts or user.budgets:
        flash("Cannot delete a user who has accounts or budgets.", "danger")
        return redirect(url_for("user_detail", user_id=user.user_id))

    try:
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully.", "success")
    except Exception as error:
        db.session.rollback()
        flash(f"Error deleting user: {error}", "danger")

    return redirect(url_for("users_list"))


@app.route("/accounts")
def accounts_list():
    accounts = Account.query.join(User).order_by(Account.account_name).all()
    return render_template("accounts/list.html", accounts=accounts)


@app.route("/accounts/new", methods=["GET", "POST"])
def accounts_new():
    users = User.query.order_by(User.last_name, User.first_name).all()
    if not users:
        flash("Create a user before adding an account.", "danger")
        return redirect(url_for("users_new"))

    if request.method == "POST":
        data, errors = get_account_form_data()

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "accounts/form.html",
                form_title="Add Account",
                form_values=account_form_values(data=data),
                account=None,
                users=users,
            )

        account = Account(**data)
        db.session.add(account)

        try:
            db.session.commit()
            flash("Account created successfully.", "success")
            return redirect(url_for("accounts_list"))
        except Exception as error:
            db.session.rollback()
            flash(f"Error creating account: {error}", "danger")

    return render_template(
        "accounts/form.html",
        form_title="Add Account",
        form_values=account_form_values(),
        account=None,
        users=users,
    )


@app.route("/accounts/<int:account_id>/edit", methods=["GET", "POST"])
def accounts_edit(account_id):
    account = Account.query.get_or_404(account_id)
    users = User.query.order_by(User.last_name, User.first_name).all()

    if request.method == "POST":
        data, errors = get_account_form_data()

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "accounts/form.html",
                form_title="Edit Account",
                form_values=account_form_values(data=data),
                account=account,
                users=users,
            )

        account.user_id = data["user_id"]
        account.account_name = data["account_name"]
        account.account_type = data["account_type"]
        account.bank_name = data["bank_name"]
        account.balance = data["balance"]
        account.currency = data["currency"]
        account.is_active = data["is_active"]

        try:
            db.session.commit()
            flash("Account updated successfully.", "success")
            return redirect(url_for("accounts_list"))
        except Exception as error:
            db.session.rollback()
            flash(f"Error updating account: {error}", "danger")

    return render_template(
        "accounts/form.html",
        form_title="Edit Account",
        form_values=account_form_values(account=account),
        account=account,
        users=users,
    )


@app.route("/accounts/<int:account_id>/delete", methods=["POST"])
def accounts_delete(account_id):
    account = Account.query.get_or_404(account_id)

    if account.transactions:
        flash("Cannot delete an account that has transactions.", "danger")
        return redirect(url_for("accounts_list"))

    try:
        db.session.delete(account)
        db.session.commit()
        flash("Account deleted successfully.", "success")
    except Exception as error:
        db.session.rollback()
        flash(f"Error deleting account: {error}", "danger")

    return redirect(url_for("accounts_list"))


@app.route("/categories")
def categories_list():
    categories = Category.query.order_by(Category.category_name).all()
    return render_template("categories/list.html", categories=categories)


@app.route("/categories/new", methods=["GET", "POST"])
def categories_new():
    if request.method == "POST":
        data = get_category_form_data()
        errors = validate_category_data(data)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "categories/form.html",
                form_title="Add Category",
                form_values=category_form_values(data=data),
                category=None,
            )

        category = Category(**data)
        db.session.add(category)

        try:
            db.session.commit()
            flash("Category created successfully.", "success")
            return redirect(url_for("categories_list"))
        except Exception as error:
            db.session.rollback()
            flash(f"Error creating category: {error}", "danger")

    return render_template(
        "categories/form.html",
        form_title="Add Category",
        form_values=category_form_values(),
        category=None,
    )


@app.route("/categories/<int:category_id>/edit", methods=["GET", "POST"])
def categories_edit(category_id):
    category = Category.query.get_or_404(category_id)

    if request.method == "POST":
        data = get_category_form_data()
        errors = validate_category_data(data, category_id=category.category_id)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "categories/form.html",
                form_title="Edit Category",
                form_values=category_form_values(data=data),
                category=category,
            )

        category.category_name = data["category_name"]
        category.category_type = data["category_type"]
        category.description = data["description"]

        try:
            db.session.commit()
            flash("Category updated successfully.", "success")
            return redirect(url_for("categories_list"))
        except Exception as error:
            db.session.rollback()
            flash(f"Error updating category: {error}", "danger")

    return render_template(
        "categories/form.html",
        form_title="Edit Category",
        form_values=category_form_values(category=category),
        category=category,
    )


@app.route("/categories/<int:category_id>/delete", methods=["POST"])
def categories_delete(category_id):
    category = Category.query.get_or_404(category_id)

    if category.transactions or category.budgets:
        flash(
            "Cannot delete a category that has transactions or budgets.",
            "danger",
        )
        return redirect(url_for("categories_list"))

    try:
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted successfully.", "success")
    except Exception as error:
        db.session.rollback()
        flash(f"Error deleting category: {error}", "danger")

    return redirect(url_for("categories_list"))


@app.route("/transactions")
def transactions_list():
    transactions = (
        Transaction.query.join(Account)
        .outerjoin(Category)
        .order_by(Transaction.transaction_date.desc(), Transaction.transaction_id.desc())
        .all()
    )
    return render_template("transactions/list.html", transactions=transactions)


@app.route("/transactions/new", methods=["GET", "POST"])
def transactions_new():
    accounts = Account.query.order_by(Account.account_name).all()
    categories = Category.query.order_by(Category.category_name).all()

    if not accounts:
        flash("Create an account before adding a transaction.", "danger")
        return redirect(url_for("accounts_new"))

    if request.method == "POST":
        data, errors = get_transaction_form_data()

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "transactions/form.html",
                form_title="Add Transaction",
                form_values=transaction_form_values(data=data),
                transaction=None,
                accounts=accounts,
                categories=categories,
            )

        account = db.session.get(Account, data["account_id"])
        transaction = Transaction(**data)

        try:
            db.session.add(transaction)
            apply_transaction_to_balance(
                account,
                data["amount"],
                data["transaction_type"],
            )
            db.session.commit()
            flash("Transaction created successfully.", "success")
            return redirect(url_for("transactions_list"))
        except Exception as error:
            db.session.rollback()
            flash(f"Error creating transaction: {error}", "danger")

    return render_template(
        "transactions/form.html",
        form_title="Add Transaction",
        form_values=transaction_form_values(),
        transaction=None,
        accounts=accounts,
        categories=categories,
    )


@app.route("/transactions/<int:transaction_id>/edit", methods=["GET", "POST"])
def transactions_edit(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    accounts = Account.query.order_by(Account.account_name).all()
    categories = Category.query.order_by(Category.category_name).all()

    if request.method == "POST":
        data, errors = get_transaction_form_data()

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "transactions/form.html",
                form_title="Edit Transaction",
                form_values=transaction_form_values(data=data),
                transaction=transaction,
                accounts=accounts,
                categories=categories,
            )

        old_account = transaction.account
        old_amount = Decimal(transaction.amount)
        old_transaction_type = transaction.transaction_type
        new_account = db.session.get(Account, data["account_id"])

        try:
            reverse_transaction_from_balance(
                old_account,
                old_amount,
                old_transaction_type,
            )
            apply_transaction_to_balance(
                new_account,
                data["amount"],
                data["transaction_type"],
            )

            transaction.account_id = data["account_id"]
            transaction.category_id = data["category_id"]
            transaction.amount = data["amount"]
            transaction.transaction_type = data["transaction_type"]
            transaction.description = data["description"]
            transaction.merchant = data["merchant"]
            transaction.transaction_date = data["transaction_date"]
            transaction.posted_date = data["posted_date"]
            transaction.days_to_post = data["days_to_post"]
            transaction.is_recurring = data["is_recurring"]

            db.session.commit()
            flash("Transaction updated successfully.", "success")
            return redirect(url_for("transactions_list"))
        except Exception as error:
            db.session.rollback()
            flash(f"Error updating transaction: {error}", "danger")

    return render_template(
        "transactions/form.html",
        form_title="Edit Transaction",
        form_values=transaction_form_values(transaction=transaction),
        transaction=transaction,
        accounts=accounts,
        categories=categories,
    )


@app.route("/transactions/<int:transaction_id>/delete", methods=["POST"])
def transactions_delete(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)

    try:
        reverse_transaction_from_balance(
            transaction.account,
            Decimal(transaction.amount),
            transaction.transaction_type,
        )
        db.session.delete(transaction)
        db.session.commit()
        flash("Transaction deleted successfully.", "success")
    except Exception as error:
        db.session.rollback()
        flash(f"Error deleting transaction: {error}", "danger")

    return redirect(url_for("transactions_list"))


@app.route("/budgets")
def budgets_list():
    budgets = (
        Budget.query.join(User)
        .join(Category)
        .order_by(Budget.budget_month.desc(), User.last_name, Category.category_name)
        .all()
    )
    return render_template("budgets/list.html", budgets=budgets)


@app.route("/budgets/new", methods=["GET", "POST"])
def budgets_new():
    users = User.query.order_by(User.last_name, User.first_name).all()
    categories = Category.query.order_by(Category.category_name).all()

    if not users:
        flash("Create a user before adding a budget.", "danger")
        return redirect(url_for("users_new"))
    if not categories:
        flash("Create a category before adding a budget.", "danger")
        return redirect(url_for("categories_new"))

    if request.method == "POST":
        data, errors = get_budget_form_data()
        duplicate_error = validate_budget_duplicate(data)
        if duplicate_error:
            errors.append(duplicate_error)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "budgets/form.html",
                form_title="Add Budget",
                form_values=budget_form_values(data=data),
                budget=None,
                users=users,
                categories=categories,
            )

        budget = Budget(**data)
        db.session.add(budget)

        try:
            db.session.commit()
            flash("Budget created successfully.", "success")
            return redirect(url_for("budgets_list"))
        except Exception as error:
            db.session.rollback()
            flash(f"Error creating budget: {error}", "danger")

    return render_template(
        "budgets/form.html",
        form_title="Add Budget",
        form_values=budget_form_values(),
        budget=None,
        users=users,
        categories=categories,
    )


@app.route("/budgets/<int:budget_id>/edit", methods=["GET", "POST"])
def budgets_edit(budget_id):
    budget = Budget.query.get_or_404(budget_id)
    users = User.query.order_by(User.last_name, User.first_name).all()
    categories = Category.query.order_by(Category.category_name).all()

    if request.method == "POST":
        data, errors = get_budget_form_data()
        duplicate_error = validate_budget_duplicate(data, budget_id=budget.budget_id)
        if duplicate_error:
            errors.append(duplicate_error)

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "budgets/form.html",
                form_title="Edit Budget",
                form_values=budget_form_values(data=data),
                budget=budget,
                users=users,
                categories=categories,
            )

        budget.user_id = data["user_id"]
        budget.category_id = data["category_id"]
        budget.monthly_limit = data["monthly_limit"]
        budget.budget_month = data["budget_month"]
        budget.notes = data["notes"]

        try:
            db.session.commit()
            flash("Budget updated successfully.", "success")
            return redirect(url_for("budgets_list"))
        except Exception as error:
            db.session.rollback()
            flash(f"Error updating budget: {error}", "danger")

    return render_template(
        "budgets/form.html",
        form_title="Edit Budget",
        form_values=budget_form_values(budget=budget),
        budget=budget,
        users=users,
        categories=categories,
    )


@app.route("/budgets/<int:budget_id>/delete", methods=["POST"])
def budgets_delete(budget_id):
    budget = Budget.query.get_or_404(budget_id)

    try:
        db.session.delete(budget)
        db.session.commit()
        flash("Budget deleted successfully.", "success")
    except Exception as error:
        db.session.rollback()
        flash(f"Error deleting budget: {error}", "danger")

    return redirect(url_for("budgets_list"))


@app.route("/dashboard")
def dashboard():
    total_users = db.session.query(func.count(User.user_id)).scalar() or 0
    total_accounts = db.session.query(func.count(Account.account_id)).scalar() or 0
    total_transactions = (
        db.session.query(func.count(Transaction.transaction_id)).scalar() or 0
    )
    total_debit_spending = (
        db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(Transaction.transaction_type == "debit")
        .scalar()
        or 0
    )
    total_credit_income = (
        db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(Transaction.transaction_type == "credit")
        .scalar()
        or 0
    )
    average_transaction_amount = (
        db.session.query(func.coalesce(func.avg(Transaction.amount), 0)).scalar() or 0
    )

    spending_total = func.coalesce(func.sum(Transaction.amount), 0)
    spending_by_category = (
        db.session.query(
            Category.category_name,
            spending_total.label("total_spending"),
        )
        .join(Transaction)
        .filter(Transaction.transaction_type == "debit")
        .group_by(Category.category_id, Category.category_name)
        .order_by(spending_total.desc())
        .all()
    )

    year_value = func.year(Transaction.transaction_date)
    month_value = func.month(Transaction.transaction_date)
    transactions_by_month = (
        db.session.query(
            year_value.label("year"),
            month_value.label("month"),
            func.count(Transaction.transaction_id).label("transaction_count"),
        )
        .group_by(year_value, month_value)
        .order_by(year_value, month_value)
        .all()
    )

    largest_transaction = func.coalesce(func.max(Transaction.amount), 0)
    largest_transaction_per_account = (
        db.session.query(
            Account.account_name,
            largest_transaction.label("largest_amount"),
        )
        .outerjoin(Transaction)
        .group_by(Account.account_id, Account.account_name)
        .order_by(largest_transaction.desc())
        .all()
    )

    category_count = func.count(Transaction.transaction_id)
    top_categories = (
        db.session.query(
            Category.category_name,
            category_count.label("transaction_count"),
        )
        .join(Transaction)
        .group_by(Category.category_id, Category.category_name)
        .order_by(category_count.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html",
        total_users=total_users,
        total_accounts=total_accounts,
        total_transactions=total_transactions,
        total_debit_spending=total_debit_spending,
        total_credit_income=total_credit_income,
        average_transaction_amount=average_transaction_amount,
        spending_by_category=spending_by_category,
        transactions_by_month=transactions_by_month,
        largest_transaction_per_account=largest_transaction_per_account,
        top_categories=top_categories,
    )


@app.cli.command("init-db")
def init_db():
    try:
        db.drop_all()
        db.create_all()
        click.echo("Database tables dropped and recreated successfully.")
    except Exception as error:
        db.session.rollback()
        raise click.ClickException(f"Database setup failed: {error}")


@app.cli.command("seed-db")
def seed_db():
    try:
        if User.query.first():
            click.echo("Seed data already exists. No duplicate data was inserted.")
            return

        alice = User(
            first_name="Alice",
            last_name="Johnson",
            email="alice.johnson@example.com",
            phone="555-1001",
            join_date=date(2026, 1, 5),
        )
        bob = User(
            first_name="Bob",
            last_name="Martinez",
            email="bob.martinez@example.com",
            phone="555-1002",
            join_date=date(2026, 1, 10),
        )
        carol = User(
            first_name="Carol",
            last_name="Thompson",
            email="carol.thompson@example.com",
            phone="555-1003",
            join_date=date(2026, 1, 15),
        )
        david = User(
            first_name="David",
            last_name="Lee",
            email="david.lee@example.com",
            phone="555-1004",
            join_date=date(2026, 2, 1),
        )
        eva = User(
            first_name="Eva",
            last_name="Nguyen",
            email="eva.nguyen@example.com",
            phone="555-1005",
            join_date=date(2026, 2, 8),
        )
        frank = User(
            first_name="Frank",
            last_name="Garcia",
            email="frank.garcia@example.com",
            phone="555-1006",
            join_date=date(2026, 2, 12),
        )
        users = [alice, bob, carol, david, eva, frank]

        salary = Category(
            category_name="Salary",
            category_type="income",
            description="Regular job income",
        )
        freelance = Category(
            category_name="Freelance",
            category_type="income",
            description="Contract or side project income",
        )
        groceries = Category(
            category_name="Groceries",
            category_type="expense",
            description="Food and household supplies",
        )
        rent = Category(
            category_name="Rent",
            category_type="expense",
            description="Monthly housing payment",
        )
        utilities = Category(
            category_name="Utilities",
            category_type="expense",
            description="Electric, water, internet, and phone bills",
        )
        dining_out = Category(
            category_name="Dining Out",
            category_type="expense",
            description="Restaurant and cafe purchases",
        )
        transportation = Category(
            category_name="Transportation",
            category_type="expense",
            description="Gas, transit, and rideshare costs",
        )
        entertainment = Category(
            category_name="Entertainment",
            category_type="expense",
            description="Movies, games, and events",
        )
        healthcare = Category(
            category_name="Healthcare",
            category_type="expense",
            description="Medical and pharmacy costs",
        )
        investment = Category(
            category_name="Investment",
            category_type="income",
            description="Investment earnings",
        )
        categories = [
            salary,
            freelance,
            groceries,
            rent,
            utilities,
            dining_out,
            transportation,
            entertainment,
            healthcare,
            investment,
        ]

        alice_checking = Account(
            user=alice,
            account_name="Alice Checking",
            account_type="checking",
            bank_name="First City Bank",
            balance=2450.75,
        )
        alice_savings = Account(
            user=alice,
            account_name="Alice Savings",
            account_type="savings",
            bank_name="First City Bank",
            balance=8200.00,
        )
        bob_checking = Account(
            user=bob,
            account_name="Bob Checking",
            account_type="checking",
            bank_name="Community Bank",
            balance=1325.40,
        )
        carol_credit_card = Account(
            user=carol,
            account_name="Carol Credit Card",
            account_type="credit card",
            bank_name="Metro Credit",
            balance=420.15,
        )
        david_savings = Account(
            user=david,
            account_name="David Savings",
            account_type="savings",
            bank_name="Neighborhood Bank",
            balance=6100.00,
        )
        eva_checking = Account(
            user=eva,
            account_name="Eva Checking",
            account_type="checking",
            bank_name="First City Bank",
            balance=1750.30,
        )
        frank_investment = Account(
            user=frank,
            account_name="Frank Investment",
            account_type="investment",
            bank_name="Future Investments",
            balance=15400.25,
        )
        accounts = [
            alice_checking,
            alice_savings,
            bob_checking,
            carol_credit_card,
            david_savings,
            eva_checking,
            frank_investment,
        ]

        transactions = [
            Transaction(
                account=alice_checking,
                category=salary,
                amount=3200.00,
                transaction_type="credit",
                description="May paycheck",
                merchant="Alice Employer",
                transaction_date=date(2026, 5, 1),
                posted_date=date(2026, 5, 1),
                days_to_post=0,
                is_recurring=True,
            ),
            Transaction(
                account=alice_checking,
                category=groceries,
                amount=94.26,
                transaction_type="debit",
                description="Weekly groceries",
                merchant="Fresh Market",
                transaction_date=date(2026, 5, 3),
                posted_date=date(2026, 5, 4),
                days_to_post=1,
                is_recurring=False,
            ),
            Transaction(
                account=alice_checking,
                category=rent,
                amount=1250.00,
                transaction_type="debit",
                description="May rent",
                merchant="Lakeview Apartments",
                transaction_date=date(2026, 5, 5),
                posted_date=date(2026, 5, 5),
                days_to_post=0,
                is_recurring=True,
            ),
            Transaction(
                account=alice_savings,
                category=investment,
                amount=35.50,
                transaction_type="credit",
                description="Monthly interest",
                merchant="First City Bank",
                transaction_date=date(2026, 5, 6),
                posted_date=date(2026, 5, 6),
                days_to_post=0,
                is_recurring=True,
            ),
            Transaction(
                account=bob_checking,
                category=freelance,
                amount=750.00,
                transaction_type="credit",
                description="Website project",
                merchant="Local Client",
                transaction_date=date(2026, 5, 7),
                posted_date=date(2026, 5, 8),
                days_to_post=1,
                is_recurring=False,
            ),
            Transaction(
                account=bob_checking,
                category=dining_out,
                amount=48.90,
                transaction_type="debit",
                description="Dinner with friends",
                merchant="Corner Bistro",
                transaction_date=date(2026, 5, 8),
                posted_date=date(2026, 5, 9),
                days_to_post=1,
                is_recurring=False,
            ),
            Transaction(
                account=carol_credit_card,
                category=utilities,
                amount=116.75,
                transaction_type="debit",
                description="Electric bill",
                merchant="City Power",
                transaction_date=date(2026, 5, 9),
                posted_date=date(2026, 5, 10),
                days_to_post=1,
                is_recurring=True,
            ),
            Transaction(
                account=carol_credit_card,
                category=healthcare,
                amount=28.40,
                transaction_type="debit",
                description="Pharmacy purchase",
                merchant="HealthPlus Pharmacy",
                transaction_date=date(2026, 5, 10),
                posted_date=date(2026, 5, 11),
                days_to_post=1,
                is_recurring=False,
            ),
            Transaction(
                account=david_savings,
                category=salary,
                amount=2850.00,
                transaction_type="credit",
                description="May paycheck",
                merchant="David Employer",
                transaction_date=date(2026, 5, 11),
                posted_date=date(2026, 5, 11),
                days_to_post=0,
                is_recurring=True,
            ),
            Transaction(
                account=eva_checking,
                category=transportation,
                amount=62.30,
                transaction_type="debit",
                description="Gas refill",
                merchant="Quick Fuel",
                transaction_date=date(2026, 5, 12),
                posted_date=date(2026, 5, 13),
                days_to_post=1,
                is_recurring=False,
            ),
            Transaction(
                account=eva_checking,
                category=entertainment,
                amount=39.99,
                transaction_type="debit",
                description="Streaming subscription",
                merchant="StreamWave",
                transaction_date=date(2026, 5, 13),
                posted_date=date(2026, 5, 13),
                days_to_post=0,
                is_recurring=True,
            ),
            Transaction(
                account=frank_investment,
                category=investment,
                amount=210.45,
                transaction_type="credit",
                description="Dividend payment",
                merchant="Future Investments",
                transaction_date=date(2026, 5, 14),
                posted_date=date(2026, 5, 15),
                days_to_post=1,
                is_recurring=False,
            ),
        ]

        budgets = [
            Budget(
                user=alice,
                category=groceries,
                monthly_limit=450.00,
                budget_month=date(2026, 5, 1),
                notes="Alice grocery budget",
            ),
            Budget(
                user=alice,
                category=dining_out,
                monthly_limit=180.00,
                budget_month=date(2026, 5, 1),
                notes="Alice restaurant budget",
            ),
            Budget(
                user=bob,
                category=transportation,
                monthly_limit=220.00,
                budget_month=date(2026, 5, 1),
                notes="Bob commute budget",
            ),
            Budget(
                user=bob,
                category=entertainment,
                monthly_limit=150.00,
                budget_month=date(2026, 5, 1),
                notes="Bob entertainment budget",
            ),
            Budget(
                user=carol,
                category=utilities,
                monthly_limit=300.00,
                budget_month=date(2026, 5, 1),
                notes="Carol utility budget",
            ),
            Budget(
                user=carol,
                category=healthcare,
                monthly_limit=125.00,
                budget_month=date(2026, 5, 1),
                notes="Carol healthcare budget",
            ),
            Budget(
                user=david,
                category=rent,
                monthly_limit=1300.00,
                budget_month=date(2026, 5, 1),
                notes="David rent budget",
            ),
            Budget(
                user=eva,
                category=groceries,
                monthly_limit=400.00,
                budget_month=date(2026, 5, 1),
                notes="Eva grocery budget",
            ),
        ]

        db.session.add_all(users)
        db.session.add_all(categories)
        db.session.add_all(accounts)
        db.session.add_all(transactions)
        db.session.add_all(budgets)
        db.session.commit()
        click.echo("Sample data inserted successfully.")
    except Exception as error:
        db.session.rollback()
        raise click.ClickException(f"Database seeding failed: {error}")


if __name__ == "__main__":
    app.run(debug=True)
