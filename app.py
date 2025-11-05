from flask import Flask, request, jsonify, send_from_directory
import gspread
from google.oauth2.service_account import Credentials
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
from datetime import datetime
from gspread.utils import rowcol_to_a1, a1_range_to_grid_range
import json


load_dotenv()

app = Flask(__name__, static_folder=".", static_url_path="")

# Load environment variables
SHEET_ID = os.getenv("SHEET_ID")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# --- Google Sheets setup ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
service_account_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
creds = Credentials.from_service_account_file(service_account_info, scopes=SCOPES)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SHEET_ID)
sheet = spreadsheet.worksheet("Form Data")  

# ✅ Serve your index.html
@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

def next_available_row_by_column(sheet, col_index=2):  # column B = 2
    col_values = sheet.col_values(col_index)
    return len(col_values) + 1

# ✅ Handle form submission
@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    print("Received data:", data)

    # Normalize headers
    headers = [h.strip() for h in sheet.row_values(1)]
    new_row = [data.get(col.strip(), "") for col in headers]
    print("Row to append:", new_row)
    print(headers)

    try:
        next_row = next_available_row_by_column(sheet, 2)
        col_count = len(headers)
        start_cell = rowcol_to_a1(next_row, 1)  # Start from column B
        end_cell = rowcol_to_a1(next_row, col_count + 1)
        range_to_update = f"{start_cell}:{end_cell}"

        sheet.update(range_to_update, [new_row])
        print(f"✅ Row written directly to row {next_row} ({range_to_update})")
    except Exception as e:
        print("❌ Google Sheets error:", e)
        return jsonify({"status": "error", "message": str(e)})

    # Send email notification
    brand = data.get("company", "Unknown Brand")
    msg = MIMEText(f"A new service form was submitted by: {brand}")
    msg["Subject"] = f"New Service Request — {brand}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASS)
            server.send_message(msg)
            print("📧 Email notification sent successfully.")
    except Exception as e:
        print("Email error:", e)

    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(debug=True)

