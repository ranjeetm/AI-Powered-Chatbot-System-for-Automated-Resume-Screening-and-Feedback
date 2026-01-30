# utils/email_sender.py
import os
import smtplib
from email.message import EmailMessage
import streamlit as st

def _get_smtp_config():
    """Read SMTP config from st.secrets or environment variables."""
    secrets = {}
    try:
        secrets = st.secrets.get("smtp", {}) if hasattr(st, "secrets") else {}
    except Exception:
        secrets = {}

    def _get(key, default=None):
        val = secrets.get(key) if secrets else None
        if val is None:
            val = os.environ.get(key)
        return val if val is not None else default

    return {
        "host": _get("SMTP_HOST"),
        "port": int(_get("SMTP_PORT", 587)),
        "user": _get("SMTP_USER"),
        "password": _get("SMTP_PASS"),
        "from_email": _get("FROM_EMAIL", _get("SMTP_USER")),
        "use_tls": str(_get("USE_TLS", "true")).lower() in ("true", "1", "yes"),
        "use_ssl": str(_get("USE_SSL", "false")).lower() in ("true", "1", "yes")
    }

def format_feedback_email(candidate_name, job_title, strengths, weaknesses, recommendations):
    """Build subject and body text for the feedback email."""
    subject = f"Application Received — {job_title}"
    body_lines = [
        f"Hi {candidate_name},",
        "",
        f"Thanks for applying for the position **{job_title}**.",
        "We've received your application and our AI has generated personalized feedback.",
        ""
    ]
    if strengths:
        body_lines.append("✅ Strengths:")
        body_lines += [f"  • {s}" for s in strengths] + [""]
    if weaknesses:
        body_lines.append("💡 Areas for Improvement:")
        body_lines += [f"  • {w}" for w in weaknesses] + [""]
    if recommendations:
        body_lines.append("🎯 Recommendations:")
        body_lines += [f"  • {r}" for r in recommendations] + [""]
    body_lines += [
        "Best regards,",
        "The Hiring Team",
        "",
        "---",
        "This message was generated automatically by the AI Resume Portal."
    ]
    return subject, "\n".join(body_lines)

def send_feedback_email(recipient_email, candidate_name, job_title,
                        strengths=None, weaknesses=None, recommendations=None,
                        dry_run=False):
    """Send or preview feedback email."""
    cfg = _get_smtp_config()
    required = ["host", "port", "user", "password", "from_email"]
    if not all(cfg.get(k) for k in required):
        st.warning("⚠️ SMTP not configured.")
        return False

    subject, body = format_feedback_email(candidate_name, job_title,
                                          strengths or [], weaknesses or [], recommendations or [])

    if dry_run:
        st.write("📧 **Email Preview (dry-run mode)**")
        st.write(f"**To:** {recipient_email}")
        st.write(f"**Subject:** {subject}")
        st.code(body)
        return True

    try:
        msg = EmailMessage()
        msg["From"] = cfg["from_email"]
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.set_content(body)

        if cfg["use_ssl"]:
            with smtplib.SMTP_SSL(cfg["host"], cfg["port"]) as s:
                s.login(cfg["user"], cfg["password"])
                s.send_message(msg)
        else:
            with smtplib.SMTP(cfg["host"], cfg["port"], timeout=20) as s:
                if cfg["use_tls"]:
                    s.starttls()
                s.login(cfg["user"], cfg["password"])
                s.send_message(msg)
        return True
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")
        return False
