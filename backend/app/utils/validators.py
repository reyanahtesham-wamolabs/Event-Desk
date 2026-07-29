from pydantic import AfterValidator
from typing import Annotated
import re
from datetime import UTC,datetime
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z][a-zA-Z0-9_.+-]*@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$"
)
MIN_LENGTH=8
PASSWORD_REGEX=re.compile(
        rf"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{{}};':\"\\|,.<>/?])\S{{{MIN_LENGTH},}}$"
)

def check_email(value: str) -> str:
    original_value = value
    value = value.strip().lower()

    if not EMAIL_REGEX.fullmatch(value):
        raise ValueError("Invalid email address")

    return original_value

def check_password(value: str) -> str:
    if not PASSWORD_REGEX.match(value):
        raise ValueError(
            f"Password must be at least {MIN_LENGTH} characters long, contain at least one uppercase letter, one lowercase letter, one number, one special character, and must not contain whitespace."
        )
    return value

def check_non_empty_value(value: str) -> str:
    if not value.strip():
        raise ValueError("Cannot accept empty string")
    return value
def validate_event_time(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("event_time must include a timezone offset")

    return value.astimezone(UTC)

email_value=Annotated[str,AfterValidator(check_email)]
password_value=Annotated[str,AfterValidator(check_password)]
non_empty_value=Annotated[str,AfterValidator(check_non_empty_value)]
datetime_with_timezone=Annotated[datetime,AfterValidator(validate_event_time)]