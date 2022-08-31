from .models import User,Follower,Post,Article,Comment,CommentArticle,Like,Notification
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, m2m_changed

def followers_changed(sender,instance,action,**kwargs):
    if action == 'post_add':
        follower = instance.followers.last()
        obj,created = Notification.objects.get_or_create(from_user=follower,to_user=instance.user,notf_follower=instance,notf_type="following")

m2m_changed.connect(followers_changed,sender=Follower.followers.through)

def anon_followers_changed(sender,instance,action,**kwargs):
    if action == 'post_add':
        follower = instance.anon_followers.last()
        obj,created = Notification.objects.get_or_create(from_anon_user=follower,to_user=instance.user,notf_follower=instance,notf_type="following")

m2m_changed.connect(anon_followers_changed,sender=Follower.anon_followers.through)

@receiver(post_save,sender=Post)
def handle_post(sender,**kwargs):
    instance = kwargs["instance"]
    follower_count = Follower.get_count(user=instance.owner)
    if follower_count > 0:
        followers = Follower.objects.filter(user=instance.owner).values()
        for follower in followers:
            to_user = User.objects.get(pk=follower["user_id"])
            obj,created = Notification.objects.get_or_create(from_user=instance.owner,to_user=to_user,notf_post=instance,notf_type="post")

@receiver(post_save,sender=Article)
def handle_article(sender,**kwargs):
    instance = kwargs["instance"]
    followers_count = Follower.get_count(user=instance.author)
    if followers_count > 0:
        user = Follower.objects.get(user=instance.author)
        for follower in user.followers.all():
            obj,created = Notification.objects.get_or_create(from_user=instance.author,to_user=follower,notf_article=instance,notf_type="article")

        for anon_follower in user.anon_followers.all():
            obj,created = Notification.objects.get_or_create(from_user=instance.author,to_anon_user=anon_follower,notf_article=instance,notf_type="article")
            
@receiver(post_save,sender=Comment)
def handle_comment(sender,*args,**kwargs):
    instance = kwargs["instance"]
    if instance.user is not None and instance.user != instance.post.owner:
        obj,created = Notification.objects.get_or_create(from_user=instance.user,to_user=instance.post.owner,notf_comment=instance,notf_type="comment")
    elif instance.user is None:
        obj,created = Notification.objects.get_or_create(from_anon_user=instance.anon_user,to_user=instance.post.owner,notf_comment=instance,notf_type="comment")

@receiver(post_save,sender=CommentArticle)
def handle_comment(sender,*args,**kwargs):
    instance = kwargs["instance"]
    if instance.user is not None and instance.user != instance.article.author:
        obj,created = Notification.objects.get_or_create(from_user=instance.user,to_user=instance.article.author,notf_comment_article=instance,notf_type="comment_article")
    elif instance.user is None:
        obj,created = Notification.objects.get_or_create(from_anon_user=instance.anon_user,to_user=instance.article.author,notf_comment_article=instance,notf_type="comment_article")

def handle_post_like(sender,instance,action,**kwargs):
    if action == "post_add":
        like = instance.likes.last()
        if not like.user == instance.owner:
            if like.user is not None:
                obj,created = Notification.objects.get_or_create(from_user=like.user,to_user=instance.owner,notf_like=like,notf_type="like")
            else:
                obj,created = Notification.objects.get_or_create(from_anon_user=like.anon_user,to_user=instance.owner,notf_like=like,notf_type="like")

m2m_changed.connect(handle_post_like,sender=Post.likes.through)

def handle_article_like(sender,instance,action,**kwargs):
    if action == "post_add":
        like = instance.likes.last()
        if not like.user == instance.author:
            if like.user is not None:
                obj,created = Notification.objects.get_or_create(from_user=like.user,to_user=instance.author,notf_like=like,notf_type="like_article")
            else:
                obj,created = Notification.objects.get_or_create(from_anon_user=like.anon_user,to_user=instance.author,notf_like=like,notf_type="like_article")

m2m_changed.connect(handle_article_like,sender=Article.likes.through)
