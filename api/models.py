from django.db import models
from django.conf import settings
from django.utils.functional import cached_property
from base.models import AnonUser

class TokenAnonUser:
	is_active = True

	@cached_property
	def is_staff(self):
		return False

	@cached_property
	def is_superuser(self):
		return False        

class OutstandingToken(models.Model):
	id = models.BigAutoField(primary_key=True, serialize=False)
	anon_user = models.ForeignKey(
		settings.AUTH_ANON_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
	)

	jti = models.CharField(unique=True, max_length=255)
	token = models.TextField()

	created_at = models.DateTimeField(null=True, blank=True)
	expires_at = models.DateTimeField()

	class Meta:
		# Work around for a bug in Django:
		# https://code.djangoproject.com/ticket/19422
		#
		# Also see corresponding ticket:
		# https://github.com/encode/django-rest-framework/issues/705
		abstract = (
			"rest_framework_simplejwt.token_blacklist" not in settings.INSTALLED_APPS
		)
		ordering = ("anon_user",)

	def __str__(self):
		return "Token for {} ({})".format(
			self.anon_user,
			self.jti,
		)


class BlacklistedToken(models.Model):
	id = models.BigAutoField(primary_key=True, serialize=False)
	token = models.OneToOneField(OutstandingToken, on_delete=models.CASCADE)

	blacklisted_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		# Work around for a bug in Django:
		# https://code.djangoproject.com/ticket/19422
		#
		# Also see corresponding ticket:
		# https://github.com/encode/django-rest-framework/issues/705
		abstract = (
			"rest_framework_simplejwt.token_blacklist" not in settings.INSTALLED_APPS
		)

	def __str__(self):
		return f"Blacklisted token for {self.token.anon_user}"
