from rest_framework_simplejwt.tokens import Token,BlacklistMixin,AccessToken
from rest_framework_simplejwt.settings import api_settings
from .models import OutstandingToken
from rest_framework_simplejwt.utils import aware_utcnow, datetime_from_epoch, datetime_to_epoch, format_lazy

class CustomToken(Token):
    @classmethod
    def for_user(cls, user):
        """
        Returns an authorization token for the given user that will be provided
        after authenticating the user's credentials.
        """
        user_id = getattr(user, api_settings.USER_ID_FIELD)
        if not isinstance(user_id, int):
            user_id = str(user_id)

        token = cls()
        token[api_settings.USER_ID_CLAIM] = user_id

        return token


class AccessToken(CustomToken):
    token_type = "access"
    lifetime = api_settings.ACCESS_TOKEN_LIFETIME

class CustomBlacklistMixin(BlacklistMixin):

    @classmethod
    def for_user(cls,user):
        """
        Adds this token to the outstanding token list.
        """
        token = super(BlacklistMixin,cls).for_user(user)

        jti = token[api_settings.JTI_CLAIM]
        exp = token["exp"]

        OutstandingToken.objects.create(
            anon_user=user,
            jti=jti,
            token=str(token),
            created_at=token.current_time,
            expires_at=datetime_from_epoch(exp),
        )

        return token

class RefreshToken(CustomBlacklistMixin, CustomToken):
    token_type = "refresh"
    lifetime = api_settings.REFRESH_TOKEN_LIFETIME
    no_copy_claims = (
        api_settings.TOKEN_TYPE_CLAIM,
        "exp",
        # Both of these claims are included even though they may be the same.
        # It seems possible that a third party token might have a custom or
        # namespaced JTI claim as well as a default "jti" claim.  In that case,
        # we wouldn't want to copy either one.
        api_settings.JTI_CLAIM,
        "jti",
    )
    access_token_class = AccessToken

    @property
    def access_token(self):
        """
        Returns an access token created from this refresh token.  Copies all
        claims present in this refresh token to the new access token except
        those claims listed in the `no_copy_claims` attribute.
        """
        access = self.access_token_class()

        # Use instantiation time of refresh token as relative timestamp for
        # access token "exp" claim.  This ensures that both a refresh and
        # access token expire relative to the same time if they are created as
        # a pair.
        access.set_exp(from_time=self.current_time)

        no_copy = self.no_copy_claims
        for claim, value in self.payload.items():
            if claim in no_copy:
                continue
            access[claim] = value

        return access
