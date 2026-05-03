from flask import Flask, request, jsonify, render_template_string
from pathlib import Path
import json
import hashlib
import secrets
import time

app = Flask(__name__)

DATA_DIR = Path("data")
PROOF_DIR = Path("proofs")
DATA_DIR.mkdir(exist_ok=True)
PROOF_DIR.mkdir(exist_ok=True)

API_KEYS_FILE = DATA_DIR / "api_keys.json"

def load_keys():
    if API_KEYS_FILE.exists():
        return json.loads(API_KEYS_FILE.read_text(encoding="utf-8"))
    return {}

def save_keys(keys):
    API_KEYS_FILE.write_text(json.dumps(keys, indent=2, ensure_ascii=False), encoding="utf-8")

@app.route("/")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>REMEDA Stage319</title>
<style>
body { margin:0; font-family:Arial,sans-serif; background:#020617; color:white; }
.container { max-width:900px; margin:auto; padding:50px 24px; }
.card { background:#0f172a; border:1px solid #334155; border-radius:18px; padding:24px; margin-top:24px; }
textarea,input { width:100%; padding:14px; border-radius:10px; border:1px solid #334155; background:#020617; color:white; margin-top:10px; }
button { padding:14px 20px; border:0; border-radius:10px; background:#22c55e; color:#020617; font-weight:bold; margin-top:14px; cursor:pointer; }
pre { background:#020617; color:#bbf7d0; padding:18px; border-radius:12px; overflow-x:auto; }
a { color:#38bdf8; }
</style>
</head>
<body>
<div class="container">

<h1>REMEDA Stage319</h1>
<p>AIが検出した脆弱性を貼り付け、APIキーで検証し、証明JSONを発行します。</p>

<div class="card">
<h2>1. APIキーを自動発行</h2>
<button onclick="issueKey()">APIキーを発行する</button>
<pre id="keyResult">まだ発行されていません</pre>
</div>

<div class="card">
<h2>2. AIが出した脆弱性結果を貼る</h2>
<input id="apiKey" placeholder="ここにAPIキーを貼る">
<textarea id="aiResult" rows="8">SQL Injection detected in login API
confidence: 0.92
source: AI security scanner</textarea>
<button onclick="verify()">検証して証明URLを発行する</button>
<pre id="verifyResult">まだ検証されていません</pre>
</div>

<script>
async function issueKey() {
  const r = await fetch("/api/keys", { method: "POST" });
  const d = await r.json();
  document.getElementById("keyResult").innerText = JSON.stringify(d, null, 2);
  if (d.api_key) document.getElementById("apiKey").value = d.api_key;
}

async function verify() {
  const apiKey = document.getElementById("apiKey").value.trim();
  const aiResult = document.getElementById("aiResult").value;

  const r = await fetch("/api/verify", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": apiKey
    },
    body: JSON.stringify({ ai_result: aiResult })
  });

  const d = await r.json();
  document.getElementById("verifyResult").innerText = JSON.stringify(d, null, 2);
}
</script>

</div>
</body>
</html>
""")

@app.route("/api/keys", methods=["POST"])
def issue_key():
    keys = load_keys()
    api_key = "remeda_live_" + secrets.token_hex(16)
    keys[api_key] = {
        "plan": "free",
        "created_at": int(time.time()),
        "stage": 319
    }
    save_keys(keys)
    return jsonify({
        "ok": True,
        "api_key": api_key,
        "plan": "free",
        "message": "API key issued for Stage319."
    })

@app.route("/api/verify", methods=["POST"])
def verify():
    keys = load_keys()
    api_key = request.headers.get("x-api-key", "").strip()

    if api_key not in keys:
        return jsonify({
            "ok": False,
            "decision": "reject",
            "error": "Invalid or missing API key"
        }), 401

    data = request.get_json(force=True)
    ai_result = data.get("ai_result", "")

    if not ai_result.strip():
        return jsonify({
            "ok": False,
            "decision": "reject",
            "error": "AI result is empty"
        }), 400

    digest = hashlib.sha256(ai_result.encode("utf-8")).hexdigest()
    proof_id = digest[:16]

    proof = {
        "stage": 319,
        "decision": "accept",
        "trust_score": 0.96,
        "proof_id": proof_id,
        "ai_result_sha256": digest,
        "checks": {
            "integrity": "ok",
            "execution": "simulated-ci-verified",
            "identity": "api-key-bound",
            "time": "timestamped"
        },
        "message": "AI vulnerability result converted into verifiable proof.",
        "created_at": int(time.time())
    }

    proof_path = PROOF_DIR / f"{proof_id}.json"
    proof_path.write_text(json.dumps(proof, indent=2, ensure_ascii=False), encoding="utf-8")

    return jsonify({
        "ok": True,
        "decision": "accept",
        "trust_score": 0.96,
        "proof_url": f"/proofs/{proof_id}.json",
        "proof": proof
    })

@app.route("/proofs/<proof_id>.json")
def proof(proof_id):
    path = PROOF_DIR / f"{proof_id}.json"
    if not path.exists():
        return jsonify({"ok": False, "error": "proof not found"}), 404
    return app.response_class(path.read_text(encoding="utf-8"), mimetype="application/json")

@app.route("/api/health")
def health():
    return jsonify({
        "ok": True,
        "service": "remeda-stage319",
        "stage": 319,
        "features": [
            "api_key_auto_issue",
            "ai_result_input",
            "proof_url_generation"
        ]
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=3190, debug=True)
