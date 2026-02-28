from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "bouquet-secret-key"

db = SQLAlchemy(app)

# ------------------
# Models
# ------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Flower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, default=50)
    image = db.Column(db.String(200), nullable=False)

class Bouquet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    size = db.Column(db.String(20))
    flowers = db.Column(db.Text)  # "1:2,3:1"
    style = db.Column(db.String(100))
    theme = db.Column(db.String(100))
    card = db.Column(db.String(200))
    total_price = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ------------------
# Bouquet Size Config
# ------------------
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
def home():
    return render_template("index.html")

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

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db.session.add(
            User(
                username=request.form["username"],
                password=request.form["password"]
            )
        )
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")

# ------------------
# Create Bouquet Flow
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
    if request.method == "POST":
        selected = {}
        for f in Flower.query.all():
            qty = int(request.form.get(str(f.id), 0))
            if qty > 0:
                selected[str(f.id)] = qty
        session["bouquet"]["flowers"] = selected
        return redirect("/style")

    return render_template("select_flowers.html", flowers=Flower.query.all())

@app.route("/style", methods=["GET", "POST"])
def style():
    if request.method == "POST":
        session["bouquet"]["style"] = request.form["style"]
        session["bouquet"]["theme"] = request.form["theme"]
        session["bouquet"]["card"] = request.form.get("card", "-")
        return redirect("/summary")

    return render_template("style.html")

@app.route("/summary")
def summary():
    bouquet = session["bouquet"]
    fee = BOUQUET_SIZE[bouquet["size"]]["fee"]

    total = fee
    flower_detail = []

    for fid, qty in bouquet["flowers"].items():
        flower = Flower.query.get(int(fid))
        subtotal = flower.price * qty
        total += subtotal
        flower_detail.append((flower, qty, subtotal))

    session["bouquet"]["total"] = total

    return render_template(
        "summary.html",
        bouquet=bouquet,
        flowers=flower_detail,
        fee=fee,
        total=total
    )

@app.route("/save-bouquet")
def save_bouquet():
    b = session["bouquet"]

    bouquet = Bouquet(
        user_id=session["user_id"],
        size=b["size"],
        flowers=",".join([f"{k}:{v}" for k, v in b["flowers"].items()]),
        style=b["style"],
        theme=b["theme"],
        card=b["card"],
        total_price=b["total"]
    )

    db.session.add(bouquet)
    db.session.commit()
    session.pop("bouquet")

    return redirect("/history")

@app.route("/history")
def history():
    if not login_required():
        return redirect("/login")

    bouquets = Bouquet.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Bouquet.created_at.desc()).all()

    return render_template("history.html", bouquets=bouquets)

# ------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)