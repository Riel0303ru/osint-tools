# core/company/fingerprints/saas_detector.py
from typing import Dict, List
import re

class SaaSDetector:
    """Deteksi penggunaan SaaS dari berbagai sumber."""

    # Pola dari berbagai sumber
    TXT_VERIFICATION_PATTERNS = {
        "Google Workspace": [
            r"google-site-verification[=:]\s*([a-zA-Z0-9_-]+)",
            r"globalsign-domain-verification[=:]\s*([a-zA-Z0-9_-]+)",
        ],
        "Microsoft 365": [
            r"MS=ms\d+",
            r"microsoft-domain-verification[=:]\s*([a-zA-Z0-9]+)",
        ],
        "Atlassian": [r"atlassian-domain-verification[=:]\s*([a-zA-Z0-9_-]+)"],
        "Slack": [r"slack-domain-verification[=:]\s*([a-zA-Z0-9_-]+)"],
        "GitHub": [r"github-domain-verification[=:]\s*([a-zA-Z0-9_-]+)"],
        "Stripe": [r"stripe-verification[=:]\s*([a-zA-Z0-9_-]+)"],
        "Twilio": [r"twilio-domain-verification[=:]\s*([a-zA-Z0-9_-]+)"],
        "Figma": [r"figma-domain-verification[=:]\s*([a-zA-Z0-9_-]+)"],
        "Vercel": [r"vercel-dns[=:]\s*([a-zA-Z0-9_-]+)"],
        "Netlify": [r"netlify-domain-verification[=:]\s*([a-zA-Z0-9_-]+)"],
        "HubSpot": [r"hubspot-domain-verification[=:]\s*([a-zA-Z0-9_-]+)"],
        "Zendesk": [r"zendesk-domain-verification[=:]\s*([a-zA-Z0-9_-]+)"],
        "Mailchimp": [r"mailchimp-domain-verification[=:]\s*([a-zA-Z0-9_-]+)"],
        "Sentry": [r"sentry-domain-verification[=:]\s*([a-zA-Z0-9_-]+)"],
        "Heroku": [r"heroku-domain-verification[=:]\s*([a-zA-Z0-9_-]+)"],
        "Tailscale": [r"tailscale-domain-verification[=:]\s*([a-zA-Z0-9_-]+)"],
    }

    MX_PROVIDER_PATTERNS = {
        "Google Workspace": [r"\.google(?:mail)?\.com\.$", r"aspmx\.l\.google\.com"],
        "Microsoft 365": [r"\.mail\.protection\.outlook\.com\.$", r"\.outlook\.com\.$"],
        "Zoho Mail": [r"\.zoho\.com\.$", r"\.zohomail\.com\.$"],
        "ProtonMail": [r"\.protonmail\.com\.$"],
    }

    SPF_INCLUDE_PATTERNS = {
        "Google Workspace": [r"_spf\.google\.com"],
        "Microsoft 365": [r"spf\.protection\.outlook\.com"],
        "SendGrid": [r"sendgrid\.net"],
        "Mailgun": [r"mailgun\.org"],
        "Amazon SES": [r"amazonses\.com"],
    }

    @classmethod
    def detect_from_txt(cls, txt_records: List[str]) -> Dict[str, List[str]]:
        """Deteksi SaaS dari TXT records (verification)."""
        detected = {}
        for saas_name, patterns in cls.TXT_VERIFICATION_PATTERNS.items():
            for txt in txt_records:
                txt_clean = txt.strip('"')
                for pattern in patterns:
                    if re.search(pattern, txt_clean):
                        if saas_name not in detected:
                            detected[saas_name] = []
                        match = re.search(pattern, txt_clean)
                        detected[saas_name].append(match.group(0) if match else txt_clean[:80])
        return detected

    @classmethod
    def detect_from_mx(cls, mx_records: List[str]) -> Dict[str, str]:
        """Deteksi email provider dari MX records."""
        detected = {}
        for provider_name, patterns in cls.MX_PROVIDER_PATTERNS.items():
            for mx in mx_records:
                for pattern in patterns:
                    if re.search(pattern, mx, re.IGNORECASE):
                        detected[provider_name] = mx.strip()
                        break
        return detected

    @classmethod
    def detect_from_spf(cls, spf_record: str) -> Dict[str, str]:
        """Deteksi layanan email dari SPF includes."""
        detected = {}
        if not spf_record:
            return detected
        for service_name, patterns in cls.SPF_INCLUDE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, spf_record, re.IGNORECASE):
                    detected[service_name] = spf_record[:100]
                    break
        return detected