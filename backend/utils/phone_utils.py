import re
from typing import Optional

def normalize_phone_e164(phone: str, default_country_code: str = "+1") -> str:
    """
    Normalize phone number to E.164 format.
    
    Args:
        phone: Phone number in various formats
        default_country_code: Default country code if not provided
    
    Returns:
        Phone number in E.164 format (e.g., +14155552671)
    """
    # Remove all non-digit characters except leading +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # If no + at the beginning, add default country code
    if not cleaned.startswith('+'):
        if len(cleaned) == 10:  # US number without country code
            cleaned = f"{default_country_code}{cleaned}"
        elif len(cleaned) == 11 and cleaned.startswith('1'):
            cleaned = f"+{cleaned}"
        else:
            cleaned = f"{default_country_code}{cleaned}"
    
    return cleaned

def format_phone_display(phone: str) -> str:
    """
    Format phone number for display.
    E.g., +14155552671 -> +1 (415) 555-2671
    """
    cleaned = normalize_phone_e164(phone)
    
    if cleaned.startswith('+1') and len(cleaned) == 12:
        return f"+1 ({cleaned[2:5]}) {cleaned[5:8]}-{cleaned[8:]}"
    
    return cleaned

def extract_phone_info(phone: str) -> dict:
    """
    Extract phone number information.
    
    Returns:
        Dictionary with normalized number, display format, and country code
    """
    normalized = normalize_phone_e164(phone)
    
    return {
        "normalized": normalized,
        "display": format_phone_display(normalized),
        "country_code": normalized[:2] if normalized.startswith('+') else None
    }
