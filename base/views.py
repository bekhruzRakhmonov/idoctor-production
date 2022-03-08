from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden,Http404,JsonResponse
from django.views import View
from django.views.generic.edit import CreateView, FormView, UpdateView, DeleteView
from django.views.generic import ListView
from django.views.generic.base import ContextMixin
from django.views import generic
from django.db.models import Q
from django.db import transaction
from django.db.models.signals import post_save,pre_save
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.core.exceptions import *
from .exceptions import FollowerError
from django.utils.text import slugify
from django.contrib import messages
from django.views.decorators.clickjacking import xframe_options_exempt
from .models import User, Post, Article, Like, Comment, ChildComment, CommentArticle, ChildCommentArticle, ChatMessage, ChatRoom, Follower, Notification
from .forms import UserCreationForm, UserLoginForm, UserPasswordChangeForm, UserSetPasswordForm, ChangeUserForm,CreatePostForm, PostCommentForm, CreateArticleForm
import json
import threading
import base64
from . import notification
import mimetypes
# https://support.lenovo.com/uz/en/solutions/ht505250-how-to-reduce-or-expand-system-partition-c-drive-size-in-windows

# https://gitpodio-templatepythond-9o72sfbanvp.ws-eu34.gitpod.io/

to_be_decoded = "VGhpcyBpcyBHZWVrc0ZvckdlZWtzIDQ1NDU0NSAjICQlNjc4KiZeQCE="
decoded = base64.b64decode(bytes(to_be_decoded, 'utf-8'))
print(decoded.decode("utf-8"))

print("[THREADING ACTIVE COUNT]",threading.active_count())
print("[CURRENT THREAD]",threading.current_thread())
print(threading.get_ident())
print(threading.get_native_id())

class Main(View):
    def get(self,request, *arg, **kwargs):
        users = User.objects.all()
        posts = Post.objects.all().order_by("-pub_date")
        comments = Comment.objects.all()
        likes = Like.objects.all()

        context = {
            "users": users,
            "posts": posts,
            "likes": likes,
            "comments": comments
        }

        if request.user.is_authenticated:
            notifications = Notification.objects.filter(to_user__exact=request.user).order_by("-date")
            post_form = CreatePostForm(request.user)
            comment_form = PostCommentForm
            context["notifications"] = notifications
            context["comment_form"] = comment_form
            context["create_post_form"] = post_form
            return render(request, "base.html", context)
        return render(request, "base.html", context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        users = User.objects.all()
        post = Post.objects.all()
        comments = Comment.objects.all()
        likes = Like.objects.all()
        notifications = Notification.objects.filter(to_user__exact=request.user).order_by("-date")
        post_form = CreatePostForm(request.user, request.POST, request.FILES)
        comment_form = PostCommentForm(request.POST)
        try:
            if request.POST["text"] or request.FILES:
                if post_form.is_valid():
                    post_form.save()
            else:
                messages.info(request, "Please write or upload something...")
        except KeyError as e:
            print("Error: ", e)
        context = {
            "users": users,
            "notifications":notifications,
            "posts": post,
            "create_post_form": post_form,
            "comments": comments,
            "likes": likes,
            "comment_form": comment_form
        }
        return render(request, "base.html", context)

class EditPostView(UpdateView):
    model = Post
    fields = ["text","photo"]
    template_name = "pages/edit_post.html"
    context_object_name = "form"
    pk_url_kwarg = "post"
    success_url = reverse_lazy("main")

    def get_object(self):
        obj = super().get_object()
        if self.request.user == obj.owner:
            return super().get_object()
        raise PermissionDenied("Access denied")

    def get_queryset(self): 
        return super().get_queryset()

class DeletePostView(DeleteView):
    model = Post
    template_name = "pages/posts/post_confirm_delete.html"
    pk_url_kwarg = "post"
    success_url = reverse_lazy("main")

    def get_object(self):
        obj = super().get_object()
        if self.request.user == obj.owner:
            return super().get_object()
        raise PermissionDenied("Access denied")

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        back = self.request.META["HTTP_REFERER"]
        context["back"] = back
        return context

class ExplorePostView(generic.DetailView):
    model = Post
    template_name = "pages/explore_post.html"
    context_object_name = "post"
    pk_url_kwarg = "post_id"

class SearchView(ListView):
    model = User
    template_name = "pages/search_results.html"
    context_object_name = "search_results"
    paginate_by = 2

    def get_queryset(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        print(x_forwarded_for)
        query = self.request.GET.get("q","page")
        if self.request.user.is_anonymous:        
            object_list = User.objects.filter(
                Q(name__contains=query)|Q(email__contains=query)|Q(name__icontains=query)|Q(email__icontains=query)
            )
            return object_list      
        return User.objects.filter(
                Q(name__contains=query)|Q(email__contains=query)|Q(name__icontains=query)|Q(email__icontains=query)
            ).exclude(email=self.request.user.email)


class PostCommentView(View):
    @transaction.atomic
    def post(self,request,post_id,*args,**kwargs):
        comment_content = request.POST["comment-text"]
        post = Post.objects.get(post_id=post_id)
        comment = Comment.objects.filter(user__exact=request.user,post__exact=post)

        # check user has a commment for this post
        if len(comment) > 0:
            comment = Comment.objects.last()
            comment_created = False
        elif len(comment) == 0:
            comment = Comment.objects.create(user=request.user,post=post)
            comment_created = True
        child_comment = ChildComment.objects.create(content=comment_content)
        
        # checking comment is not created 
        if not comment_created:
            data = comment.comment.latest("date")
            data_dict = {}
            for d in data.child_comment.all():
                data_dict = dict((("user_id",d.user.id),("post_id",d.post_id)))
            if data_dict["user_id"] == request.user.id and str(data_dict["post_id"]) == post_id:
                comment.comment.add(child_comment)
            else:
                comment = Comment.objects.create(user=request.user,post=post)
                comment.comment.add(child_comment)
                comment.save()
        elif comment_created:
            comment.comment.add(child_comment)
        return redirect(reverse_lazy("main"))

class PostCommentArticleView(View):
    @transaction.atomic
    def post(self,request,pk,*args,**kwargs):
        path = request.META["HTTP_REFERER"]
        comment_content = request.POST["comment-text"]
        article = Article.objects.get(pk=pk)
        comment = CommentArticle.objects.filter(user__exact=request.user,article__exact=article)
        if len(comment) > 0:
            comment = CommentArticle.objects.last()
            comment_created = False
        elif len(comment) == 0:
            comment = CommentArticle.objects.create(user=request.user,article=article)
            comment_created = True
        child_comment = ChildCommentArticle.objects.create(content=comment_content)
        if not comment_created:
            data = comment.comment.latest("date")
            data_dict = {}
            for d in data.child_comment_article.all():
                data_dict = dict((("user_id",d.user.id),("article_id",d.article_id)))
            if data_dict["user_id"] == request.user.id and int(data_dict["article_id"]) == pk:
                comment.comment.add(child_comment)
            else:
                comment = CommentArticle.objects.create(user=request.user,article=article)
                comment.comment.add(child_comment)
                comment.save()
        elif comment_created:
            comment.comment.add(child_comment)
        return redirect(path)    

# Article section

class ShowArticles(ListView):
    model = Article
    template_name = "pages/articles/show_articles.html"
    context_object_name = "articles"

    def get_queryset(self):
        article = Article.objects.all().order_by("-likes_count")
        return article


class CreateArticleView(LoginRequiredMixin,CreateView):
    form_class = CreateArticleForm
    template_name = "pages/create_article.html"
    success_url = reverse_lazy("main")

    def handle_no_permission(self):
        print(super().handle_no_permission())
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["article_form"] = CreateArticleForm
        return context
    
    def form_valid(self, form):
        form.instance.author = self.request.user
        data = form.save()
        data.comments = data
        data.save()
        url = form.instance.get_absolute_url()
        return redirect(url)
    
    def form_invalid(self, form):
        data = form.errors.as_json()
        data_json = json.loads(data)
        message = data_json["body"][0]["message"]
        messages.error(self.request, message)
        return super().form_invalid(form)  
    
class ArticleDetailView(generic.detail.DetailView):
    model = Article
    template_name = "pages/article_detail.html"
    context_object_name = "article"
    query_pk_and_slug = True

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        article = Article.objects.get(pk=self.kwargs["pk"])
        if not self.request.user.is_anonymous:
            related_articles = Article.objects.filter(Q(headline__icontains=article.headline)|Q(body__icontains=article.headline)|Q(body__icontains=article.headline)|Q(body__icontains=article.body)|Q(headline__in=article.body)|Q(headline__in=article.headline)|Q(headline__istartswith=article.headline)|Q(headline__startswith=article.headline)|Q(author__exact=self.request.user)).exclude(pk__exact=article.pk)
            context["related_articles"] = related_articles
            return context
        related_articles = Article.objects.filter(Q(headline__icontains=article.headline)|Q(body__icontains=article.headline)|Q(body__icontains=article.headline)|Q(body__icontains=article.body)|Q(headline__in=article.body)|Q(headline__in=article.headline)|Q(headline__istartswith=article.headline)|Q(headline__startswith=article.headline))
        context["related_articles"] = related_articles
        return context

class EditArticleView(LoginRequiredMixin,UpdateView):
    model = Article
    fields = ["headline","body"]
    template_name = "pages/articles/edit_article.html"
    context_object_name = "form"
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("main")

    def get_object(self):
        obj = super().get_object()
        if self.request.user == obj.author:
            return super().get_object()
        raise PermissionDenied("Access denied")

    def get_queryset(self): 
        return super().get_queryset()

class DeleteArticleView(LoginRequiredMixin,DeleteView):
    model = Article
    template_name = "pages/articles/article_confirm_delete.html"
    pk_url_kwarg = "article"
    success_url = reverse_lazy("main")

    def get_object(self):
        obj = super().get_object()
        if self.request.user == obj.author:
            return super().get_object()
        raise PermissionDenied("Access denied")

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        back = self.request.META["HTTP_REFERER"]
        context["article"] = obj.headline
        context["back"] = back
        return context

class LikeArticleView(View):
    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ip = x_forwarded_for
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def get(self,request,pk):
        redirect_url = request.META.get("HTTP_REFERER")

        if redirect_url:
            article = Article.objects.get(pk=pk)
            ip = self.get_client_ip()
            try:
                if request.user.is_authenticated:
                    like = article.likes.get(user=request.user,like=True)
                    article.likes.remove(like)
                    like.delete()
                else:
                    like = article.likes.get(anonymous_user=ip,like=True)
                    article.likes.remove(like)
                    like.delete()
            except Like.DoesNotExist:
                if request.user.is_authenticated:
                    like = Like.objects.create(user=request.user,like=True)
                    article.likes.add(like)
                else:
                    like = Like.objects.create(anonymous_user=ip,like=True)
                    article.likes.add(like)
            return redirect(redirect_url)
        raise PermissionDenied("Invalid url.")

# like a post
class LikePostView(View):

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')

        if x_forwarded_for:
            ip = x_forwarded_for
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip

    def get(self,request,*args,**kwargs):
        redirect_url = request.META.get("HTTP_REFERER")
        if redirect_url:
            post_id = kwargs["post_id"]
            ip = self.get_client_ip()
            post = Post.objects.get(post_id=post_id)
            try:
                if request.user.is_authenticated:
                    like = post.likes.get(user=request.user,like=True)
                    post.likes.remove(like)
                    like.delete()
                else:
                    like = post.likes.get(anonymous_user=ip,like=True)
                    post.likes.remove(like)
                    like.delete()
            except Like.DoesNotExist:
                if request.user.is_authenticated:
                    like = Like.objects.create(user=request.user,like=True)
                    post.likes.add(like)
                else:
                    like = Like.objects.create(anonymous_user=ip,like=True)
                    post.likes.add(like)

            return redirect(redirect_url)
        raise PermissionDenied("Invalid url.")
    def post(self,request,*args,**kwargs):
        pass

# Dashboard
class DashboardView(LoginRequiredMixin, View, ContextMixin):
    login_url = reverse_lazy("login")
    redirect_field_name = reverse_lazy("dashboard")

    def get(self, request, user,**kwargs):
        ctx = self.get_context_data()
        form = ChangeUserForm
        context = {
            "followers": ctx["followers"],
            "posts": ctx["posts"],
            "posts_count": ctx["posts_count"],
            "articles": ctx["articles"],
            "articles_count": ctx["articles_count"],
            "form":form,
        }
        return render(request, 'pages/dashboard.html', context)

    def post(self, request, *args, **kwargs):
        form = ChangeUserForm(request.POST,request.FILES)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            image = form.cleaned_data["image"]
            try:
                user = User.objects.get(email=request.user.email)
                if name is not None:
                    user.name = name
                    user.save()
                if len(email) > 0:
                    user.email = email
                    user.save()
                if image is not None:
                    user.image = image
                    user.save()
                messages.info(request,"Your changes are successfully changed")
            except Exception as e:
                print(e)
                messages.info(request,"This email is already exists")
                       
        ctx = self.get_context_data()
        context = {
            "followers": ctx["followers"],
            "posts": ctx["posts"],
            "posts_count": ctx["posts_count"],
            "articles": ctx["articles"],
            "articles_count": ctx["articles_count"],
            "form":form,
        }
        return render(request, "pages/dashboard.html",context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        current_user.refresh_from_db()
        context["followers"] = Follower.get_count(self.request.user)
        context["posts"] = Post.objects.filter(owner__exact=self.request.user)
        context["posts_count"] = Post.get_count(self.request.user)
        context["articles"] = Article.objects.filter(author__exact=self.request.user)
        context["articles_count"] = Article.get_count(author=self.request.user)
        
        return context


class UserProfileShowcaseView(View):
    def get(self, request, username, user_id, *args, **kwargs):
        user = User.objects.get(pk=user_id)
        posts = Post.objects.filter(owner=user).values().order_by("-pub_date")
        articles = Article.objects.filter(author=user)
        followed = True
        try:
            follower = Follower.objects.get(user=user,follower=request.user)
        except Follower.DoesNotExist:
            followed = False
        context = {
            "user": user,
            "posts": posts,
            "articles": articles,
            "followed": followed
        }
        return render(request, "pages/user_profile_showcase.html", context)

@csrf_exempt
def chat_api(request):
    room_id = None
    if request.method == "POST":
        data = request.POST.dict()
        data_json = json.loads(data["data"])
        request_user_id = data_json["requestUserId"]
        user_id = data_json["userId"]
        user,user_2 = User.objects.get(pk=request_user_id),User.objects.get(pk=user_id)
        try:
            room_id = ChatRoom.get_room_id(outgoing_user=user,incoming_user=user_2)
        except ChatRoom.DoesNotExist:
            pass
        print("ROOM ID: ",room_id)
        return JsonResponse({"room_id": room_id})
    return JsonResponse({"room_id": room_id})

class ChatRoomView(LoginRequiredMixin, View):
    @method_decorator(csrf_protect)
    def get(self, request, *args, **kwargs):
        context = {}
        message_users = ChatRoom.objects.filter(Q(outgoing=request.user)|Q(incoming=request.user))
        context["message_users"] = message_users
        try:
            if kwargs["user_id"]:
                user = User.objects.get(pk=kwargs["user_id"])
                messages = ChatRoom.objects.filter((Q(outgoing=request.user) & Q(incoming=user)) | (Q(outgoing=user) & Q(incoming=request.user)))
                context["messages"] = messages
                context["user"] = user
        except KeyError:
            print("KeyError occured")
        return render(request, "pages/chat.html", context)
    @method_decorator(csrf_protect)
    def post(self, request, *args, **kwargs):
        message = request.POST.get("message_text")
        context = {}
        try:
            if kwargs["user_id"]:
                user = User.objects.get(pk=kwargs["user_id"])
                context["user"] = user
        except KeyError:
            print("KeyError occured")
        return render(request, "pages/chat.html", context)
class Register(CreateView):
    form_class = UserCreationForm
    template_name = "auth/register.html"
    success_url = "/login"

    def form_valid(self, form):
        if form.is_valid():
            form.save(commit=True)
            messages.success(
                self.request, f"Account created for {form.cleaned_data.get('email')}")
        return super().form_valid(form)


class Login(View):
    def get(self, request, *args, **kwargs):
        context = {}
        context["form"] = UserLoginForm
        return render(request, "auth/login.html", context)

    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            try:
                user = authenticate(
                    request, email=form.cleaned_data["email"], password=form.cleaned_data["password"])
                login(request, user)
                return redirect("base:main")
            except Exception as e:
                print("error: ", e)
                messages.info(request, e.message)
        context = {
            "form": form
        }
        return render(request, "auth/login.html", context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_error"] = self.context
        return context


class FollowView(LoginRequiredMixin,View):

    def get_redirect_field_name(self):
        path = self.request.path
        return path

    def get(self, request, user_id,*args, **kwargs):
        path = request.META.get('HTTP_REFERER')
        user = User.objects.get(pk=user_id)
        print("[PATH]",dir(request),dir(request.session),request.session,request.COOKIES)
        try:
            follower = Follower.objects.get(user=user)
            followers = follower.follower.all()
            if request.user in followers:
                Follower.unfollow(user=user, follower=request.user)
            else:
                raise FollowerError("UserDoesNotExist")
        except (FollowerError,Follower.DoesNotExist):
            if not user == request.user:
                Follower.follow(user=user, follower=request.user)
        return redirect(path)


def logout_view(request):
    logout(request)
    return HttpResponse("<h3>You succesfully logged out.</h3> Login <a href='/'>Home</a>")


class UserPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = "auth/password_change.html"
    success_url = reverse_lazy("dashboard")


class UserPasswordResetView(LoginRequiredMixin, PasswordResetView):
    form_class = PasswordResetForm
    template_name = "auth/password_reset.html"
    success_url = reverse_lazy("password_reset_done")


class UserPasswordResetDoneView(LoginRequiredMixin, PasswordResetDoneView):
    template_name = "auth/password_reset_done.html"


class UserPasswordResetConfirmView(LoginRequiredMixin, PasswordResetConfirmView):
    form_class = UserSetPasswordForm
    template_name = "auth/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class UserPasswordResetCompleteView(LoginRequiredMixin, PasswordResetCompleteView):
    template_name = "auth/password_reset_complete.html"
