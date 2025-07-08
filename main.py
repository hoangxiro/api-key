from flask import Flask, request, jsonify
import hashlib
import time
import requests

app = Flask(__name__)

SECRET = "HHOannGdAIIxu"
API_TOKEN = "b926b7fc397affdd8de5be08b14ba3a3cf00dc6c7df19202c1e1d096a6d4264b"

@app.route("/api-sv", methods=["GET"])
def api_sv():
    # === Lấy IP thật ===
    client_ip = request.remote_addr or "127.0.0.1"

    # === Lấy time từ GET hoặc mặc định time() ===
    client_time = int(request.args.get("time", int(time.time())))

    # === Ưu tiên lấy UID từ header X-Device-UID ===
    client_uid = request.args.get("uid") or request.headers.get("X-Device-UID", "")

    # === Xác định thao tác ===
    thaotac = request.args.get("thaotac", "")

    if thaotac == "time":
        return jsonify({
            "server_time": int(time.time()),
            "ip": client_ip
        })

    # === Tạo RAW string ===
    raw_string = f"{SECRET}|{client_time}|{client_uid}|{client_ip}"

    # === Hash SHA256 và cắt 12 ký tự ===
    key_hash = hashlib.sha256(raw_string.encode()).hexdigest()
    key_short = key_hash[:12]

    # === Tạo link key gốc ===
    link = f"https://hoangdaixu.x10.bz/laykey.php?key={key_short}"

    # === Gọi YeuMoney rút gọn ===
    api_url = f"https://yeumoney.com/QL_api.php?token={API_TOKEN}&format=json&url={link}"

    try:
        res = requests.get(api_url, timeout=10)
        data = res.json()
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Lỗi gọi YeuMoney: {str(e)}",
            "detail": {
                "api_url_called": api_url
            }
        })

    if data.get("status") == "success":
        return jsonify({
            "status": "success",
            "message": "Server Tạo link key thành công!",
            "server_time": client_time,
            "ip": client_ip,
            "uid": client_uid,
            "Admin": "Trần Đình Hoàng",
            "key_link": data.get("shortenedUrl")
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Lỗi Khi Tạo Key. Liên hệ FB: 61575008776219 hoặc Tele: @toladinhhoang",
            "detail": {
                "api_response": data,
                "api_url_called": api_url
            }
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
