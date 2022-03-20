from django.utils.deprecation import MiddlewareMixin
from django.contrib import auth
from django.utils.functional import SimpleLazyObject
from .models import AnonymousUser as CustomAnonymousUser
from django.contrib.auth.models import AnonymousUser
from .cookies import b64_decode
import json
import ast

def get_user(request):
    if not hasattr(request, "_cached_user"):
        request._cached_user = auth.get_user(request)
        print(request._cached_user)
    return request._cached_user


class AnonUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def get_client_ip(self,request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ip = x_forwarded_for
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        # request.user = SimpleLazyObject(lambda: get_user(request))  
        if request.user.is_anonymous:
            cookies = request.COOKIES
            anon_user_data = cookies.get("data",None)
            anon_user_ip = self.get_client_ip(request)
            all_anon_users = CustomAnonymousUser.objects.all()
            anon_users_ip = []
            for user in all_anon_users:
                anon_users_ip.append(user.ip)
                
            if anon_user_data is None:
                if anon_user_ip in anon_users_ip:
                    anon_user = CustomAnonymousUser.objects.get(ip=anon_user_ip)
                    request.user = anon_user
            else:
                decoded_data = b64_decode(anon_user_data)
                anon_user_id = int(decoded_data[7:9])
                anon_user = CustomAnonymousUser.objects.get(id=anon_user_id)
                request.user = anon_user

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        return response