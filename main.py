from flask import Flask, request, jsonify
import time
import hashlib
import requests

app = Flask(__name__)

@app.route('/api-sv', methods=['GET'])
def api_sv():
    # === Lấy IP thật ===
    client_ip = request.remote_addr or '127.0.0.1'

    # === Lấy time từ GET hoặc mặc định time() ===
    client_time = int(request.args.get('time', int(time.time())))

    # === Ưu tiên lấy UID từ header X-Device-UID ===
    client_uid = request.args.get('uid', '') or request.headers.get('X-Device-UID', '')

    # === Xác định thao tác ===
    thaotac = request.args.get('thaotac', '')

    if thaotac == "time":
        return jsonify({
            'server_time': int(time.time()),
            'ip': client_ip
        })

    # === SECRET chuẩn đồng bộ ===
    secret = 'HHOannGdAIIxu'

    # === Tạo RAW string ===
    raw_string = f"{secret}|{client_time}|{client_uid}|{client_ip}"

    # === Hash SHA256 và cắt 12 ký tự ===
    key_hash = hashlib.sha256(raw_string.encode()).hexdigest()
    key_short = key_hash[:12]

    # === Tạo link key gốc ===
    link = 'https://hoangdaixu.x10.bz/laykey.php?key=' + key_short

    # === Gọi YeuMoney rút gọn ===
    api_token = 'b926b7fc397affdd8de5be08b14ba3a3cf00dc6c7df19202c1e1d096a6d4264b'
    api_url = 'https://yeumoney.com/QL_api.php?token=' + api_token + '&format=json&url=' + requests.utils.quote(link)

    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code != 200:
            return jsonify({
                "raw_response": False,
                "curl_error": f"HTTP status {response.status_code}"
            })
        data = response.json()
    except Exception as e:
        return jsonify({
            "raw_response": False,
            "curl_error": str(e)
        })

    # === Xử lý kết quả ===
    if data.get('status') == 'success':
        short_link = data['shortenedUrl']
        return jsonify({
            "status": "success",
            "message": "Server Tạo link key thành công!",
            "server_time": client_time,
            "ip": client_ip,
            "uid": client_uid,
            "Admin": "Trần Đình Hoàng",
            "link": link,
            "key_link": short_link
        }, ensure_ascii=False)
    else:
        return jsonify({
            "status": "error",
            "message": "Lỗi Khi Tạo Key. Liên hệ FB: 61575008776219 hoặc Tele: @toladinhhoang",
            "detail": data.get('message', 'Không rõ lỗi')
        }, ensure_ascii=False)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
