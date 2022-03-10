from django.contrib.auth.backends import BaseBackend
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from .models import User

class CustomBackend(BaseBackend):
    def authenticate(self,request,email=None,password=None):
        login_valid = (settings.ADMIN_LOGIN == email)
        pwd_valid = check_password(password,settings.ADMIN_PASSWORD)
        if login_valid and pwd_valid:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = User(email=email)
                user.is_staff = True
                user.is_superuser = True
                user.save()
            return user
        else:
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    return user
                raise ValidationError("Password is incorrect!")
            except User.DoesNotExist:
                raise ValidationError("User does not exists")
        return None
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
