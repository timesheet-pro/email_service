import os
from datetime import datetime, timezone, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)
CORS(app, origins="*")

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDER_EMAIL = os.environ.get("GMAIL_USER")

def send_email(to_email, subject, body_html):
    message = Mail(
        from_email=SENDER_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=body_html
    )
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    sg.send(message)

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

def get_subject_and_body(type_, name, period, reason="", app_url="", manager_name="Manager", timesheet_date=""):
    IST = timezone(timedelta(hours=5, minutes=30))
    action_date = datetime.now(IST).strftime("%B %d, %Y at %I:%M %p IST")

    # fallback to period if timesheetDate not passed
    ts_date = timesheet_date if timesheet_date else period

    review_link = f'<a href="{app_url}" style="color:#1a73e8; font-weight:bold;">Review Timesheet →</a>' if app_url else ""

    templates = {

        "submitted": (
            f"Timesheet Submitted – {period}",
            base_template(f"""
                <div style="background:#e8f0fe; padding:20px; border-radius:8px; border-left:4px solid #1a73e8;">
                    <h2 style="color:#1a73e8; margin:0;">📋 Timesheet Submitted</h2>
                    <p style="color:#666; font-size:13px; margin:5px 0 0 0;">Submitted on {action_date}</p>
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
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Submitted For</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{ts_date}</td>
                    </tr>
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Timesheet Submitted On</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{action_date}</td>
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

        "edit_requested": (
            f"Edit Access Requested – {period}",
            base_template(f"""
                <div style="background:#fff8e1; padding:20px; border-radius:8px; border-left:4px solid #f9a825;">
                    <h2 style="color:#f57c00; margin:0;">✏️ Edit Access Requested</h2>
                    <p style="color:#666; font-size:13px; margin:5px 0 0 0;">Requested on {action_date}</p>
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
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Edit Requested For</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{ts_date}</td>
                    </tr>
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Edit Access Requested On</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{action_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Reason</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{reason if reason else "No reason provided"}</td>
                    </tr>
                </table>
                <p>⚠️ <strong>Action Required</strong> — Please approve or reject this edit request.</p>
            """)
        ),

        "approved": (
            f"Timesheet Approved – {period}",
            base_template(f"""
                <div style="background:#e8f5e9; padding:20px; border-radius:8px; border-left:4px solid #2e7d32;">
                    <h2 style="color:#2e7d32; margin:0;">✅ Timesheet Approved</h2>
                    <p style="color:#666; font-size:13px; margin:5px 0 0 0;">Approved on {action_date}</p>
                </div>
                <br>
                <p>Hi <strong>{name}</strong>,</p>
                <p>Great news! Your timesheet has been reviewed and <strong style="color:#2e7d32;">approved</strong>.</p>
                <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd; width:40%;"><strong>Approved For</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{ts_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Timesheet Approved On</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{action_date}</td>
                    </tr>
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Status</strong></td>
                        <td style="padding:10px; border:1px solid #ddd; color:#2e7d32;"><strong>✅ Approved</strong></td>
                    </tr>
                </table>
                <p>No further action is required from your side.</p>
            """)
        ),

        "rejected": (
            f"Timesheet Rejected – {period}",
            base_template(f"""
                <div style="background:#ffebee; padding:20px; border-radius:8px; border-left:4px solid #c62828;">
                    <h2 style="color:#c62828; margin:0;">❌ Timesheet Rejected</h2>
                    <p style="color:#666; font-size:13px; margin:5px 0 0 0;">Rejected on {action_date}</p>
                </div>
                <br>
                <p>Hi <strong>{name}</strong>,</p>
                <p>Your timesheet for <strong>{ts_date}</strong> has been <strong style="color:#c62828;">rejected</strong> and requires your attention.</p>
                <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd; width:40%;"><strong>Rejected For</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{ts_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Timesheet Rejected On</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{action_date}</td>
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

        "edit_approved": (
            f"Edit Access Approved – {period}",
            base_template(f"""
                <div style="background:#e8f5e9; padding:20px; border-radius:8px; border-left:4px solid #2e7d32;">
                    <h2 style="color:#2e7d32; margin:0;">✅ Edit Access Approved</h2>
                    <p style="color:#666; font-size:13px; margin:5px 0 0 0;">Approved on {action_date}</p>
                </div>
                <br>
                <p>Hi <strong>{name}</strong>,</p>
                <p>Your request to edit your timesheet for <strong>{ts_date}</strong> has been <strong style="color:#2e7d32;">approved</strong>.</p>
                <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd; width:40%;"><strong>Edit Approved For</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{ts_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Edit Access Approved On</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{action_date}</td>
                    </tr>
                </table>
                <p>You can now log in and make the necessary changes to your timesheet.</p>
            """)
        ),

        "edit_rejected": (
            f"Edit Access Rejected – {period}",
            base_template(f"""
                <div style="background:#ffebee; padding:20px; border-radius:8px; border-left:4px solid #c62828;">
                    <h2 style="color:#c62828; margin:0;">❌ Edit Access Rejected</h2>
                    <p style="color:#666; font-size:13px; margin:5px 0 0 0;">Rejected on {action_date}</p>
                </div>
                <br>
                <p>Hi <strong>{name}</strong>,</p>
                <p>Your request to edit your timesheet for <strong>{ts_date}</strong> has been <strong style="color:#c62828;">rejected</strong>.</p>
                <table style="width:100%; border-collapse:collapse; margin:20px 0;">
                    <tr style="background:#f1f3f4;">
                        <td style="padding:10px; border:1px solid #ddd; width:40%;"><strong>Edit Rejected For</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{ts_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:10px; border:1px solid #ddd;"><strong>Edit Access Rejected On</strong></td>
                        <td style="padding:10px; border:1px solid #ddd;">{action_date}</td>
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
    data         = request.json
    to           = data.get("to")
    type_        = data.get("type")
    name         = data.get("name", "User")
    period       = data.get("period", "")
    reason       = data.get("reason", "")
    app_url      = data.get("appUrl", "")
    manager_name = data.get("managerName", "Manager")
    timesheet_date = data.get("timesheetDate", "")

    result = get_subject_and_body(type_, name, period, reason, app_url, manager_name, timesheet_date)

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
