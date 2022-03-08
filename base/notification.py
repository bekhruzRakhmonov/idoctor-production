from .models import User,Follower,Post,Article,Comment,CommentArticle,Like,Notification
from django.dispatch import receiver
from django.db.models.signals import post_save,pre_save

@receiver(post_save,sender=Follower)
def handle_follower(sender,**kwargs):
    instance = kwargs["instance"]
    obj,created = Notification.objects.get_or_create(from_user=instance.follower.last(),to_user=instance.user,notf_follower=instance,notf_type="following")

@receiver(post_save,sender=Post)
def handle_post(sender,**kwargs):
    instance = kwargs["instance"]
    follower_count = Follower.get_count(user=instance.owner)
    if follower_count > 0:
        followers = Follower.objects.filter(user=instance.owner).values()
        for follower in followers:
            to_user = User.objects.get(pk=follower["follower_id"])
            obj,created = Notification.objects.get_or_create(from_user=instance.owner,to_user=to_user,notf_post=instance,notf_type="post")

@receiver(post_save,sender=Article)
def handle_post(sender,**kwargs):
    instance = kwargs["instance"]
    follower_count = Follower.get_count(user=instance.author)
    if follower_count > 0:
        followers = Follower.objects.filter(user=instance.author).values()
        for follower in followers:
            to_user = User.objects.get(pk=follower["follower_id"])
            obj,created = Notification.objects.get_or_create(from_user=instance.author,to_user=to_user,notf_article=instance,notf_type="article")

@receiver(post_save,sender=Comment)
def handle_comment(sender,*args,**kwargs):
    instance = kwargs["instance"]
    if not instance.user == instance.post.owner:
        obj,created = Notification.objects.get_or_create(from_user=instance.user,to_user=instance.post.owner,notf_comment=instance,notf_type="comment")

@receiver(post_save,sender=CommentArticle)
def handle_comment(sender,*args,**kwargs):
    instance = kwargs["instance"]
    if not instance.user == instance.article.author:
        obj,created = Notification.objects.get_or_create(from_user=instance.user,to_user=instance.article.author,notf_comment_article=instance,notf_type="comment_article")

@receiver(post_save,sender=Like)
def handle_like(sender,*args,**kwargs):
    instance = kwargs["instance"]
    # if not instance.user == instance.post.owner:
      #  obj,created = Notification.objects.get_or_create(from_user=instance.user,to_user=instance.post.owner,notf_like=instance,notf_type="like")

