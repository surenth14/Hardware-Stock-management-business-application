from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'a_very_secret_key_for_dev')

# --- User Data (In-memory storage with hardcoded hashed passwords and roles) ---
USERS = {
    'admin': {'password_hash': generate_password_hash('admin_password'), 'role': 'admin'},
    'user1': {'password_hash': generate_password_hash('user1_password'), 'role': 'user'},
    'user2': {'password_hash': generate_password_hash('user2_password'), 'role': 'user'}
}

# --- Inventory Data ---
inventory = []
next_id = 1

# --- Helper Functions ---
def is_logged_in():
    return 'username' in session

def get_current_user_role():
    return session.get('role')

# --- Routes ---
@app.route('/')
def index():
    if not is_logged_in():
        flash('Please log in to access the inventory.', 'warning')
        return redirect(url_for('login'))
    show_add_button = get_current_user_role() == 'admin'
    # Pass session to template to access username
    return render_template('index.html', inventory=inventory, show_add_button=show_add_button, session=session)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    global next_id
    if not is_logged_in():
        flash('Please log in to add items.', 'warning')
        return redirect(url_for('login'))
    if get_current_user_role() != 'admin':
        flash('You do not have permission to add items.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        item_name = request.form['item_name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        inventory.append({'id': next_id, 'name': item_name, 'quantity': quantity, 'price': price})
        next_id += 1
        flash('Item added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_item.html')

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    if not is_logged_in():
        flash('Please log in to edit items.', 'warning')
        return redirect(url_for('login'))
    if get_current_user_role() != 'admin':
        flash('You do not have permission to edit items.', 'danger')
        return redirect(url_for('index'))

    item_to_edit = next((item for item in inventory if item['id'] == item_id), None)
    if not item_to_edit:
        flash('Item not found.', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        item_to_edit['name'] = request.form['item_name']
        item_to_edit['quantity'] = int(request.form['quantity'])
        item_to_edit['price'] = float(request.form['price'])
        flash('Item updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('edit_item.html', item=item_to_edit)

@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    global inventory
    if not is_logged_in():
        flash('Please log in to delete items.', 'warning')
        return redirect(url_for('login'))
    if get_current_user_role() != 'admin':
        flash('You do not have permission to delete items.', 'danger')
        return redirect(url_for('index'))

    initial_length = len(inventory)
    inventory = [item for item in inventory if item['id'] != item_id]
    if len(inventory) < initial_length:
        flash('Item deleted successfully!', 'success')
    else:
        flash('Item not found.', 'danger')
    return redirect(url_for('index'))

# --- Authentication Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = USERS.get(username)

        if user_data and check_password_hash(user_data['password_hash'], password):
            session['username'] = username
            session['role'] = user_data['role']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)
