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

@register.filter(name="get_extension", is_safe=True)
def get_extension(value):
    ext = str(value)
    ext = ext.split("/")
    return ext[2][5:]

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

@register.filter(name="filter_like",is_safe=True)
def filter(value):
    global request
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
            anonymous_users.append(_.anon_user)

        if request.user in anonymous_users:
            return "s"
        return "r"

@register.filter(name="check_followed")
def check_followed(follower):
    global request
    followed = False
    if not request.user.is_anonymous:
        request_user = request.user
        try:
            follower = Follower.objects.get(user__exact=follower)
            if request.user in (follower.followers.all() or follower.anon_followers.all()):
                print(follower.followers.all(),follower.anon_followers.all())
                followed = True
        except Follower.DoesNotExist:
            followed = False
        return followed
    return followed

@register.inclusion_tag("components/recommended_users.html",takes_context=True)
def get_context(context):
    print(context["users"])
    return {"userss":context["users"]}
