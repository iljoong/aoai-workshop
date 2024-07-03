# utils.py

import secrets
import string

alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits

def randstr(n=12):
    return "".join([secrets.choice(alphabet) for i in range(n)])