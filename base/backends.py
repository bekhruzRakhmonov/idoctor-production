from django.contrib.auth.backends import BaseBackend
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import check_password
from .models import User,AnonUser

class CustomBackend(BaseBackend):
    def authenticate(self,request,username=None,email=None,password=None):
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
        elif username is not None:
            try:
                anon_user = AnonUser.objects.get(username=username)
                return anon_user
            except AnonUser.DoesNotExist:
                raise ValidationError("User does not exists.")
        else:
            try:
                user = User.objects.get(email=email)
                if user.check_password(password):
                    return user
                raise ValidationError("Password is incorrect!")
            except User.DoesNotExist:
                raise ValidationError("User does not exists.")
        return None
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
