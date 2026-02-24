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
    flowers = [
        {
            "id": 1,
            "name": "Lily",
            "image": "images/flowers/1_Lily.png"
        },
        {
            "id": 2,
            "name": "Daisy",
            "image": "images/flowers/2_Daisy.png"
        },
        {
            "id": 3,
            "name": "Dandelion",
            "image": "images/flowers/3_Dandelion.png"
        },
        {
            "id": 4,
            "name": "Sunflower",
            "image": "images/flowers/4_Sunflower.png"
        },
        {
            "id": 5,
            "name": "Bluedaze",
            "image": "images/flowers/5_Bluedaze.png"
        },
        {
            "id": 6,
            "name": "Lavendula spica",
            "image": "images/flowers/6_Lavendula_spica.png"
        },
        {
            "id": 7,
            "name": "Peony",
            "image": "images/flowers/7_Peony.png"
        },
        {
            "id": 8,
            "name": "Red Holly",
            "image": "images/flowers/8_Red_Holly.png"
        },
        {
            "id": 9,
            "name": "Calluna",
            "image": "images/flowers/9_Calluna.png"
        },
        {
            "id": 10,
            "name": "Tulip",
            "image": "images/flowers/10_Tulip.png"
        },
    ]

    return render_template("flowers.html", flowers=flowers)

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

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
