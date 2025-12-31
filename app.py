import sqlite3
import os
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
