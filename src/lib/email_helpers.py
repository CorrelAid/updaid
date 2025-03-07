import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from typing import List, Dict
from lib.helpers import client, infisical_project
from config import doc_link, iac_repos
from html import escape

email_pw = client.secrets.get_secret_by_name(
    secret_name="CORRELAID_GOOGLE_BOT_APP_PW",
    project_id=infisical_project,
    environment_slug="prod",
    secret_path="/",
).secretValue


def create_html_report(results):
    """
    Creates an HTML formatted version of the software update report.

    Args:
        results: List of dictionaries containing update information for each project
        iac_repos: List of dictionaries containing repository information
        doc_link: Documentation link to be included in the report

    Returns:
        str: HTML formatted report
    """
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .repo {{ margin: 20px 0; padding: 10px; background-color: #f5f5f5; }}
            .software {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ccc; }}
            .major {{ border-left-color: #ff4444; }}
            .minor {{ border-left-color: #ffbb33; }}
            .patch {{ border-left-color: #00C851; }}
            .error {{ border-left-color: #666; }}
            .repo-link {{ color: #0366d6; text-decoration: none; }}
            .repo-link:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <h2>Software Version Update Report - {datetime.now().strftime("%Y-%m-%d")}</h2>
    """

    for repo_dict in results:
        for repo, updates in repo_dict.items():
            project = next((r for r in iac_repos if r["repo"] == repo), None)
            if project:
                repo_link = f"https://github.com/{project['owner']}/{project['repo']}"
                html += f'''<div class="repo">
                    <h3>Repository: {escape(repo)} 
                    <a href="{repo_link}" class="repo-link" target="_blank">({repo_link})</a></h3>'''
            else:
                html += f'<div class="repo"><h3>Repository: {escape(repo)}</h3>'

            if not updates:
                html += "<p>No updates required.</p>"
            else:
                for update in updates:
                    update_type = update.get("update_type", "error")
                    html += f'<div class="software {update_type}">'
                    html += f"<strong>{escape(update['software'])}</strong><br>"
                    html += f"{escape(update['message'])}<br>"
                    html += "</div>"
            html += "</div>"

    html += f"""
    <p>Documentation can be found at <a href="{escape(doc_link)}" target="_blank">{escape(doc_link)}</a></p>
    </body></html>
    """

    return html


def send_email_report(results: List[Dict], recipients: List[str]) -> None:
    """
    Send email report using SMTP.

    Args:
        results: List of dictionaries containing update information
        recipients: List of email addresses to send the report to
    """
    # Email configuration
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL")

    if not all([smtp_server, smtp_port, sender_email, email_pw]):
        raise ValueError("Missing email configuration. Check environment variables.")

    # Create message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = (
        f"Action required: Software Version Update - {datetime.now().strftime('%Y-%m-%d')}"
    )
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)

    html_content = create_html_report(results)

    msg.attach(MIMEText(html_content, "html"))

    try:
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, email_pw)
            server.send_message(msg)
        print("Email report sent successfully")
    except Exception as e:
        print(f"Failed to send email report: {str(e)}")
        raise


def send_report(results: List[Dict]) -> None:
    """
    Main function to send the report.

    Args:
        results: List of dictionaries containing update information
    """
    try:
        recipients = os.getenv("REPORT_RECIPIENTS", "").split(",")
        if not recipients:
            raise ValueError(
                "No recipients configured. Set REPORT_RECIPIENTS environment variable."
            )

        send_email_report(results, recipients)
    except Exception as e:
        print(f"Error sending report: {str(e)}")
        raise
