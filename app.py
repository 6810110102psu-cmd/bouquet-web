from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import re
import pytz
from datetime import datetime

app = Flask(__name__)
app.secret_key = "bouquet-secret-key"

# ------------------
# Database Config
# ------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ------------------
# Models
# ------------------

# ฟังก์ชันดึงเวลาปัจจุบันของไทย (GMT+7)
def get_bangkok_time():
    tz = pytz.timezone('Asia/Bangkok')
    return datetime.now(tz)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=get_bangkok_time)

class Bouquet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    size = db.Column(db.String(50))
    flowers = db.Column(db.Text)
    style = db.Column(db.String(100))
    theme = db.Column(db.String(50))
    card = db.Column(db.Text)
    occasion = db.Column(db.String(100))
    total_price = db.Column(db.Float)
    
    # ข้อมูลการจัดส่ง
    receive_date = db.Column(db.String(50))
    receive_time = db.Column(db.String(50))
    method = db.Column(db.String(50))
    detail = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=get_bangkok_time)

# ------------------
# Static Data
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
    "small": {"name": "ช่อเล็ก", "fee": 200, "min": 5, "max": 9},
    "medium": {"name": "ช่อกลาง", "fee": 300, "min": 10, "max": 19},
    "large": {"name": "ช่อใหญ่", "fee": 500, "min": 20, "max": 39},
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

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if len(username) < 8:
            flash("Username ต้องมีความยาวอย่างน้อย 8 ตัวอักษร", "danger")
            return redirect("/register")
        if len(password) < 8:
            flash("Password ต้องมีความยาวอย่างน้อย 8 ตัวอักษร", "danger")
            return redirect("/register")
        if not re.search(r"[A-Z]", password):
            flash("Password ต้องมีตัวพิมพ์ใหญ่ (A-Z) อย่างน้อย 1 ตัว", "danger")
            return redirect("/register")
        if not re.search(r"\d", password):
            flash("Password ต้องมีตัวเลข (0-9) อย่างน้อย 1 ตัว", "danger")
            return redirect("/register")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("ชื่อผู้ใช้นี้ถูกใช้ไปแล้ว", "danger")
            return redirect("/register")

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ", "success")
        return redirect("/login")

    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/create-bouquet", methods=["GET", "POST"])
def create_bouquet():
    if not login_required(): return redirect("/login")

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
    if not login_required(): return redirect("/login")

    if request.method == "POST":
        selected = {}
        for f in FLOWERS:
            qty = int(request.form.get(str(f["id"]), 0))
            if qty > 0:
                selected[str(f["id"])] = qty

        session["bouquet"]["flowers"] = selected
        session.modified = True
        return redirect("/style")

    return render_template("select_flowers.html", flowers=FLOWERS)

@app.route("/style", methods=["GET", "POST"])
def style():
    if not login_required(): 
        return redirect("/login")
        
    if request.method == "POST":
        # รับค่าจากฟอร์มและเก็บลงใน Session ก้อน bouquet
        session["bouquet"]["style"] = request.form.get("style", "-")
        session["bouquet"]["theme"] = request.form.get("theme", "-")
        session["bouquet"]["card"] = request.form.get("card", "-")
        
        # --- เพิ่มบรรทัดนี้เพื่อรับค่า "เนื่องในโอกาส" ---
        session["bouquet"]["occasion"] = request.form.get("occasion", "-")
        # ------------------------------------------
        
        session.modified = True # บังคับให้ Flask บันทึกการเปลี่ยนแปลงใน Session
        return redirect("/delivery")
        
    return render_template("style.html")

@app.route("/delivery", methods=["GET", "POST"])
def delivery():
    if not login_required(): return redirect("/login")
    if request.method == "POST":
        session["bouquet"]["fullname"] = request.form.get("fullname")
        session["bouquet"]["phone"] = request.form.get("phone")
        session["bouquet"]["method"] = request.form.get("method")
        session["bouquet"]["receive_date"] = request.form.get("receive_date")
        session["bouquet"]["receive_time"] = request.form.get("receive_time")
        session["bouquet"]["detail"] = request.form.get("detail")
        session.modified = True
        return redirect("/summary")
    return render_template("delivery.html")

@app.route("/summary")
def summary():
    if not login_required(): return redirect("/login")
    bouquet = session.get("bouquet")
    if not bouquet: return redirect("/flowers")

    fee = BOUQUET_SIZE[bouquet["size"]]["fee"]
    total = fee
    flower_detail = []

    # คำนวณยอดรวมที่หน้า Summary
    for fid, qty in bouquet.get("flowers", {}).items():
        flower = next((f for f in FLOWERS if f["id"] == int(fid)), None)
        if flower:
            subtotal = flower["price"] * qty
            flower_detail.append({
                "name": flower["name"],
                "qty": qty,
                "price": flower["price"],
                "subtotal": subtotal
            })
            total += subtotal # รวมราคาดอกไม้จริง

    return render_template("summary.html", 
                            bouquet=bouquet, 
                            flower_detail=flower_detail, 
                            fee=fee, 
                            total=total)
    
@app.route("/payment", methods=["GET", "POST"])
def payment():
    if not login_required(): 
        return redirect("/login")
    
    bouquet_data = session.get("bouquet")
    if not bouquet_data: 
        return redirect("/flowers")

    # 1. คำนวณราคาและเตรียมข้อมูลดอกไม้ (สำหรับโชว์ในหน้า Payment)
    flower_list = []
    total_price = BOUQUET_SIZE[bouquet_data["size"]]["fee"]
    for f_id, qty in bouquet_data["flowers"].items():
        if qty > 0:
            flower = next((f for f in FLOWERS if f["id"] == int(f_id)), None)
            if flower:
                flower_list.append(f"{flower['name']} x {qty}")
                total_price += flower["price"] * qty

    # 2. เมื่อกดยืนยันจากหน้า Payment (POST) -> ถึงจะบันทึกจริง
    if request.method == "POST":
        new_order = Bouquet(
            user_id=session["user_id"],
            size=BOUQUET_SIZE[bouquet_data["size"]]["name"],
            flowers=", ".join(flower_list),
            style=bouquet_data.get("style", "-"),
            theme=bouquet_data.get("theme", "-"),
            card=bouquet_data.get("card", "-"),
            occasion=bouquet_data.get("occasion", "-"), # บันทึกเนื่องในโอกาส
            receive_date=bouquet_data.get("receive_date"),
            receive_time=bouquet_data.get("receive_time"),
            method=bouquet_data.get("method"),
            detail=bouquet_data.get("detail", "-"),
            total_price=total_price
        )
        db.session.add(new_order)
        db.session.commit()
        
        session.pop("bouquet", None) # ล้างข้อมูลในตะกร้า
        session["success_message"] = "ชำระเงินเรียบร้อยแล้ว! ขอบคุณที่ใช้บริการค่ะ" # แจ้งเตือนจะเด้งตอนนี้
        return redirect("/history") # บันทึกเสร็จค่อยเด้งไปหน้าประวัติ

    # 3. ถ้าเพิ่งกดมาจากหน้า Summary (GET) -> ให้โชว์หน้าจ่ายเงินที่มี QR Code
    return render_template("payment.html", total=total_price)

@app.route("/history")
def history():
    if not login_required(): return redirect("/login")
    
    bouquets = Bouquet.query.filter_by(user_id=session["user_id"]).order_by(Bouquet.created_at.desc()).all()
    
    history_data = []
    for b in bouquets:
        flower_items = []
        # แยกข้อความดอกไม้ เช่น "White Rose x 2, Lily x 1"
        if b.flowers:
            parts = b.flowers.split(", ")
            for p in parts:
                if " x " in p:
                    name, qty = p.split(" x ")
                    # ค้นหารูปภาพจากลิสต์ FLOWERS หลัก
                    flower_info = next((f for f in FLOWERS if f["name"] == name.strip()), None)
                    flower_items.append({
                        "name": name.strip(),
                        "qty": qty.strip(),
                        "image": flower_info["image"] if flower_info else "images/flowers/default.png"
                    })
        
        history_data.append({
            "order": b,
            "flower_items": flower_items
        })
    
    return render_template("history.html", history_data=history_data)

# ------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)