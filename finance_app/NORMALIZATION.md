# Normalization Notes

## Goal

The database is designed to store personal finance information in a simple, organized way.

## Tables

### users

Stores user information. Each user has one row.

### accounts

Stores financial accounts that belong to users, such as checking, savings, or credit card accounts.

### categories

Stores transaction categories, such as Salary, Groceries, Rent, and Entertainment.

### transactions

Stores money movement records. Each transaction connects to one account and one category.

## First Normal Form

Each table has a primary key, and each column stores one value. There are no repeating groups.

## Second Normal Form

Each non-key column depends on the whole primary key. Since the tables use single-column primary keys, the design avoids partial dependency.

## Third Normal Form

Non-key columns do not depend on other non-key columns. For example, category details are stored in the categories table instead of being repeated in every transaction.
