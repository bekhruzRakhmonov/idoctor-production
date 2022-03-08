from ..models import Like,Notification

def custom_context_processors(request):
	likes = Like.objects.all()
	if not request.user.is_anonymous:
		notifications = Notification.objects.filter(to_user__exact=request.user)
		notf_count = Notification.get_count(to_user=request.user)
		return {"likes":likes,"notf_count":notf_count,"notifications":notifications}
	return {"likes":likes}