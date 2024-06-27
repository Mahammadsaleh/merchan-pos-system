from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
import base64
from cryptography.fernet import Fernet
from datetime import datetime
import qrcode
import io
from PIL import Image
from pyzbar.pyzbar import decode

app = Flask(__name__)

# Secret key for Fernet encryption (this should be securely generated and stored)
SECRET_KEY = Fernet.generate_key()
f = Fernet(SECRET_KEY)
print(SECRET_KEY)

# Simulated user database
users = {
    'user1': {'balance': 100},
    'user2': {'balance': 150},
}

def encrypt_data(data):
    return f.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data):
    try:
        return f.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

@app.route('/')
def index():
    user_id = 'user1'  # For demonstration, we use 'user1'
    balance = users[user_id]['balance']
    return render_template('index.html', user_id=user_id, balance=balance)

@app.route('/generate_qr/<user_id>', methods=['GET'])
def generate_qr(user_id):
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    data = f"{user_id},{current_time}"
    print(f"Data to be encrypted: {data}")
    encrypted_data = encrypt_data(data)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(encrypted_data)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    buffer.seek(0)
    
    return send_file(buffer, mimetype='image/png', as_attachment=True, download_name='qr_code.png')
#server side hadnle the if qr code is valid or not
@app.route('/process_qr', methods=['POST'])
def process_qr():
    try:
        data = request.json['qr_data']
        decrypted_data = decrypt_data(data)
        if decrypted_data:
            user_id, user_payment_time = decrypted_data.split(',')
            server_currrent_time = datetime.now().strftime("%Y%m%d%H%M%S")
            if int(server_currrent_time) - int(user_payment_time) > 20:
                return jsonify({'status': 'invalid qr'})
            if user_id in users:
                users[user_id]['balance'] -= 10  # Subtract a fixed amount for demonstration
                return jsonify({'uid': user_id, 'status': 'valid', 'balance': users[user_id]['balance'], 'time_left': 30 - (int(server_currrent_time) - int(user_payment_time))})
            else:
                return jsonify({'status': 'invalid user'})
        else:
            return jsonify({'status': 'invalid qr'})
    except Exception as e:
        print(f"Error processing QR code: {e}")
        return jsonify({'error': 'Failed to process QR code'}), 500

@app.route('/upload_qr', methods=['POST'])
def upload_qr():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        img = Image.open(file)
        decoded_objects = decode(img)
        print(f"Decoded objects: {decoded_objects}")
        if decoded_objects:
            qr_data = decoded_objects[0].data.decode('utf-8')
            print(f"Decoded QR data: {qr_data}")
            return jsonify({'qr_data': qr_data})
        else:
            return jsonify({'error': 'Failed to decode QR code'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
