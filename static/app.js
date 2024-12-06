document.getElementById('addExpenseForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const category = document.getElementById('category').value;
    const description = document.getElementById('description').value;
    const amount = parseFloat(document.getElementById('amount').value);

    const response = await fetch('/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ category, description, amount }),
    });

    if (response.ok) {
        loadExpenses();
        document.getElementById('addExpenseForm').reset();
    } else {
        alert('Failed to add expense.');
    }
});

async function loadExpenses() {
    const response = await fetch('/expenses');
    const data = await response.json();
    const expensesList = document.getElementById('expensesList');
    expensesList.innerHTML = '';
    data.expenses.forEach((expense) => {
        const li = document.createElement('li');
        li.textContent = `${expense.category}: $${expense.amount} (${expense.description}) on ${expense.date}`;

        // Edit button
        const editButton = document.createElement('button');
        editButton.textContent = 'Edit';
        editButton.onclick = () => editExpense(expense.id, expense.category, expense.description, expense.amount);

        // Delete button
        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.onclick = () => deleteExpense(expense.id);

        li.appendChild(editButton);
        li.appendChild(deleteButton);

        expensesList.appendChild(li);
    });
// update total expenses
    const totalResponse = await fetch('/total');
    const totalData = await totalResponse.json();
    document.getElementById('totalExpenses').textContent = `$${totalData.total_expenses.toFixed(2)}`;
}

// Function to edit an expense
function editExpense(id, category, description, amount) {
    const categoryInput = document.getElementById('category');
    const descriptionInput = document.getElementById('description');
    const amountInput = document.getElementById('amount');

    // Populate the form with the current expense data
    categoryInput.value = category;
    descriptionInput.value = description;
    amountInput.value = amount;

    // Change the form submission to edit the expense
    const form = document.getElementById('addExpenseForm');
    form.onsubmit = async (e) => {
        e.preventDefault();

        const updatedCategory = categoryInput.value;
        const updatedDescription = descriptionInput.value;
        const updatedAmount = parseFloat(amountInput.value);

        const response = await fetch(`/edit/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ category: updatedCategory, description: updatedDescription, amount: updatedAmount }),
        });

        if (response.ok) {
            loadExpenses();  // Reload the expenses list
            form.reset();    // Reset the form fields
            form.onsubmit = loadExpenses;  // Reset the form submission to add expense
        } else {
            alert('Failed to update expense.');
        }
    };
}

// Function to delete an expense
async function deleteExpense(id) {
    const response = await fetch(`/delete/${id}`, {
        method: 'DELETE',
    });

    if (response.ok) {
        loadExpenses();  // Reload the expenses list
    } else {
        alert('Failed to delete expense.');
    }
}

loadExpenses();
