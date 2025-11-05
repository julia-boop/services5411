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
creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
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

def create_summary(data_dict):
    company_name = data_dict.get("company", "Unnamed Company").strip() or "Unnamed"
    safe_title = company_name[:99]  

    existing_titles = [ws.title for ws in spreadsheet.worksheets()]
    if safe_title in existing_titles:
        spreadsheet.del_worksheet(spreadsheet.worksheet(safe_title))

    filtered_data = {
        k: v
        for k, v in data_dict.items()
        if v and (str(v).strip().lower() != "no" and str(v).strip().lower() != "")
    }
    
    new_ws = spreadsheet.add_worksheet(title=safe_title, rows=len(filtered_data) + 5, cols=3)
    new_ws.update("A1", [["Field", "Value"]])
    rows = [[key.replace("_", " ").title(), str(value)] for key, value in filtered_data.items()]
    new_ws.update("A2", rows)

    new_ws.format("A1:B1", {
        "backgroundColor": {"red": 0.04, "green": 0.26, "blue": 0.57},
        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
    })
    new_ws.format("A:B", {
        "wrapStrategy": "WRAP",
        "verticalAlignment": "TOP",
    })
    print(f"✅ Summary created for {safe_title}")

# ✅ Handle form submission
@app.route("/submit", methods=["POST"])
def submit():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data received"})

        # Append to master sheet
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data["timestamp"] = date

        # Convert dict to list of values matching header order
        headers = sheet.row_values(1)
        row_values = [data.get(h, "") for h in headers]
        sheet.append_row(row_values, value_input_option="USER_ENTERED")

        # Create a summary sheet
        create_summary(data)
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
    app.run(host="0.0.0.0", port=8080, debug=os.getenv("DEBUG", "False") == "True")

