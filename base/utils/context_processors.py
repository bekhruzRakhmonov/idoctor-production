from ..models import Like,Notification
import datetime

def custom_context_processors(request):
	likes = Like.objects.all()
	date_time = str(datetime.datetime.now())[:10]
	if not request.user.is_anonymous and not request.user.is_anon:
		notifications = Notification.objects.filter(to_user__exact=request.user)
		notf_count = Notification.get_count(to_user=request.user)
		return {"likes":likes,"notf_count":notf_count,"notifications":notifications}
	elif not request.user.is_anonymous and not request.user.is_authenticated:
		notifications = Notification.objects.filter(to_anon_user__exact=request.user)
		notf_count = Notification.get_count(to_anon_user=request.user)
		return {"likes":likes,"notf_count":notf_count,"notifications":notifications}
	return {"likes":likes,"date_time":date_time}
