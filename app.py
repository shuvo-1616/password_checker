from flask import Flask, render_template, request, jsonify
from core import CoreChecker
from fuzzy import FuzzyChecker
from context import ContextDB
from predictive import Predictive
import os

app = Flask(__name__)
core = CoreChecker()

LEAKED_SAMPLE = [
    "password", "123456", "qwerty", "letmein", "Password123", "admin", "welcome"
]
fuzzy = FuzzyChecker(leaked_list=LEAKED_SAMPLE)
ctx = ContextDB()
pred = Predictive()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    conn = ctx.conn
    cur = conn.cursor()
    cur.execute("SELECT user_id, COUNT(*) as count FROM user_passwords GROUP BY user_id ORDER BY count DESC")
    users = cur.fetchall()
    return render_template("admin.html", users=users)

@app.route("/api/check", methods=["POST"])
def api_check():
    data = request.json or {}
    password = data.get("password", "")
    user_id = data.get("user_id")
    if not password:
        return jsonify({"error": "password_required"}), 400

    strength = core.check_strength(password)
    hibp = core.hibp_pwned_check(password)
    fuzzy_res = fuzzy.find_similar(password, threshold=2, max_checks=1000)
    reuse = None
    mfa = None
    if user_id:
        reuse_flag = ctx.has_reuse(user_id, password)
        reuse = {"reused": reuse_flag}
        mfa_flag = ctx.get_mfa(user_id)
        mfa = {"mfa_enabled": mfa_flag}
    predictive = pred.estimate(password)

    out = {
        "strength": strength,
        "pwned": hibp,
        "fuzzy": fuzzy_res,
        "context": {"reuse": reuse, "mfa": mfa},
        "predictive": predictive
    }
    return jsonify(out), 200

@app.route("/api/store_password", methods=["POST"])
def api_store_password():
    data = request.json or {}
    user_id = data.get("user_id")
    password = data.get("password")
    if not user_id or not password:
        return jsonify({"error": "user_id_and_password_required"}), 400
    ctx.store_password(user_id, password)
    return jsonify({"status": "stored"}), 200

@app.route("/api/set_mfa", methods=["POST"])
def api_set_mfa():
    data = request.json or {}
    user_id = data.get("user_id")
    enabled = data.get("enabled", False)
    if not user_id:
        return jsonify({"error": "user_id_required"}), 400
    ctx.set_mfa(user_id, bool(enabled))
    return jsonify({"status": "ok", "mfa_enabled": bool(enabled)}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)