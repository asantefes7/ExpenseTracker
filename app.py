from flask import Flask, jsonify, request, render_template  # type: ignore
from flask_sqlalchemy import SQLAlchemy  # type: ignore
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Expense model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


# Initialize the database
with app.app_context():
    db.create_all()


# Flask Routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add_expense():
    data = request.json
    category = data.get('category')
    description = data.get('description', '')
    amount = data.get('amount')

    if not category or not amount:
        return jsonify(message="Category and amount are required."), 400

    expense = Expense(category=category, description=description, amount=amount)
    db.session.add(expense)
    db.session.commit()
    return jsonify(message="Expense added successfully!")


@app.route('/expenses', methods=['GET'])
def view_expenses():
    expenses = Expense.query.all()
    expenses_list = [
        {"id": exp.id, "category": exp.category, "description": exp.description,
         "amount": exp.amount, "date": exp.date.strftime('%Y-%m-%d %H:%M:%S')}
        for exp in expenses
    ]
    return jsonify(expenses=expenses_list)


@app.route('/total', methods=['GET'])
def total_expenses():
    total = db.session.query(db.func.sum(Expense.amount)).scalar() or 0.0
    return jsonify(total_expenses=total)


@app.route('/edit/<int:expense_id>', methods=['PUT'])
def edit_expense(expense_id):
    data = request.json
    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify(message="Expense not found."), 404

    expense.category = data.get('category', expense.category)
    expense.description = data.get('description', expense.description)
    expense.amount = data.get('amount', expense.amount)
    db.session.commit()

    return jsonify(message="Expense updated successfully!")


@app.route('/delete/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if not expense:
        return jsonify(message="Expense not found."), 404

    db.session.delete(expense)
    db.session.commit()
    return jsonify(message="Expense deleted successfully!")


# CLI Functionality
def interactive_mode():
    print("\nWelcome to the CLI Expense Tracker!")
    while True:
        print("\nOptions:")
        print("1. Add Expense")
        print("2. View All Expenses")
        print("3. View Total Expenses")
        print("4. Edit Expense")
        print("5. Delete Expense")
        print("6. Exit")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            category = input("Enter category: ")
            description = input("Enter description: ")
            amount = float(input("Enter amount: "))
            expense = Expense(category=category, description=description, amount=amount)
            db.session.add(expense)
            db.session.commit()
            print("Expense added successfully!")
        elif choice == "2":
            expenses = Expense.query.all()
            if not expenses:
                print("No expenses found.")
            else:
                for exp in expenses:
                    print(f"ID: {exp.id}, Category: {exp.category}, Description: {exp.description}, "
                          f"Amount: {exp.amount}, Date: {exp.date.strftime('%Y-%m-%d %H:%M:%S')}")
        elif choice == "3":
            total = db.session.query(db.func.sum(Expense.amount)).scalar() or 0.0
            print(f"Total Expenses: ${total:.2f}")
        elif choice == "4":
            expense_id = int(input("Enter expense ID to edit: "))
            expense = Expense.query.get(expense_id)
            if not expense:
                print("Expense not found.")
            else:
                category = input(f"Enter new category (current: {expense.category}): ") or expense.category
                description = input(f"Enter new description (current: {expense.description}): ") or expense.description
                amount = input(f"Enter new amount (current: {expense.amount}): ") or expense.amount
                expense.category = category
                expense.description = description
                expense.amount = float(amount)
                db.session.commit()
                print("Expense updated successfully!")
        elif choice == "5":
            expense_id = int(input("Enter expense ID to delete: "))
            expense = Expense.query.get(expense_id)
            if not expense:
                print("Expense not found.")
            else:
                db.session.delete(expense)
                db.session.commit()
                print("Expense deleted successfully!")
        elif choice == "6":
            print("Exiting CLI... Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == '__main__':
    print("Choose your mode:")
    print("1. Flask (Web-based)")
    print("2. CLI (Command Line Interface)")
    mode = input("Enter 1 for Flask or 2 for CLI: ").strip()
    if mode == "1":
        app.run(debug=True)
    elif mode == "2":
        interactive_mode()
    else:
        print("Invalid input. Exiting.")
