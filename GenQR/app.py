from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import qrcode
import os
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///qrdata.db'
db = SQLAlchemy(app)

# Updated model with filename field
class QRCodeData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # Added this line

def sanitize_filename(data):
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', data)

@app.route('/download/<filename>')
def download_qr(filename):
    # Folder where QR codes are saved
    folder = os.path.join(app.root_path, 'static', 'qrcodes')
    return send_from_directory(folder, filename, as_attachment=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form['data']

        # Temporarily create entry with placeholder filename
        entry = QRCodeData(content=data, filename="placeholder.png")
        db.session.add(entry)
        db.session.commit()

        # Generate QR code
        qr = qrcode.make(data)

        # Create filename using entry.id
        safe_name = sanitize_filename(data)[:50]
        filename = f"{safe_name}_{entry.id}.png"
        folder = os.path.join('static', 'qrcodes')
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)

        # Save image
        qr.save(path)

        # Update entry with correct filename
        entry.filename = filename
        db.session.commit()

    all_data = QRCodeData.query.all()
    return render_template('index.html', data=all_data)

if __name__ == '__main__':
    app.run(debug=True, port=225)
