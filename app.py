from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"
DB = "cars.db"

# ---------------- DATABASE ----------------
def get_db_connection():
    if not os.path.exists(DB):
        raise FileNotFoundError(f"Database '{DB}' not found.")
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def get_master_columns():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(cars_master)")
    columns = [row[1] for row in cur.fetchall()]
    conn.close()
    return columns

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    # Get categories for filter
    cur.execute("SELECT DISTINCT category FROM cars_master")
    categories = [row[0] for row in cur.fetchall()]

    category = request.form.get("category") if request.method=="POST" else "All"
    columns = get_master_columns()

    if category != "All":
        cur.execute("SELECT * FROM cars_master WHERE category=?", (category,))
    else:
        cur.execute("SELECT * FROM cars_master")
    cars = cur.fetchall()
    conn.close()

    return render_template("index.html", cars=cars, columns=columns, categories=categories, selected_category=category)

@app.route("/add", methods=["GET", "POST"])
def add_car():
    columns = get_master_columns()[1:]  # skip car_id
    if request.method == "POST":
        data = {key: request.form[key] for key in request.form}
        col_names = ",".join(data.keys())
        placeholders = ",".join("?"*len(data))
        values = list(data.values())

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(f"INSERT INTO cars_master ({col_names}) VALUES ({placeholders})", values)
        conn.commit()
        conn.close()
        flash("Car added successfully!", "success")
        return redirect(url_for("index"))
    return render_template("add.html", columns=columns)

@app.route("/update/<int:car_id>", methods=["GET", "POST"])
def update_car(car_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM cars_master WHERE car_id=?", (car_id,))
    car = cur.fetchone()
    columns = get_master_columns()[1:]  # skip car_id

    if request.method=="POST":
        data = {key: request.form[key] for key in request.form}
        set_clause = ",".join([f"{k}=?" for k in data])
        values = list(data.values()) + [car_id]
        cur.execute(f"UPDATE cars_master SET {set_clause} WHERE car_id=?", values)
        conn.commit()
        conn.close()
        flash("Car updated successfully!", "success")
        return redirect(url_for("index"))

    conn.close()
    return render_template("update.html", car=car, columns=columns)

@app.route("/delete/<int:car_id>")
def delete_car(car_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM cars_master WHERE car_id=?", (car_id,))
    conn.commit()
    conn.close()
    flash("Car deleted successfully!", "danger")
    return redirect(url_for("index"))

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Car Management</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-dark text-light">
<div class="container mt-4">
<h1>🚗 Car Management System</h1>

<form method="post" class="mb-3">
    <select name="category" class="form-select w-25 d-inline-block">
        <option value="All" {% if selected_category=="All" %}selected{% endif %}>All</option>
        {% for c in categories %}
            <option value="{{c}}" {% if selected_category==c %}selected{% endif %}>{{c}}</option>
        {% endfor %}
    </select>
    <button type="submit" class="btn btn-primary ms-2">Filter</button>
    <a href="{{ url_for('add_car') }}" class="btn btn-success ms-2">Add Car</a>
    <a href="{{ url_for('index') }}" class="btn btn-info ms-2">Refresh</a>
</form>

{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    {% for category, msg in messages %}
      <div class="alert alert-{{category}}">{{msg}}</div>
    {% endfor %}
  {% endif %}
{% endwith %}

<table class="table table-striped table-hover table-dark">
<thead>
<tr>
{% for col in columns %}
<th>{{col}}</th>
{% endfor %}
<th>Actions</th>
</tr>
</thead>
<tbody>
{% for car in cars %}
<tr>
{% for col in columns %}
<td>{{car[col]}}</td>
{% endfor %}
<td>
<a href="{{ url_for('update_car', car_id=car['car_id']) }}" class="btn btn-warning btn-sm">Edit</a>
<a href="{{ url_for('delete_car', car_id=car['car_id']) }}" class="btn btn-danger btn-sm">Delete</a>
</td>
</tr>
{% endfor %}
</tbody>
</table>
</div>
</body>
</html>
