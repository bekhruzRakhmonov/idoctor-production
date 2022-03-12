from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # users authentication and authoration
	path('users/',views.ListUsers.as_view(),name='users'),
	path('register/',views.CreateUser.as_view(),name="api-register"),
	path('token/',views.CustomTokenObtainPairView.as_view(),name="token_obtain_pair"),
	path('token/refresh/',TokenRefreshView.as_view(),name="token_refresh"),
    path('password-change/',views.UserPasswordChangeView.as_view(),name="password-change"),
    path('password-reset/',views.UserPasswordResetEmailView.as_view(),name="password-reset-email"),
    path('password-reset/<uuid:user_id>/',views.UserPasswordResetView.as_view(),name="password-reset"),

    # post
    path('get-post/',views.GetPost.as_view(),name="get-post"),
    path('get-post/<uuid:pk>/',views.GetPostById.as_view(),name="get-post-by-id"),
	path('create-post/',views.CreatePostView.as_view(),name="create-post"),
	path('get-comment/',views.GetComment.as_view(),name="get-comment"),
	path('get-comment/<int:pk>/',views.GetCommentById.as_view(),name="get-comment-by-id"),
	path('create-comment/',views.CreateComment.as_view(),name="create-comment"),

    # articel urls
    path('create-article/',views.CreateArticle.as_view(),name="create-article"),
    path('get-article/',views.GetArticle.as_view(),name="get-article"),
    path('get-article/<int:pk>/',views.GetArticleById.as_view(),name="get-article-by-id"),
    path('create-article-comment/',views.CreateArticleComment.as_view(),name="create-article-comment"),
    path('article-comments/',views.ArticleComments.as_view(),name='article-comments'),

    # like urls
    path('like-post/',views.LikePost.as_view(),name="like-post"),
    path('like-article/',views.LikeArticle.as_view(),name="like-article"),

    # following urls
    path('follow/',views.FollowView.as_view(),name="follow"),
]
