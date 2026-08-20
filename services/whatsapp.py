import re


def _ensure_brazilian_ninth_digit(digits: str) -> str:
    """Insert the mobile 9 after DDD when the subscriber number has only 8 digits.

    Example: 55 48 30256255 → 55 48 9 30256255. Displayed phone is unchanged.
    """
    if digits.startswith("55") and len(digits) == 12:
        return f"{digits[:4]}9{digits[4:]}"
    return digits


def to_whatsapp_url(phone: str | None) -> str | None:
    if not phone or phone.strip() in ("", "Não informado"):
        return None

    digits = re.sub(r"\D", "", phone)
    if len(digits) < 10:
        return None
    if len(digits) in (10, 11) and not digits.startswith("55"):
        digits = f"55{digits}"
    digits = _ensure_brazilian_ninth_digit(digits)
    return f"https://wa.me/{digits}"
