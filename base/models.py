from django.db import models
from django.db.models import Q
from ckeditor.fields import RichTextField
from django.conf import settings
from django.contrib.auth.models import AbstractUser,AbstractBaseUser,PermissionsMixin
from django.contrib.auth.models import UserManager,BaseUserManager
from django.contrib.auth.hashers import make_password
from django.core.validators import FileExtensionValidator
from . import validators
from django.urls import reverse, reverse_lazy
from django.utils import timezone
import datetime
import random
import uuid
import typing

class CustomUserManager(BaseUserManager):
    def create_superuser(self,email,name,bio,password=None,**others):
        others.setdefault('is_staff',True)
        others.setdefault('is_superuser',True)
        others.setdefault('is_active',True)

        if others.get('is_staff') is not True:
            raise ValueError("Superuser must be assigned to is_staff=True")
        if others.get('is_superuser') is not True:
            raise ValueError("Superuser must be assigned to is_superuser=True")

        user = self.create_user(email,name,bio,password,**others)
        # user.is_admin = True
        user.save(using=self._db)

        return user

    def create_user(self,email,name,bio,password=None,**others):
        others.setdefault('is_active',True)
        if not email:
            raise ValueError("You must provide an email address")
        email = self.normalize_email(email)
        user = self.model(email=email,name=name,bio=bio,**others)
        user.set_password(password)
        user.save(using=self._db)

        return user

class User(AbstractBaseUser,PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)    
    image = models.ImageField(upload_to="users/profile_image",null=True)
    birth_date = models.DateTimeField(null=True)
    name = models.CharField(max_length=200,null=True)
    email = models.EmailField(unique=True,null=True)
    bio = models.TextField(null=True)
    profession_categories = (
        ("Family physicians","Family physicians"),
        ("Internists","Internists"),
        ("Emergency physicians","Emergency physicians"),
        ("Psychiatrists","Psychiatrists"),
        ("Obstetricians and gynecologists","Obstetricians and gynecologists"),
        ("Neurologists","Neurologists"),
        ("Radiologists","Radiologists"),
        ("Anesthesiologists","Anesthesiologists"),
        ("Pediatricians","Pediatricians"),
        ("Cardiologists","Cardiologists"),
    )
    profession = models.CharField(choices=profession_categories,max_length=255,null=True)
    status = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["name","bio"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def get_status(self,user):
        return self.objects.get(user=user).status

    @property
    def is_anon(self):
        return False

class AnonUser(models.Model):
    username = models.CharField(max_length=255,null=True,blank=True,unique=True)
    ip = models.CharField(max_length=50,null=True) #models.GenericIPAddressField()
    date_joined = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_user(cls,ip,username=None):
        if username is not None:
            obj,created = cls.objects.get_or_create(ip=ip,username=username)
            if created:
                obj.save()
            return obj
        obj,created = cls.objects.get_or_create(ip=ip)
        if created:
            obj.username = f"user{obj.id}"
            obj.save()
        return obj

    @property
    def is_authenticated(self):
        # This always returns True
        return False

    @property
    def is_anonymous(self):
        return False

    @property
    def is_anon(self):
        return True
    
    @property
    def is_staff(self):
        return False
    
    @property
    def is_active(self):
        return True

    def __str__(self):
        return self.username

class Follower(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="following_user")
    followers = models.ManyToManyField(User,related_name="followers")
    anon_followers = models.ManyToManyField(AnonUser,related_name="anon_followers")

    def __str__(self):
        return f"{self.followers} is followed to {self.user}"

    @classmethod
    def get_count(cls,user):
        try:
            followers = cls.objects.get(user=user)
            followers_count = followers.followers.all().count()
            return followers_count
        except Follower.DoesNotExist:
            return 0

    @classmethod
    def follow(cls,user: User,follower: typing.Union[User,AnonUser]) -> None:
        obj,created = cls.objects.get_or_create(user=user)
        if isinstance(follower,User):
            if not created:
                obj.followers.add(follower)
                obj.save()
            else:
                obj.followers.add(follower)
                obj.save()
        else:
            if not created:
                obj.anon_followers.add(follower)
                obj.save()
            else:
                obj.anon_followers.add(follower)
                obj.save()
        return obj

    @classmethod
    def unfollow(cls,user: User,follower: typing.Union[User,AnonUser]) -> None:
        obj = cls.objects.get(user=user)
        if isinstance(follower,User):
            obj.followers.remove(follower)
        else:
            obj.anon_followers.remove(follower)
        return obj

class ChatMessage(models.Model):
    outgoing = models.ForeignKey(User, on_delete=models.CASCADE,related_name="outgoing",null=True,blank=True)
    outgoing_anon_user = models.ForeignKey(AnonUser, on_delete=models.CASCADE,related_name="outgoing_anon_user",null=True,blank=True)
    incoming = models.ForeignKey(User, on_delete=models.CASCADE,related_name="incoming",null=True)
    message = models.TextField(null=True)
    date = models.DateTimeField(auto_now_add=True,null=True)
    is_seen = models.BooleanField(default=False)
    
    @classmethod
    def create(cls,message,outgoing: User,incoming: User) -> None:
        if outgoing.is_authenticated:
            return cls(outgoing=outgoing,incoming=incoming,message=message)
        elif outgoing.is_anonymous:
            return cls(outgoing_anon_user=outgoing,incoming=incoming,message=message)

    def __str__(self):
        return self.message
    
    @property
    def check_seen(self):
        return self.is_seen
    
class ChatRoom(models.Model):
    room_id =  models.CharField(max_length=255)
    outgoing = models.ForeignKey(User, on_delete=models.CASCADE,related_name="out_room_user")
    incoming = models.ForeignKey(User, on_delete=models.CASCADE,related_name="in_room_user")
    messages = models.ManyToManyField(ChatMessage,related_name="messages")

    @classmethod
    def get_room_id(cls,outgoing_user,incoming_user):
        chat_room = cls.objects.get((Q(incoming=incoming_user) & Q(outgoing=outgoing_user)) | (Q(incoming=outgoing_user) & Q(outgoing=incoming_user)))
        return chat_room.room_id

    @classmethod
    def create_room_id(cls,outgoing_user,incoming_user):
        chat_room = cls.objects.create(room_id=f"{outgoing_user.pk}{incoming_user.pk}",outgoing=outgoing_user,incoming=incoming_user)
        chat_room.save()
        print("Models",chat_room.room_id)
        return chat_room.room_id

    def __str__(self):
        return self.room_id

class Post(models.Model):
    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User,on_delete=models.CASCADE,related_name="post_user")
    text = models.TextField(blank=True)
    photo = models.ImageField(upload_to='posts/images/',blank=True,null=True)
    video = models.FileField(upload_to='posts/videos/',validators=[FileExtensionValidator(allowed_extensions=['MOV','avi','mp4','webm','mkv'])],blank=True,null=True)
    pub_date = models.DateTimeField(auto_now_add=True,null=True)
    likes = models.ManyToManyField("Like",related_name="post_likes",blank=True)

    def __str__(self):
        return f"{self.text}" or f"{self.photo}"

    def get_absolute_url(self):
        return reverse("article-detail", kwargs={"pk":self.pk})  

    @classmethod
    def get_count(cls,user):
        return cls.objects.filter(owner=user).count()

class Comment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="comment_user",blank=True,null=True)
    anon_user = models.ForeignKey(AnonUser,on_delete=models.CASCADE,related_name="comment_anon_user",blank=True,null=True)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="post_comment",null=True)
    comment = models.ManyToManyField("ChildComment",related_name="child_comment")
 
    def get_absolute_url(self):
        return reverse("get-comment-by-id",args=[str(self.id)])

    def __str__(self):
        return f"{self.user}'s comment is '{self.comment}'"

class ChildComment(models.Model):
    content = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True,null=True)

class CommentArticle(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="comment_article_user",blank=True,null=True)
    anon_user = models.ForeignKey(AnonUser,on_delete=models.CASCADE,related_name="comment_article_anon_user",blank=True,null=True)
    article = models.ForeignKey("Article",on_delete=models.CASCADE,related_name="article_comment")
    comment = models.ManyToManyField("ChildCommentArticle",related_name="child_comment_article")
 
    def get_absolute_url(self):
        return reverse("get-comment-by-id",args=[str(self.id)])

    def __str__(self):
        return f"{self.user}'s comment is '{self.comment}'"

class ChildCommentArticle(models.Model):
    content = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.content

class Like(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="like_post_user",null=True,blank=True)
    anon_user = models.ForeignKey(AnonUser,on_delete=models.CASCADE,related_name="like_post_anonymous_user",null=True,blank=True)
    date = models.DateTimeField(auto_now_add=True)
    like = models.BooleanField(default=False)
    
    def __str__(self):
        if self.user:
            return str(self.user.pk)
        return str(self.anon_user)
    
class Article(models.Model):
    comments = models.ForeignKey("self",on_delete=models.CASCADE,related_name="own_article",null=True,blank=True)
    author = models.ForeignKey(User,on_delete=models.CASCADE)
    headline = models.CharField(max_length=255)
    body = RichTextField(validators=[validators.validate_article])
    date = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    likes = models.ManyToManyField("Like",related_name="article_likes",blank=True)

    @property
    def views_count(self):
        return self.views_count
        
    @views_count.setter
    def increase_views_count(self,pk):
        count = self.objects.get(pk=pk).views_count
        return self.objects.filter(pk=pk).update(views_count=count+1)

    @classmethod
    def get_count(cls,author):
        count = cls.objects.filter(author=author).count()
        return count

    def __str__(self):
        return f"Author: {self.author} About: {self.headline}"
    
    def get_absolute_url(self):
        return reverse("base:article-detail", kwargs={"pk":self.pk})
    

class Notification(models.Model):
    notf_types = (
        ("following","FOLLOWING"),
        ("post","POST"),
        ("article","ARTICLE"),
        ("comment","COMMENT"),
        ("like","LIKE"),
        ("like_article","LIKE-ARTICLE"),
        ("comment_article","COMMENT ARTICLE"),
    )
    from_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="notf_from_user",null=True,blank=True)
    from_anon_user = models.ForeignKey(AnonUser,on_delete=models.CASCADE,related_name="notf_from_anon_user",null=True,blank=True)
    to_user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="notf_to_user",null=True,blank=True)
    to_anon_user = models.ForeignKey(AnonUser,on_delete=models.CASCADE,related_name="notf_to_anon_user",null=True,blank=True)
    notf_comment = models.ForeignKey(Comment,on_delete=models.CASCADE,related_name="notf_comments",null=True)
    notf_comment_article = models.ForeignKey(CommentArticle,on_delete=models.CASCADE,related_name="notf_comments_article",null=True)
    notf_like = models.ForeignKey(Like,on_delete=models.CASCADE,related_name="notf_likes",null=True)
    notf_post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name="notf_posts",null=True)
    notf_article = models.ForeignKey(Article,on_delete=models.CASCADE,related_name="notf_article",null=True)
    notf_follower = models.ForeignKey(Follower,on_delete=models.CASCADE,related_name="notf_followers",null=True)
    notf_type = models.CharField(max_length=255,choices=notf_types,null=True)
    date = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        msg = ''
        if self.notf_type == "comment":
            msg = f"{self.from_user} is wrote comment to {self.to_user}"
        return msg

    @classmethod
    def get_count(cls,to_user=None,to_anon_user=None):
        if to_anon_user is None:
            count = cls.objects.filter(to_user=to_user).count()
        else:
            count = cls.objects.filter(to_anon_user=to_anon_user).count()
        return count

class Client(models.Model):
    client = models.ForeignKey(AnonUser,on_delete=models.CASCADE,related_name="appointment_client",blank=True,null=True)
    doctor = models.ForeignKey(User,on_delete=models.CASCADE,related_name="appointment_doctor",blank=True,null=True)
    reason = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

class Appointment(models.Model):
    doctor = models.ForeignKey(User,on_delete=models.CASCADE,related_name="appointment_user")
    clients = models.ManyToManyField(Client,related_name="appointment_clients")
    date = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False)

class SavedMessages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="saved_messages_user",blank=True,null=True)
    anon_user = models.ForeignKey(AnonUser, on_delete=models.CASCADE,related_name="saved_messagess_anon_user",blank=True,null=True)
    posts = models.ManyToManyField(Post,related_name="saved_message_post")
    articles = models.ManyToManyField(Article,related_name="saved_messages_article")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.posts is not None:
            return self.posts.last().text
        return self.articles.last().headline
