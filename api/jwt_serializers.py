from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenObtainSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.settings import api_settings
from django.conf import settings
from .tokens import RefreshToken

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls,user):
        token = super().get_token(user)

        # Adding custom token
        token["user"] = user.email,user.name,user.bio

        return token

class CustomTokenObtainSerializer(serializers.Serializer):
    token_class = RefreshToken

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self.fields["username"] = serializers.CharField(max_length=255)

    def validate(self,attrs):
        authenticate_kwargs= {
            "username": attrs["username"]
        }

        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.AuthenticationFailed(
                self.error_messages["no_active_account"],
                "no_active_account",
            )

        return {}

    @classmethod
    def get_token(cls, user):
        return cls.token_class.for_user(user)

class CustomTokenObtainPairSerializer(CustomTokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        #if api_settings.UPDATE_LAST_LOGIN:
        #    update_last_login(None, self.user)

        return data

class CustomTokenObtainPairSerializerForAnonUser(CustomTokenObtainPairSerializer):
    @classmethod
    def get_token(cls,anon_user):
        token = super().get_token(anon_user)

        token["anon_user"] = anon_user.username

        return token