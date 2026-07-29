from __future__ import annotations

import html as html_lib

from backend.services.jd_matching.email_service import EmailJSEmailService


class ShortlistEmailService:
    def __init__(self, email_service: EmailJSEmailService | None = None):
        self.email_service = email_service or EmailJSEmailService()

    def is_configured(self) -> bool:
        return self.email_service.is_configured()

    @property
    def last_error(self) -> str | None:
        return self.email_service.last_error

    def build_shortlisted_email(
        self,
        *,
        candidate_name: str,
        job_title: str | None = None,
    ) -> tuple[str, str, str]:
        greeting_name = candidate_name or "Candidate"
        greeting_html = html_lib.escape(greeting_name)
        role_line = (
            f" for the {job_title} role"
            if job_title
            else ""
        )
        role_html = (
            f" for the {html_lib.escape(job_title)} role"
            if job_title
            else ""
        )
        subject = "Application Update — Shortlisted"
        text = (
            f"Dear {greeting_name},\n\n"
            f"Thank you for applying{role_line}. "
            "We are pleased to let you know that you have been shortlisted "
            "for the next stage of our hiring process.\n\n"
            "Our recruiting team will contact you with next steps shortly. "
            "No further action is required from you at this time.\n\n"
            "Best regards,\n"
            "Recruiting Team"
        )
        html = (
            f"<p>Dear {greeting_html},</p>"
            f"<p>Thank you for applying{role_html}. "
            "We are pleased to let you know that you have been "
            "<strong>shortlisted</strong> for the next stage of our hiring process.</p>"
            "<p>Our recruiting team will contact you with next steps shortly. "
            "No further action is required from you at this time.</p>"
            "<p>Best regards,<br/>Recruiting Team</p>"
        )
        return subject, text, html

    def build_unshortlisted_email(
        self,
        *,
        candidate_name: str,
        feedback: str,
        job_title: str | None = None,
    ) -> tuple[str, str, str]:
        greeting_name = candidate_name or "Candidate"
        greeting_html = html_lib.escape(greeting_name)
        role_line = (
            f" for the {job_title} role"
            if job_title
            else ""
        )
        role_html = (
            f" for the {html_lib.escape(job_title)} role"
            if job_title
            else ""
        )
        subject = "Application Update"
        text = (
            f"Dear {greeting_name},\n\n"
            f"Thank you for your interest{role_line} and for taking the time to apply. "
            "After careful review, we will not be moving forward with your application "
            "at this time.\n\n"
            f"Feedback from our recruiting team:\n{feedback.strip()}\n\n"
            "We appreciate your interest and wish you success in your job search.\n\n"
            "Best regards,\n"
            "Recruiting Team"
        )
        html_body = (
            f"<p>Dear {greeting_html},</p>"
            f"<p>Thank you for your interest{role_html} and for taking the time to apply. "
            "After careful review, we will not be moving forward with your application "
            "at this time.</p>"
            "<p><strong>Feedback from our recruiting team:</strong></p>"
            f"<p>{html_lib.escape(feedback.strip())}</p>"
            "<p>We appreciate your interest and wish you success in your job search.</p>"
            "<p>Best regards,<br/>Recruiting Team</p>"
        )
        return subject, text, html_body

    async def send_shortlisted_email(
        self,
        *,
        to_email: str,
        candidate_name: str,
        job_title: str | None = None,
    ) -> bool:
        subject, text, html = self.build_shortlisted_email(
            candidate_name=candidate_name,
            job_title=job_title,
        )
        return await self.email_service.send_email(
            to_email=to_email,
            subject=subject,
            text=text,
            html=html,
        )

    async def send_unshortlisted_email(
        self,
        *,
        to_email: str,
        candidate_name: str,
        feedback: str,
        job_title: str | None = None,
    ) -> bool:
        subject, text, html = self.build_unshortlisted_email(
            candidate_name=candidate_name,
            feedback=feedback,
            job_title=job_title,
        )
        return await self.email_service.send_email(
            to_email=to_email,
            subject=subject,
            text=text,
            html=html,
        )
