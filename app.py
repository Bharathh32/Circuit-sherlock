import os
import base64
from datetime import timedelta, datetime
from functools import wraps
from firebase_admin import firestore

from flask import Flask, render_template, request, redirect, jsonify, make_response
from flask_mail import Mail, Message
from ultralytics import YOLO
from PIL import Image
import pandas as pd
import cv2
import numpy as np
import razorpay
import firebase_admin
from firebase_admin import auth, credentials

# ---------------------------
# FLASK APP CONFIG
# ---------------------------
app = Flask(__name__)

# ---------------------------
# MAIL CONFIG
# ---------------------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "suryachekuri119@gmail.com"
app.config['MAIL_PASSWORD'] = "hqre liec qyye fxlf"
mail = Mail(app)

# ---------------------------
# UPLOAD / RESULT PATHS
# ---------------------------
UPLOAD_FOLDER = "static/uploads"
RESULT_FOLDER = "static/results"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["RESULT_FOLDER"] = RESULT_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# ---------------------------
# YOLO MODEL + DATA
# ---------------------------
model = YOLO("model/best.pt")
spares_df = pd.read_csv("spares.csv")
spares_dict = {row['defect']: {"part": row['spare_part'], "cost": int(row['cost'])} 
               for _, row in spares_df.iterrows()}
repair_suggestions = {
    "missing_hole": "Re-drill the hole or adjust drilling machine alignment.",
    "spurious_copper": "Remove extra copper using micro-etch or PCB scraping tool.",
    "short": "Remove solder short using soldering iron and flux.",
    "open_circuit": "Repair trace using conductive ink or jumper wire.",
    "mouse_bite": "Clean edges or use solder mask to cover exposed pads."
}

# ---------------------------
# FIREBASE ADMIN
# ---------------------------
# ---------------------------
# FIREBASE ADMIN
# ---------------------------
# ---------------------------
# FIREBASE ADMIN
# ---------------------------
ADMIN_EMAIL = "circuitadmin@gmail.com"
FIREBASE_SA_PATH = "serviceAccountKey.json"

if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_SA_PATH)
    firebase_admin.initialize_app(cred)

from firebase_admin import firestore
db = firestore.client()


# ---------------------------
# RAZORPAY CONFIG
# ---------------------------
RAZORPAY_KEY = "rzp_test_RqbpmOK64UzDJb"
RAZORPAY_SECRET = "4EKfvX23208vLgiwksguUnD5"
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY, RAZORPAY_SECRET))

def verify_signature(order_id, payment_id, signature, secret):
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
        return True
    except:
        return False

# ---------------------------
# JINJA FILTER
# ---------------------------
@app.template_filter("readable_date")
def readable_date(timestamp):
    if not timestamp:
        return "Not available"
    ts = int(timestamp)
    if ts > 1_000_000_000_000:
        ts //= 1000
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S UTC')

# ---------------------------
# SESSION HELPERS
# ---------------------------
def verify_session_cookie():
    cookie = request.cookies.get("session")
    if not cookie:
        return None
    try:
        decoded = auth.verify_session_cookie(cookie, check_revoked=True)
        uid = decoded.get("uid")
        email = decoded.get("email")
        user_record = auth.get_user(uid)
        claims = user_record.custom_claims or {}
        return {
            "email": email,
            "uid": uid,
            "admin": claims.get("admin", False) or email == ADMIN_EMAIL,
            "created": user_record.user_metadata.creation_timestamp,
            "last_login": user_record.user_metadata.last_sign_in_timestamp
        }
    except Exception:
        return None

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not verify_session_cookie():
            return redirect("/auth")
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = verify_session_cookie()
        if not user or not user["admin"]:
            return "Admins only", 403
        return f(*args, **kwargs)
    return wrapper

# ---------------------------
# PUBLIC ROUTES
# ---------------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/ai")
@login_required   # remove this line if you want it public
def ai_index():
    return render_template("index.html")

@app.route("/history")
@login_required
def history():
    return render_template("user_history.html")

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=verify_session_cookie())

@app.route("/live")
@login_required
def live():
    return render_template("live.html")

@app.route("/auth")
def auth_page():
    return render_template("login_signup.html")

@app.context_processor
def inject_user():
    return dict(user=verify_session_cookie())




# ---------------------------
# SESSION LOGIN / LOGOUT
# ---------------------------
@app.route("/sessionLogin", methods=["POST"])
def sessionLogin():
    id_token = request.json.get("idToken")
    expires_in = timedelta(days=5)
    decoded = auth.verify_id_token(id_token)
    uid = decoded["uid"]
    email = decoded.get("email")
    if email == ADMIN_EMAIL:
        auth.set_custom_user_claims(uid, {"admin": True})
    session_cookie = auth.create_session_cookie(id_token, expires_in=expires_in)
    resp = make_response({"status": "success"})
    resp.set_cookie("session", session_cookie, max_age=int(expires_in.total_seconds()), httponly=True)
    return resp

@app.route("/sessionLogout", methods=["POST"])
def sessionLogout():
    resp = make_response(redirect("/"))
    resp.set_cookie("session", "", expires=0)
    return resp

# ---------------------------
# ADMIN ROUTES
# ---------------------------
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    total_users = 0
    admin_users = 0
    normal_users = 0

    for user in auth.list_users().iterate_all():
        total_users += 1
        if (user.custom_claims or {}).get("admin"):
            admin_users += 1
        else:
            normal_users += 1

    return render_template(
        "admin_dashboard.html",
        total_users=total_users,
        admin_users=admin_users,
        normal_users=normal_users
    )


@app.route("/admin/users")
@admin_required
def admin_users():
    users = []
    for u in auth.list_users().iterate_all():
        users.append({
            "uid": u.uid,
            "email": u.email,
            "admin": (u.custom_claims or {}).get("admin", False),
            "created": u.user_metadata.creation_timestamp,
            "last_login": u.user_metadata.last_sign_in_timestamp
        })
    return render_template("admin_users.html", users=users)

@app.route("/admin/profile")
@admin_required
def admin_profile():
    user = verify_session_cookie()
    return render_template("admin_profile.html", user=user)

@app.route("/admin/user/<uid>")
@admin_required
def admin_user_detail(uid):
    try:
        user_record = auth.get_user(uid)
    except:
        return "User not found", 404

    user_data = {
        "uid": user_record.uid,
        "email": user_record.email,
        "admin": (user_record.custom_claims or {}).get("admin", False),
        "created": user_record.user_metadata.creation_timestamp,
        "last_login": user_record.user_metadata.last_sign_in_timestamp,
        "name": user_record.display_name
    }

    return render_template("admin_user_details.html", user=user_data)

@app.route("/admin/payments")
@admin_required
def admin_payments():
    payments_ref = db.collection("payments").order_by(
        "timestamp", direction=firestore.Query.DESCENDING
    )

    payments = []
    for p in payments_ref.stream():
        payments.append(p.to_dict())

    return render_template("admin_payments.html", payments=payments)

# ---------------------------
# CONTACT FORM
# ---------------------------
@app.route("/send_message", methods=["POST"])
def send_message():
    msg = Message(
        subject="New Contact Message",
        sender=app.config['MAIL_USERNAME'],
        recipients=[app.config['MAIL_USERNAME']],
        body=f"Name: {request.form.get('name')}\nEmail: {request.form.get('email')}\nMobile: {request.form.get('mobile')}\n\nMessage:\n{request.form.get('message')}"
    )
    mail.send(msg)
    return render_template("contact.html", success=True)

# ---------------------------
# YOLO LIVE
# ---------------------------
@app.route("/process_frame", methods=["POST"])
def process_frame():
    image_bytes = base64.b64decode(request.form["frame"].split(",")[1])
    frame = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    results = model.predict(frame, imgsz=640, conf=0.3)
    annotated = results[0].plot()
    _, buffer = cv2.imencode(".jpg", annotated)
    encoded = base64.b64encode(buffer).decode()
    defects = list({model.names[int(box.cls[0])] for r in results for box in r.boxes})
    return jsonify({"frame": f"data:image/jpeg;base64,{encoded}", "defects": defects})

# ---------------------------
# IMAGE UPLOAD / DETECTION
# ---------------------------
# @app.route("/upload", methods=["POST"])
# def upload():
#     file = request.files["image"]
#     path = os.path.join(UPLOAD_FOLDER, file.filename)
#     file.save(path)
#     result, defects, repair_info, total = run_detection(path)
#     return render_template("result.html", result_image=result, defects=defects, repair_info=repair_info, total_cost=total)

def run_detection(image_path):
    results = model.predict(image_path, save=True)
    output = "result_" + os.path.basename(image_path)
    Image.open(results[0].save_dir + "/" + os.listdir(results[0].save_dir)[0]).save(f"{RESULT_FOLDER}/{output}")
    detected = {model.names[int(box.cls[0])] for r in results for box in r.boxes} or {"No defects"}
    repair_info, total = {}, 0
    for d in detected:
        part = spares_dict.get(d, {})
        total += part.get("cost", 0)
        repair_info[d] = {"suggestion": repair_suggestions.get(d, "N/A"), "part": part.get("part", "N/A"), "cost": part.get("cost", 0)}
    return output, list(detected), repair_info, total

# ---------------------------
# PAYMENT ROUTES
# ---------------------------
@app.route("/payment")
@login_required
def payment_page():
    user = verify_session_cookie()
    print("PAYMENT PAGE UID:", user["uid"])  # DEBUG

    return render_template(
        "payment.html",
        razorpay_key=RAZORPAY_KEY,
        user_uid=user["uid"]
    )



@app.route("/create_order", methods=["POST"])
def create_order():
    data = request.get_json()
    amount = int(data["amount"]) * 100
    order = razorpay_client.order.create({"amount": amount, "currency": "INR", "payment_capture": "1"})
    return jsonify(order)

# @app.route("/verify_payment", methods=["POST"])
# def verify_payment_route():
#     payment_id = request.form.get("razorpay_payment_id")
#     order_id = request.form.get("razorpay_order_id")
#     signature = request.form.get("razorpay_signature")
#     if verify_signature(order_id, payment_id, signature, RAZORPAY_SECRET):
#         return f"Payment Successful! Payment ID: {payment_id}"
#     else:
#         return "Payment Verification Failed", 400

# @app.route("/verify_payment", methods=["POST"])
# def verify_payment_route():

#     payment_id = request.form.get("razorpay_payment_id")
#     order_id = request.form.get("razorpay_order_id")
#     signature = request.form.get("razorpay_signature")
#     user_id = request.form.get("user_id")
#     amount = request.form.get("amount")

#     if not user_id:
#         return "User ID missing", 400

#     if verify_signature(order_id, payment_id, signature, RAZORPAY_SECRET):

#         db.collection("users").document(user_id).set({
#             "is_subscribed": True,
#             "plan": "premium",
#             "ai_uses": 0,
#             "updatedAt": firestore.SERVER_TIMESTAMP
#         }, merge=True)

#         return redirect("/live")

@app.route("/verify_payment", methods=["POST"])
def verify_payment_route():

    payment_id = request.form.get("razorpay_payment_id")
    user_id = request.form.get("user_id")
    amount = request.form.get("amount")

    if not user_id or not payment_id or not amount:
        return "Invalid payment data", 400

    amount = int(amount)

    # ---------------------------
    # PLAN & EXPIRY LOGIC
    # ---------------------------
    if amount == 59:
        plan_name = "1_week"
        expiry_days = 7
    elif amount == 99:
        plan_name = "1_month"
        expiry_days = 30
    elif amount == 249:
        plan_name = "3_months"
        expiry_days = 90
    else:
        plan_name = "custom"
        expiry_days = 7

    expiry_date = datetime.utcnow() + timedelta(days=expiry_days)

    # ---------------------------
    # UPDATE USER SUBSCRIPTION
    # ---------------------------
    db.collection("users").document(user_id).set({
        "is_subscribed": True,
        "plan": plan_name,
        "subscription_start": firestore.SERVER_TIMESTAMP,
        "subscription_end": expiry_date,
        "ai_uses": 0,
        "updatedAt": firestore.SERVER_TIMESTAMP,
        "razorpay_payment_id": payment_id
    }, merge=True)

    # ---------------------------
    # STORE PAYMENT HISTORY (ADMIN)
    # ---------------------------
    user_doc = db.collection("users").document(user_id).get()
    email = user_doc.to_dict().get("email") if user_doc.exists else "unknown"

    db.collection("payments").add({
        "user_id": user_id,
        "email": email,
        "amount": amount,
        "plan": plan_name,
        "razorpay_payment_id": payment_id,
        "status": "success",
        "timestamp": firestore.SERVER_TIMESTAMP
    })

    return redirect("/ai")



@app.route("/payment_success")
def payment_success():
    return render_template("payment_success.html")



@app.route("/upload", methods=["POST"])
@login_required
def upload():
    user = verify_session_cookie()
    uid = user["uid"]

    file = request.files["image"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    result, defects, repair_info, total = run_detection(path)

    # 🔥 SAVE HISTORY (FIX)
    db.collection("users").document(uid).set({
        "email": user["email"],
        "updatedAt": firestore.SERVER_TIMESTAMP
    }, merge=True)

    db.collection("users").document(uid).collection("history").add({
        "defects": defects,
        "total_cost": total,
        "result_image": result,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

    return render_template(
        "result.html",
        result_image=result,
        defects=defects,
        repair_info=repair_info,
        total_cost=total
    )
# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)
