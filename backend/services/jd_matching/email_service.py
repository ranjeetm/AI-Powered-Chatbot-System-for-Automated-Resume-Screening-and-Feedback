from __future__ import annotations

import os
import html
import logging
from pathlib import Path
from typing import Any

import httpx
from dotenv import dotenv_values, load_dotenv


load_dotenv()

logger = logging.getLogger(__name__)

BACKEND_ENV = dotenv_values(Path(__file__).resolve().parents[2] / ".env")
ROOT_ENV = dotenv_values(Path(__file__).resolve().parents[3] / ".env")


def _get_setting(name: str, default: str | None = None) -> str | None:
    return (
        os.getenv(name)
        or BACKEND_ENV.get(name)
        or ROOT_ENV.get(name)
        or default
    )


class EmailJSEmailService:
    def __init__(self):
        self.service_id = _get_setting("EMAILJS_SERVICE_ID")
        self.template_id = _get_setting("EMAILJS_TEMPLATE_ID")
        self.public_key = _get_setting("EMAILJS_PUBLIC_KEY")
        self.private_key = _get_setting("EMAILJS_PRIVATE_KEY")
        self.base_url = _get_setting(
            "EMAILJS_API_URL",
            "https://api.emailjs.com/api/v1.0/email/send",
        )
        self.timeout = float(_get_setting("EMAILJS_TIMEOUT_SECONDS", "5"))
        self.last_error: str | None = None

    def is_configured(self) -> bool:
        return bool(
            self.service_id
            and self.template_id
            and self.public_key
        )

    async def send_email(
        self,
        *,
        to_email: str,
        subject: str,
        text: str,
        html: str | None = None,
    ) -> bool:
        self.last_error = None

        if not self.is_configured():
            self.last_error = (
                "EmailJS is missing EMAILJS_SERVICE_ID, "
                "EMAILJS_TEMPLATE_ID, or EMAILJS_PUBLIC_KEY."
            )
            return False

        payload = {
            "service_id": self.service_id,
            "template_id": self.template_id,
            "user_id": self.public_key,
            "template_params": {
                "to_email": to_email,
                "email": to_email,
                "recipient_email": to_email,
                "subject": subject,
                "message": text,
                "text_message": text,
                "html_message": html or text,
            },
        }

        if self.private_key:
            payload["accessToken"] = self.private_key

        headers = {
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                return True
        except httpx.HTTPStatusError as exc:
            response_text = exc.response.text.strip()
            self.last_error = (
                f"EmailJS returned HTTP {exc.response.status_code}: "
                f"{response_text or exc.response.reason_phrase}"
            )
            logger.warning(self.last_error)
            return False
        except httpx.RequestError as exc:
            self.last_error = f"EmailJS request failed: {exc}"
            logger.warning(self.last_error)
            return False
        except Exception:
            self.last_error = "EmailJS delivery failed unexpectedly."
            logger.exception(self.last_error)
            return False

    def build_recruiter_summary(
        self,
        *,
        job_title: str,
        matches: list[dict[str, Any]],
        email_type: str,
    ) -> tuple[str, str, str]:
        label = {
            "shortlist": "Shortlist",
            "interview": "Interview Recommendations",
            "feedback": "Candidate Feedback Summary",
        }.get(email_type, "JD Match Summary")
        subject = f"{label}: {job_title}"
        job_title_html = html.escape(job_title)
        lines = [
            f"{label} for {job_title}",
            "",
            "Top matched candidates:",
            "",
        ]

        html_items = []

        for index, match in enumerate(matches, start=1):
            feedback = match.get("ai_feedback") or {}
            candidate_name = match.get("candidate_name") or "Unknown Candidate"
            matched_skills = ", ".join(match.get("matched_skills") or []) or "None confirmed"
            missing_skills = ", ".join(match.get("missing_skills") or []) or "None highlighted"
            recommendation = (
                feedback.get("hiring_recommendation")
                or feedback.get("interview_recommendation")
                or "Review candidate profile"
            )
            lines.extend(
                [
                    f"{index}. {candidate_name} - {round((match.get('final_score') or 0) * 100)}%",
                    f"   Matched skills: {matched_skills}",
                    f"   Missing skills: {missing_skills}",
                    f"   Recommendation: {recommendation}",
                    "",
                ]
            )
            html_items.append(
                "<li>"
                f"<strong>{html.escape(candidate_name)}</strong> "
                f"({round((match.get('final_score') or 0) * 100)}%)"
                f"<br/>Matched: {html.escape(matched_skills)}"
                f"<br/>Missing: {html.escape(missing_skills)}"
                f"<br/>Recommendation: {html.escape(recommendation)}"
                "</li>"
            )

        lines.extend(
            [
                "This message was generated by the AI Resume Screening ATS.",
            ]
        )
        html = (
            f"<h2>{html.escape(label)} for {job_title_html}</h2>"
            "<ol>"
            + "".join(html_items)
            + "</ol><p>This message was generated by the AI Resume Screening ATS.</p>"
        )

        return subject, "\n".join(lines), html


# Backwards-compatible name for old imports.
ResendEmailService = EmailJSEmailService
