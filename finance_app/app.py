from datetime import date

import click
from flask import Flask, render_template

from config import Config
from extensions import db
from models import Account, Budget, Category, Transaction, User


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")


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
