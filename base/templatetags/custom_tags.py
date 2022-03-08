from django import template
from ..models import Post, Article, Like, Comment, User, Follower
import uuid
import textwrap as tw

register = template.Library()

request = None

@register.filter(name="truncate_bio")
def truncate(value):
    return value[:60]

@register.filter(name="cut", is_safe=True)
def cut(value):
    time = str(value)
    return time[10:16]

@register.filter(name="filter_comment", is_safe=True)
def filter(value):
    comment = Comment.objects.filter(post_id__exact=value)
    if len(comment.values()) > 0:
        return comment
    return None

@register.filter(name="filter_user",is_safe=True)
def filter(value):
    global request
    request = value
    return value

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@register.filter(name="filter_like",is_safe=True)
def filter(value):
    global request
    ip = get_client_ip(request)
    users = []
    anonymous_users = []
    if request.user.is_authenticated:
        for _ in value:
            users.append(_.user)
        if request.user in users:
            return "s"
        return "r"
    else:
        for _ in value:
            anonymous_users.append(_.anonymous_user)

        if ip in anonymous_users:
            return "s"
        return "r"

@register.filter(name="check_followed")
def check_followed(follower):
    global request
    print(request)
    request_user = request.user
    followed = True
    try:
        Follower.objects.get(user__exact=follower,follower__exact=request_user)
    except Follower.DoesNotExist:
        followed = False
    print(followed)
    return followed

@register.inclusion_tag("components/recommended_users.html",takes_context=True)
def get_context(context):
    print(context["users"])
    return {"userss":context["users"]}
