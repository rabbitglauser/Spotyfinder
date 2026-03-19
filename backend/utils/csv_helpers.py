import re
def clean_text(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text or text == "-":
        return None
    return text


def parse_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "y"}


def parse_int(value):
    if value in (None, "", "-"):
        return None
    return int(float(value))


def parse_float(value):
    if value in (None, "", "-"):
        return None
    return float(value)


def parse_date(value):
    text = clean_text(value)
    if not text:
        return None

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        return text

    if re.fullmatch(r"\d{4}-\d{2}", text):
        return f"{text}-01"

    if re.fullmatch(r"\d{4}", text):
        return f"{text}-01-01"

    return None


def parse_timestamp(value):
    text = clean_text(value)
    if not text:
        return None
    return text.replace("Z", "+00:00")


def split_artists(value):
    text = clean_text(value)
    if not text:
        return []
    return [part.strip() for part in text.split(";") if part.strip()]


def split_genres(value):
    text = clean_text(value)
    if not text:
        return []
    return [part.strip() for part in text.split(",") if part.strip()]