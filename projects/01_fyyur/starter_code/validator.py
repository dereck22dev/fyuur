# ----------------------------------------------------------------------------#
# Import.
# ----------------------------------------------------------------------------#
from wtforms.validators import ValidationError
import re

# ----------------------------------------------------------------------------#
# form validator.
# ----------------------------------------------------------------------------#


def validate_genres(form, genres):
    genres_enabled = [
        "Alternative",
        "Blues",
        "Classical",
        "Country",
        "Electronic",
        "Folk",
        "Funk",
        "Hip-Hop",
        "Heavy Metal",
        "Instrumental",
        "Jazz",
        "Musical Theatre",
        "Pop",
        "Punk",
        "R&B",
        "Reggae",
        "Rock n Roll",
        "Soul",
        "Other",
    ]
    for genre in genres.data:
        if genre not in genres_enabled:
            raise ValidationError("This genre is not allowed")


def validate_state(form, state):
    states_enabled = [
        "AL",
        "AK",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "DC",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]
    if state.data not in states_enabled:
        raise ValidationError("This state is not allowed")


def validate_phone(form, phone):
    reg_validator = r"\+?(\d?)[-\(\.]?(\d{3})[-\)\.\s]?(\d{3})[-\.\s]?\d{4}"
    phone_enabled = re.match(reg_validator, phone.data)
    print(f"phone number: {phone.data}")
    print(f"phone number is valid? : {phone_enabled}")
    if not phone_enabled:
        raise ValidationError("This phone number is not allowed")
