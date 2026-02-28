from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "bouquet-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ------------------
# Models
# ------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Bouquet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    size = db.Column(db.String(20))
    flowers = db.Column(db.Text)
    style = db.Column(db.String(100))
    theme = db.Column(db.String(50))
    card = db.Column(db.String(200))
    total_price = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ------------------
# Static Flower Data
# ------------------
FLOWERS = [
        {"id": 1, "name": "Lily of the Valley", "price": 120, "image": "images/flowers/1.png"},
        {"id": 2, "name": "White Rose", "price": 40, "image": "images/flowers/2.png"},
        {"id": 3, "name": "Dusty Purple Rose", "price": 60, "image": "images/flowers/3.png"},
        {"id": 4, "name": "Waxflower", "price": 30, "image": "images/flowers/4.png"},
        {"id": 5, "name": "Carnation", "price": 25, "image": "images/flowers/5.png"},
        {"id": 6, "name": "Gerbera", "price": 30, "image": "images/flowers/6.png"},
        {"id": 7, "name": "Hydrangea", "price": 150, "image": "images/flowers/7.png"},
        {"id": 8, "name": "Tulip", "price": 80, "image": "images/flowers/8.png"},
        {"id": 9, "name": "Hyacinth", "price": 70, "image": "images/flowers/9.png"},
        {"id": 10, "name": "Calla Lily", "price": 90, "image": "images/flowers/10.png"},
        {"id": 11, "name": "Phalaenopsis Orchid", "price": 180, "image": "images/flowers/11.png"},
        {"id": 12, "name": "Marigold", "price": 15, "image": "images/flowers/12.png"},
        {"id": 13, "name": "Daisy", "price": 20, "image": "images/flowers/13.png"},
        {"id": 14, "name": "Anthurium", "price": 100, "image": "images/flowers/14.png"},
        {"id": 15, "name": "Sunflower", "price": 35, "image": "images/flowers/15.png"},
        {"id": 16, "name": "Aster", "price": 25, "image": "images/flowers/16.png"},
        {"id": 17, "name": "Gypsophila", "price": 20, "image": "images/flowers/17.png"},
        {"id": 18, "name": "Lily", "price": 90, "image": "images/flowers/18.png"},
        {"id": 19, "name": "Eucalyptus", "price": 35, "image": "images/flowers/19.png"},
]

BOUQUET_SIZE = {
    "small": {"fee": 200},
    "medium": {"fee": 300},
    "large": {"fee": 500},
}

# ------------------
# Helper
# ------------------
def login_required():
    if "user_id" not in session:
        flash("กรุณาเข้าสู่ระบบก่อน", "warning")
        return False
    return True

# ------------------
# Routes
# ------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/flowers")
def flowers():
    return render_template("flowers.html", flowers=FLOWERS)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form["username"],
            password=request.form["password"]
        ).first()

        if user:
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect("/")
        flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ------------------
# Create Bouquet (ต้อง login)
# ------------------
@app.route("/create-bouquet", methods=["GET", "POST"])
def create_bouquet():
    if not login_required():
        return redirect("/login")

    if request.method == "POST":
        session["bouquet"] = {
            "size": request.form["size"],
            "flowers": {},
            "style": "",
            "theme": "",
            "card": "-"
        }
        return redirect("/select-flowers")

    return render_template("create_bouquet.html", sizes=BOUQUET_SIZE)

@app.route("/select-flowers", methods=["GET", "POST"])
def select_flowers():
    if not login_required():
        return redirect("/login")

    if request.method == "POST":
        selected = {}
        for f in FLOWERS:
            qty = int(request.form.get(str(f["id"]), 0))
            if qty > 0:
                selected[str(f["id"])] = qty

        session["bouquet"]["flowers"] = selected
        return redirect("/style")

    return render_template("select_flowers.html", flowers=FLOWERS)

@app.route("/style", methods=["GET", "POST"])
def style():
    if not login_required():
        return redirect("/login")

    if request.method == "POST":
        session["bouquet"]["style"] = request.form["style"]
        session["bouquet"]["theme"] = request.form["theme"]
        session["bouquet"]["card"] = request.form.get("card", "-")
        return redirect("/summary")

    return render_template("style.html")

@app.route("/summary")
def summary():
    if not login_required():
        return redirect("/login")

    bouquet = session["bouquet"]
    fee = BOUQUET_SIZE[bouquet["size"]]["fee"]

    total = fee
    detail = []

    for fid, qty in bouquet["flowers"].items():
        flower = next(f for f in FLOWERS if f["id"] == int(fid))
        subtotal = flower["price"] * qty
        total += subtotal
        detail.append((flower, qty, subtotal))

    bouquet["total"] = total

    return render_template("summary.html", bouquet=bouquet, flowers=detail, fee=fee, total=total)

@app.route("/history")
def history():
    if not login_required():
        return redirect("/login")

    bouquets = Bouquet.query.filter_by(user_id=session["user_id"]).all()
    return render_template("history.html", bouquets=bouquets)

# ------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)