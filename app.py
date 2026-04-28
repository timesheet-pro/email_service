import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")

def send_email(to_email, subject, body_html):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg.attach(MIMEText(body_html, "html"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())

def base_template(content):
    return f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        {content}
        <hr style="margin-top: 30px; border: none; border-top: 1px solid #eee;">
        <p style="color: #999; font-size: 12px;">
            This is an automated notification from TimesheetPro. Please do not reply to this email.
        </p>
    </div>
    """

def get_subject_and_body(type_, name, period, reason="", app_url="", manager_name="Manager"):
   
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    submitted_date = datetime.now(IST).strftime("%B %d, %Y at %I:%M %p IST")
   
    review_link = f'<a href="{app_url}" style="color:#1a73e8; font-weight:bold;">Review Timesheet →</a>' if app_url else ""
    request_link = f'<a href="{app_url}" style="color:#1a73e8; font-weight:bold;">Review Request →</a>' if app_url else ""

    templates = {

        # ── Employee submits timesheet → Manager receives this ──
        "submitted": (
            f"Timesheet Submitted – {period}",
            base_template(f"""
                <div style="background:#e8f0fe; padding:20px; border-radius:8px; border-left:4px solid #1a73e8;">
                    <h2 style="color:#1a73e8; margin:0;">📋 Timesheet Submitted</h2>
                    <p style="color:#666; font-size:13px; margin:5px 0 0 0;">Submitted on {submitted_date}</p>
                </div>
                <br>
                <p>Hi <strong>{manager_name}</strong>,</p>
                <p>This is to notify you that <strong>{name}</strong> has submitted their timesheet and requires your review.</p>
                <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd; width:40%;"><strong>Employee</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{name}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Week Period</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{period}</td>
                    </tr>
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Submitted On</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{submitted_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Status</strong></td>
                        <td style="padding:10px; border:1px solid #ddd; color:#f57c00;"><strong>⏳ Pending Review</strong></td>
                    </tr>
                </table>
                <p>✅ <strong>Action Required</strong> — Please review and approve or reject this timesheet at your earliest convenience.</p>
                <p>{review_link}</p>
            """)
        ),

        # ── Employee requests edit access → Manager receives this ──
        "edit_requested": (
            f"Edit Access Requested – {period}",
            base_template(f"""
                <div style="background:#fff8e1; padding:20px; border-radius:8px; border-left:4px solid #f9a825;">
                    <h2 style="color:#f57c00; margin:0;">✏️ Edit Access Requested</h2>
                    <p style="color:#666; font-size:13px; margin:5px 0 0 0;">Requested on {submitted_date}</p>
                </div>
                <br>
                <p>Hi <strong>{manager_name}</strong>,</p>
                <p><strong>{name}</strong> has requested permission to edit their submitted timesheet.</p>
                <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd; width:40%;"><strong>Employee</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{name}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Week Period</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{period}</td>
                    </tr>
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Requested On</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{submitted_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Reason</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{reason if reason else "No reason provided"}</td>
                    </tr>
                </table>
                <p>⚠️ <strong>Action Required</strong> — Please approve or reject this edit request.</p>
                <p>{request_link}</p>
            """)
        ),

        # ── Manager approves timesheet → Employee receives this ──
        "approved": (
            f"Timesheet Approved – {period}",
            base_template(f"""
                <div style="background:#e8f5e9; padding:20px; border-radius:8px; border-left:4px solid #2e7d32;">
                    <h2 style="color:#2e7d32; margin:0;">✅ Timesheet Approved</h2>
                    <p style="color:#666; font-size:13px; margin:5px 0 0 0;">Approved on {submitted_date}</p>
                </div>
                <br>
                <p>Hi <strong>{name}</strong>,</p>
                <p>Great news! Your timesheet has been reviewed and <strong style="color:#2e7d32;">approved</strong>.</p>
                <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd; width:40%;"><strong>Week Period</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{period}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Approved On</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{submitted_date}</td>
                    </tr>
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Status</strong></td>
                        <td style="padding:10px; border:1px solid #ddd; color:#2e7d32;"><strong>✅ Approved</strong></td>
                    </tr>
                </table>
                <p>No further action is required from your side.</p>
            """)
        ),

        # ── Manager rejects timesheet → Employee receives this ──
        "rejected": (
            f"Timesheet Rejected – {period}",
            base_template(f"""
                <div style="background:#ffebee; padding:20px; border-radius:8px; border-left:4px solid #c62828;">
                    <h2 style="color:#c62828; margin:0;">❌ Timesheet Rejected</h2>
                    <p style="color:#666; font-size:13px; margin:5px 0 0 0;">Rejected on {submitted_date}</p>
                </div>
                <br>
                <p>Hi <strong>{name}</strong>,</p>
                <p>Your timesheet for the week of <strong>{period}</strong> has been <strong style="color:#c62828;">rejected</strong> and requires your attention.</p>
                <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd; width:40%;"><strong>Week Period</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{period}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Rejected On</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{submitted_date}</td>
                    </tr>
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Reason</strong></td>
                        <td style="padding:10px; border:1px solid #ddd; color:#c62828;">{reason if reason else "No reason provided"}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Status</strong></td>
                        <td style="padding:10px; border:1px solid #ddd; color:#c62828;"><strong>❌ Rejected</strong></td>
                    </tr>
                </table>
                <p>Please review the feedback, make necessary corrections and resubmit your timesheet.</p>
            """)
        ),

        # ── Manager approves edit access → Employee receives this ──
        "edit_approved": (
            f"Edit Access Approved – {period}",
            base_template(f"""
                <div style="background:#e8f5e9; padding:20px; border-radius:8px; border-left:4px solid #2e7d32;">
                    <h2 style="color:#2e7d32; margin:0;">✅ Edit Access Approved</h2>
                    <p style="color:#666; font-size:13px; margin:5px 0 0 0;">Approved on {submitted_date}</p>
                </div>
                <br>
                <p>Hi <strong>{name}</strong>,</p>
                <p>Your request to edit your timesheet for <strong>{period}</strong> has been <strong style="color:#2e7d32;">approved</strong>.</p>
                <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd; width:40%;"><strong>Week Period</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{period}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Approved On</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{submitted_date}</td>
                    </tr>
                </table>
                <p>You can now log in and make the necessary changes to your timesheet.</p>
                <p>{review_link}</p>
            """)
        ),

        # ── Manager rejects edit access → Employee receives this ──
        "edit_rejected": (
            f"Edit Access Rejected – {period}",
            base_template(f"""
                <div style="background:#ffebee; padding:20px; border-radius:8px; border-left:4px solid #c62828;">
                    <h2 style="color:#c62828; margin:0;">❌ Edit Access Rejected</h2>
                    <p style="color:#666; font-size:13px; margin:5px 0 0 0;">Rejected on {submitted_date}</p>
                </div>
                <br>
                <p>Hi <strong>{name}</strong>,</p>
                <p>Your request to edit your timesheet for <strong>{period}</strong> has been <strong style="color:#c62828;">rejected</strong>.</p>
                <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd; width:40%;"><strong>Week Period</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{period}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Rejected On</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{submitted_date}</td>
                    </tr>
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Reason</strong></td>
                        <td style="padding:10px; border:1px solid #ddd; color:#c62828;">{reason if reason else "No reason provided"}</td>
                    </tr>
                </table>
                <p>Please contact your manager if you have any questions.</p>
            """)
        ),
    }

    return templates.get(type_)

@app.route("/send-email", methods=["POST"])
def trigger_email():
    data = request.json
    to           = data.get("to")
    type_        = data.get("type")
    name         = data.get("name", "User")
    period       = data.get("period", "")
    reason       = data.get("reason", "")
    app_url      = data.get("appUrl", "")
    manager_name = data.get("managerName", "Manager")

    result = get_subject_and_body(type_, name, period, reason, app_url, manager_name)

    if not result:
        return jsonify({"error": "Invalid email type"}), 400

    subject, body = result

    try:
        send_email(to, subject, body)
        return jsonify({"message": "Email sent!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
