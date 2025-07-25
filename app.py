from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'secretkey'  # Needed for session

# DB init
def init_db():
    conn = sqlite3.connect('employee.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS employee (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        age INTEGER,
                        department TEXT,
                        salary REAL)''')
    conn.commit()
    conn.close()

# Admin login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect('employee.db')
    employees = conn.execute("SELECT * FROM employee").fetchall()
    conn.close()
    return render_template('dashboard.html', employees=employees)

# Add employee
@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if not session.get('admin'):
        return redirect('/')
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        dept = request.form['department']
        salary = request.form['salary']
        conn = sqlite3.connect('employee.db')
        conn.execute("INSERT INTO employee (name, age, department, salary) VALUES (?, ?, ?, ?)",
                     (name, age, dept, salary))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('add_employee.html')

# Edit employee
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    conn = sqlite3.connect('employee.db')
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        dept = request.form['department']
        salary = request.form['salary']
        conn.execute("UPDATE employee SET name=?, age=?, department=?, salary=? WHERE id=?",
                     (name, age, dept, salary, id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    employee = conn.execute("SELECT * FROM employee WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template('edit_employee.html', employee=employee)

# Delete employee
@app.route('/delete/<int:id>')
def delete_employee(id):
    conn = sqlite3.connect('employee.db')
    conn.execute("DELETE FROM employee WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

#salar
@app.route('/salary/<int:id>', methods=['GET', 'POST'])
def manage_salary(id):
    if not session.get('admin'):
        return redirect('/')
    conn = sqlite3.connect('employee.db')
    if request.method == 'POST':
        new_salary = float(request.form['salary'])
        conn.execute("UPDATE employee SET salary=? WHERE id=?", (new_salary, id))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    employee = conn.execute("SELECT * FROM employee WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template('salary.html', employee=employee)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
