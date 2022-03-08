from django.urls import path,re_path
from . import views
from . import errors
from django.utils.text import slugify
from urllib.parse import quote,unquote, quote_plus
import re

print(quote('query sdkjsdksdk dksndk'))

app_name = "base"

urlpatterns = [
	path('',views.Main.as_view(),name="main"),
	path('search_query/',views.SearchView.as_view(),name="search"),
	path('register/',views.Register.as_view(),name="register"),
	path('login/',views.Login.as_view(),name="login"),
	path('logout/',views.logout_view,name="logout"),
	path('password_change/',views.UserPasswordChangeView.as_view(),name="password_change_view"),
	path('password_reset/',views.UserPasswordResetView.as_view(),name="password_reset"),
	path('password_reset_done/',views.UserPasswordResetDoneView.as_view(),name="password_reset_done"),
	path('reset/<uidb64>/<token>',views.UserPasswordResetConfirmView.as_view(),name="password_reset_confirm"),
	path('password_reset_complete/',views.UserPasswordResetCompleteView.as_view(),name="password_reset_complete"),
	path('<slug:user>-<uidb64>/dashboard/',views.DashboardView.as_view(),name="dashboard"),
	path('comment/<str:post_id>/',views.PostCommentView.as_view(),name="post-comment-view"),
	path('comment-article/<int:pk>/',views.PostCommentArticleView.as_view(),name="article-comment-view"),
	path('like/<str:post_id>/',views.LikePostView.as_view(),name="like-post"),
	path('create-article/',views.CreateArticleView.as_view(),name="create-article"),
	path('articles/',views.ShowArticles.as_view(),name="articles"),
	path('article/<str:pk>/',views.ArticleDetailView.as_view(),name="article-detail"),
	path('article-edit/<int:pk>/',views.EditArticleView.as_view(),name="edit-article"),
	path('article-delete/<article>/',views.DeleteArticleView.as_view(),name="delete-article"),
	path('like-article/<int:pk>/',views.LikeArticleView.as_view(),name="like-article"),
	path('post-edit/<uuid:post><str:user_id>/',views.EditPostView.as_view(),name="edit-post"),
	path('post-delete/<uuid:post><str:user_id>/',views.DeletePostView.as_view(),name="delete-post"),
	path('posts/post-<uuid:post_id>/',views.ExplorePostView.as_view(),name="explore-post"),
	path('users/<str:username>/<str:user_id>/',views.UserProfileShowcaseView.as_view(),name="user-profile-showcase"),
	path('follow/<str:name>/<str:user_id>/',views.FollowView.as_view(),name="follow"),
	path('chat/',views.ChatRoomView.as_view(),name="chat-room"),
	path('chat/<str:user_id>/',views.ChatRoomView.as_view(),name="chat-room"),
	path('room/',views.chat_api,name="chat-api"),
]

# C:\Users\Admin\AppData\Local\Programs\Python\Python39\Lib\site-packages\django\contrib\auth
