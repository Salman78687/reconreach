"""PhoneInfoga wrapper — uses the CLI tool if installed, plus phonenumbers lib."""
import asyncio
import json
import re
import phonenumbers
from phonenumbers import geocoder, carrier


def parse_phone(raw: str) -> dict:
    """Parse a phone number using the phonenumbers library."""
    try:
        parsed = phonenumbers.parse(raw, None)
        if not phonenumbers.is_valid_number(parsed):
            # Try with a +1 prefix (assume US if no country code)
            parsed = phonenumbers.parse(f"+{raw.lstrip('+')}", None)

        return {
            "is_valid": phonenumbers.is_valid_number(parsed),
            "formatted": phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            "country": geocoder.description_for_number(parsed, "en"),
            "carrier": carrier.name_for_number(parsed, "en"),
            "line_type": _line_type(parsed),
        }
    except Exception:
        return {"is_valid": False}


def _line_type(parsed) -> str | None:
    try:
        nt = phonenumbers.number_type(parsed)
        mapping = {
            phonenumbers.PhoneNumberType.MOBILE: "mobile",
            phonenumbers.PhoneNumberType.FIXED_LINE: "landline",
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "mobile/landline",
            phonenumbers.PhoneNumberType.TOLL_FREE: "toll_free",
            phonenumbers.PhoneNumberType.VOIP: "voip",
        }
        return mapping.get(nt, "unknown")
    except Exception:
        return None


async def run_phoneinfoga(phone: str) -> dict:
    """Run PhoneInfoga CLI if available. Returns raw output dict."""
    try:
        proc = await asyncio.create_subprocess_exec(
            "phoneinfoga", "scan", "-n", phone, "--output", "json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
        output = stdout.decode()
        # PhoneInfoga JSON output starts after the banner
        json_match = re.search(r"\{.*\}", output, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except (FileNotFoundError, asyncio.TimeoutError, json.JSONDecodeError):
        pass
    return {}
