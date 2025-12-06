import re


def sanitize_prompt(text: str) -> str:
    if not text:
        return ""

    # Masquer emails
    text = re.sub(r"\S+@\S+\.\S+", "[EMAIL]", text)

    # Masquer numéros téléphone
    text = re.sub(r"\+?\d{8,15}", "[PHONE]", text)

    # Masquer mots de passe
    text = re.sub(r"(password\s*[:=]\s*)(\S+)", r"\1***", text, flags=re.IGNORECASE)

    return text
