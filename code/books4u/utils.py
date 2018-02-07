from .models import *
import re


def password_filter(pwd):

    length_check = len(pwd) > 8
    digit_check = re.search(r"\d", pwd)
    uppercase_check = re.search(r"[A-Z]", pwd)
    pwd_check = (length_check and digit_check and uppercase_check)
    # TODO: Return detailed result
    return pwd_check
