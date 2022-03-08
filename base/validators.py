from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

def validate_article(value):
    if len(value) < 255:
        raise ValidationError(_("Minimium text length is 255"))