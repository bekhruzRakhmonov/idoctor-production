from django.utils.deprecation import MiddlewareMixin
from django.contrib import auth
from django.utils.functional import SimpleLazyObject
from .models import AnonUser
from django.contrib.auth.models import AnonymousUser
from .cookies import b64_decode
import json
import time

class RestrictUserAdminMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith(str(reverse_lazy('admin:index'))):
            if request.user.is_authenticated:
                if not request.user.is_staff:
                    raise Http404
            else:
                raise Http404

        response = self.get_response(request)
        return response

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

    def get_anon_user_by_ip(self,ip):
        try:
            return AnonUser.objects.get(ip=ip)
        except AnonUser.DoesNotExist:
            return None

    def get_anon_user_by_id(self,id):
        try:
            return AnonUser.objects.get(id=id)
        except AnonUser.DoesNotExist:
            return None

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.  
        if request.user.is_anonymous:
            cookies = request.COOKIES
            anon_user_data = cookies.get("data",None)
            anon_user_ip = self.get_client_ip(request)
            all_anon_users = AnonUser.objects.all()
            anon_users_ip = []
            for user in all_anon_users:
                anon_users_ip.append(user.ip)
                
            #if anon_user_data is None:
            if anon_user_ip in anon_users_ip:
                anon_user = self.get_anon_user_by_ip(anon_user_ip)
                request.user = anon_user
            else:
                decoded_data = b64_decode(anon_user_data)
                if decoded_data is not None:
                    anon_user_id = int(decoded_data[7:9])
                    anon_user = self.get_anon_user_by_id(anon_user_id)
                    if anon_user is None:
                        request.user = SimpleLazyObject(lambda: get_user(request))
                    else:
                        request.user = anon_user
                else:
                    request.user.is_anon = False

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        return response

class StatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.total = 0

    def __call__(self,request):
        start_time = time.time()
        request.start_time = start_time
        response = self.get_response(request)
 
        total = time.time() - start_time
        
        response["X-total-time"] = int(self.total * 1000)

        return response

    def process_template_response(self, request, response):
        total = time.time() - request.start_time
        if response.context_data is not None:
            response.context_data["time"] = int(total * 1000)
        return response
