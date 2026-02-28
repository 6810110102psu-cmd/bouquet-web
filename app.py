from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, session, flash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "bouquet-secret-key"

db = SQLAlchemy(app)
# สร้างฐานข้อมูลครั้งแรก
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Flower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False)

from datetime import datetime

class Bouquet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    flowers = db.Column(db.Text)  # เก็บเป็นข้อความ เช่น "1,2,3"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/flowers")
def flowers():
    flowers = Flower.query.all()
    return render_template("flowers.html", flowers=flowers)

@app.route("/add_to_bouquet/<int:flower_id>")
def add_to_bouquet(flower_id):
    if "bouquet" not in session:
        session["bouquet"] = []

    session["bouquet"].append(flower_id)
    session.modified = True

    flash("เพิ่มดอกไม้ลงในช่อแล้ว", "success")
    return redirect("/flowers")
@app.route("/preview")
def preview():
    flower_ids = session.get("bouquet", [])

    selected_flowers = Flower.query.filter(
        Flower.id.in_(flower_ids)
    ).all()

    return render_template("preview.html", flowers=selected_flowers)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login successful!", "success")
            return redirect("/")
        else:
            flash("Invalid username or password", "danger")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")

import random

@app.route("/blessing")
def blessing():
    messages = [
        "ขอให้เต็มไปด้วยรอยยิ้ม",
        "ขอให้มีความสุขในทุกวัน",
        "ขอให้สมหวังในสิ่งที่ตั้งใจ",
        "ขอให้วันนี้อ่อนโยนกับหัวใจคุณ",
        "ขอให้ความรักรายล้อมคุณเสมอ"
    ]

    message = random.choice(messages)
    return render_template("blessing.html", message=message)

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect("/")

@app.route("/save_bouquet")
def save_bouquet():
    if "user_id" not in session:
        flash("กรุณาเข้าสู่ระบบก่อนบันทึกช่อดอกไม้", "warning")
        return redirect("/login")

    flower_ids = session.get("bouquet", [])

    bouquet = Bouquet(
        user_id=session["user_id"],
        flowers=",".join(map(str, flower_ids))
    )
    db.session.add(bouquet)
    db.session.commit()

    session.pop("bouquet", None)  # เคลียร์ช่อหลังบันทึก
    flash("บันทึกช่อดอกไม้เรียบร้อย", "success")

    return redirect("/history")

@app.route("/remove/<int:flower_id>")
def remove_flower(flower_id):
    if "bouquet" in session:
        session["bouquet"] = [
            f for f in session["bouquet"] if f != flower_id
        ]
        session.modified = True

    return redirect("/preview")

@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect("/login")

    bouquets = Bouquet.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Bouquet.created_at.desc()).all()

    flower_map = {f.id: f.name for f in Flower.query.all()}

    return render_template(
        "history.html",
        bouquets=bouquets,
        flower_map=flower_map
    )
    
@app.route("/final")
def final():
    return render_template("final.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)