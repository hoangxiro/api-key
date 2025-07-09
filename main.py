from flask import Flask, request, jsonify
import hashlib
import time
import requests

app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
    # === Đặt timezone, nhưng Python không set system timezone như PHP ===
    # Sử dụng time.localtime() sẽ tự lấy theo OS
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
            "server_time": int(time.time()),
            "ip": client_ip
        })

    # === SECRET chuẩn đồng bộ ===
    secret = 'HHOannGdAIIxu'

    # === Tạo RAW string ===
    raw_string = f"{secret}|{client_time}|{client_uid}|{client_ip}"

    # === Hash SHA256 và cắt 12 ký tự ===
    key_hash = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()
    key_short = key_hash[:12]

    # === Tạo link key gốc ===
    link = f'https://hoangdaixu.x10.bz/laykey.php?key={key_short}'

    # === Gọi YeuMoney rút gọn ===
    api_token = 'b926b7fc397affdd8de5be08b14ba3a3cf00dc6c7df19202c1e1d096a6d4264b'
    api_url = f'https://yeumoney.com/QL_api.php?token={api_token}&format=json&url={requests.utils.quote(link)}'

    try:
        response = requests.get(api_url, timeout=10)
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
        })
    else:
        return jsonify({
            "status": "error",
            "message": "Lỗi Khi Tạo Key. Liên hệ FB: 61575008776219 hoặc Tele: @toladinhhoang",
            "detail": data.get('message', 'Không rõ lỗi')
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
