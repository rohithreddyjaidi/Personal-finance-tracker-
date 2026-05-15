from datetime import date
from decimal import Decimal, InvalidOperation

import click
from flask import Flask, flash, redirect, render_template, request, url_for
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
