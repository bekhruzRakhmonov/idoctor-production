import datetime
from django.conf import settings
import base64 as b64
from django.core import serializers
from django.core.signing import Signer
from .models import User
import json


def b64_encode(s):
    data_json = json.dumps(s, indent=4, sort_keys=True, default=str)
    encoded_json_data = data_json.encode("utf-8")
    return b64.urlsafe_b64encode(encoded_json_data).strip(b'=')

def b64_decode(s):
    pad = b'=' * (-len(s) % 4)
    pad_decoded = pad.decode("utf-8")
    data = b64.urlsafe_b64decode(s + pad_decoded)
    return data.decode("utf-8")

def set_cookie(response, key, value, days_expire=7):
    print("Set cookie is working now:",value)
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(
        datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age),
        "%a, %d-%b-%Y %H:%M:%S GMT",
    )

    base64_bytes = b64_encode(value)
    base64_string = base64_bytes.decode("utf-8")
    response.set_cookie(
        key,
        base64_string,
        max_age=max_age,
        expires=expires,
        domain=settings.SESSION_COOKIE_DOMAIN,
        secure=settings.SESSION_COOKIE_SECURE or None,
    )

# views.py
# def view(request):
#    response = HttpResponse("hello")
#    set_cookie(response, 'name', 'jujule')
#    return response