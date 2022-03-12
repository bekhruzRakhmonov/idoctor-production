from django.http import Http404
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse,reverse_lazy
from django.conf import settings
import json
from rest_framework import authentication,permissions,status,reverse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView,CreateAPIView,ListAPIView,UpdateAPIView
from rest_framework.response import Response
from rest_framework import parsers
from django.core.serializers import serialize
from django.db.models import Q
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password
from base.models import User,Comment,ChildComment,Post,Article,CommentArticle,ChildCommentArticle,Like
from .serializers import UserSerializer,PostSerializer,CreateAndUpdatePostSerializer,CommentSerializer,CustomTokenObtainPairSerializer,CreateCommentSerializer,ArticleSerializer,CreateArticleSerializer,ArticleCommentSerializer,ArticleCommentsSerializer,LikePostSerializer,LikeArticleSerializer,UserPasswordChangeSerializer,UserPasswordResetEmailSerializer,UserPasswordResetSerializer, FollowerSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CreateUser(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # authentication_classes  = [authentication.BasicAuthentication]

    def post(self,request,*args,**kwargs):
        data = request.data
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data)

class GetPost(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def initial(self,request,*args,**kwargs):
        
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        self.format_kwarg = self.get_format_suffix(**kwargs)

        # Perform content negotiation and store the accepted info on the request
        neg = self.perform_content_negotiation(request)
        request.accepted_renderer, request.accepted_media_type = neg

        # Determine the API version, if versioning is in use.
        version, scheme = self.determine_version(request, *args, **kwargs)
        print(version)
        request.version, request.versioning_scheme = version, scheme

        # Ensure that the incoming request is permitted
        self.perform_authentication(request)
        self.check_permissions(request)
        self.check_throttles(request)

class CreateAndUpdatePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser,parsers.JSONParser]    

    def post(self,request,*args,**kwargs):
        stream = request.stream
        text = request.data.get("text",None)
        photo = request.data.get("photo",None)
        serializer = CreateAndUpdatePostSerializer(data=request.data,owner=request.user,context={"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.data,status=status.HTTP_400_BAD_REQUEST)


    def put(self,request,*args,**kwargs):
        queryset = Post.objects.all()
        serializer = CreateAndUpdatePostSerializer(queryset=queryset,data=request.data,owner=request.user,context={"request":request},many=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)

        return Response(serializer.data)

class CreateComment(CreateAPIView):
    serializer_class = CreateCommentSerializer
    def get_post(self,post_id):
        try:
            post = Post.objects.get(post_id__exact=post_id)
            return {"post":post,"response": Response(status=status.HTTP_200_OK)}
        except Post.DoesNotExist:
            return {"response": Response(status=status.HTTP_404_NOT_FOUND)}

    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post_id = request.data.get("post_id",None)
        content = request.data.get("content",None)

        #if not post_id == None and content == None:
        res = self.get_post(post_id)
        
        response = res.get("response")

        if response.status_code == 200:
            post = res.get("post")
            child_comment = ChildComment.objects.create(content=request.data["content"])
            comment = Comment.objects.filter(user__exact=request.user,post__exact=post)

            # check user has comment for this post
            if len(comment) > 0:
                comment = Comment.objects.last()
                created = True
            else:
                comment = Comment.objects.create(user=request.user,post=post)
                created = False
            if not created:
                # getting a latest comment
                try:
                    latest_comment = comment.comment.latest("date")
                    latest_comment_data = latest_comment.child_comment.last()
                    latest_comment_user,latest_comment_post = latest_comment_data.user,latest_comment_data.post
                    # check latest comment user is current user
                    if request.user == latest_comment_user:
                        comment.child_comment.add(child_comment)
                    else:
                        comment = Comment.objects.create(user=request.user,post=post)
                        comment.save()
                        comment.comment.add(child_comment)
                except ChildComment.DoesNotExist:
                    comment.comment.add(child_comment)
            elif created:
                comment.comment.add(child_comment)
            data = { 
                "user":{
                    "name": comment.user.name,
                    "email": comment.user.email,
                } ,
                "post": comment.post.text,
                "comments": [comment.content for comment in comment.comment.all()]
            }
            return Response(data,status=status.HTTP_201_CREATED)
        else:
            return Response({"error":"Post not found"},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data,status=status.HTTP_404_NOT_FOUND)
class GetComment(RetrieveAPIView):
    queryset = Comment.objects.all().order_by("-id")
    # renderer_classes = [TemplateHTMLRenderer]

    def get(self,request,format=None,*args,**kwargs):
        host = request.META["HTTP_HOST"]
        queryset = self.get_queryset()
        serializer = CommentSerializer(queryset,many=True,context={"request":request})
        # for q in range(len(queryset)):
           # serializer.data[q]["url"] = f"http://{host}{request.get_full_path()}{queryset[q].id}/"
        return Response(serializer.data)

class GetCommentById(APIView):
    def get_object(self,pk):
        try:
            comment = Comment.objects.get(pk=pk)
            return comment
        except Comment.DoesNotExist:
            return Http404
    def get(self,request,pk,*args,**kwargs):
        comment = self.get_object(pk)
        serializer = CommentSerializer(comment,many=False)
        return Response(serializer.data)

    def put(self,request,pk,format=None):
        comment = self.get_object(pk)
        serializer = CommentSerializer(comment,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)

class CreateArticle(CreateAPIView):
    serializer_class = CreateArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data,author=request.user)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        print("Headers",headers)
        return Response(serializer.data,status=status.HTTP_201_CREATED,headers=headers)
    
    def get_serializer(self,author=None,*args,**kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context",self.get_serializer_context())
        kwargs.setdefault("author", author)
        return serializer_class(*args,**kwargs)

class GetArticle(ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

class GetArticleById(RetrieveAPIView):   
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    def retrieve(self,request,*args,**kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class CreateArticleComment(CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = ArticleCommentSerializer

    def get_article(self,pk):
        try:
            article = Article.objects.get(pk__exact=pk)
            return {"article": article,"response": Response(status=status.HTTP_200_OK)}
        except Article.DoesNotExist:
            return {"response": Response(status=status.HTTP_404_NOT_FOUND)}
    
    #def get_serializer(self,*args,**kwargs):
     #   serializer_class = self.get_serializer_class()
      #  print("Serializer Class:",serializer_class)
       # return serializer_class(*args,**kwargs)

    def create(self,request,*args,**kwargs):
        serializer= self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        article_id = request.data.get("article_id",None)
        res = self.get_article(article_id)
        
        response = res.get("response")

        if response.status_code == 200:
            article = res.get("article")

            child_comment = ChildCommentArticle.objects.create(content=request.data["content"])
            comment = CommentArticle.objects.filter(user__exact=request.user,article__exact=article)

            # check user has comment for this post
            if len(comment) > 0:
                comment = CommentArticle.objects.last()
                created = True
            elif len(comment) == 0:
                comment = CommentArticle.objects.create(user=request.user,article=article)
                created = False
            print("Article created:",created)
            if not created:
                # getting a latest comment
                try:
                    latest_comment = comment.comment.latest("date")
                    latest_comment_data = latest_comment.child_comment_article.last()
                    latest_comment_user,latest_comment_post = latest_comment_data.user,latest_comment_data.post
                    # check latest comment user is current user
                    if request.user == latest_comment_user:
                        comment.comment.add(child_comment)
                    else:
                        comment = CommentArticle.objects.create(user=request.user,article=article)
                        comment.save()
                        comment.comment.add(child_comment)
                except ChildCommentArticle.DoesNotExist:
                    comment.comment.add(child_comment)
            elif created:
                comment.comment.add(child_comment)
            data = { 
                "user":{
                    "name": comment.user.name,
                    "email": comment.user.email,
                } ,
                "article": comment.article.body,
                "comments": [comment.content for comment in comment.comment.all()]
            }
            return Response(data,status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "Article not found"},status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data)
class ArticleComments(ListAPIView):
    queryset = CommentArticle.objects.all()
    serializer_class = ArticleCommentsSerializer

class LikePost(CreateAPIView):
    serializer_class = LikePostSerializer
    
    def get_post(self,post_id):
        try:
            post = Post.objects.get(post_id=post_id)
            return {"post": post,"response":Response(status=status.HTTP_200_OK)}
        except Post.DoesNotExist:
            return {"response":Response(status=status.HTTP_404_NOT_FOUND)}
    
    def create(self,request,*args,**kwargs):
        post_id = request.data.get("post_id",None)
        res = self.get_post(post_id)
        response = res.get("response")
        if not response.status_code == 404:
            post = res.get("post")
            try:
                like = post.likes.get(user=request.user,like=True)
                post.likes.remove(like)
                like.delete()
            except Like.DoesNotExist:
                like = Like.objects.create(user=request.user,like=True)
                post.likes.add(like)
            print(post)
            data = {
                    "post": {"text":post.text,"photo":post.photo.url},
                    "likes": post.likes.all().count()
            }
            return Response(data,status=status.HTTP_201_CREATED)
        return Response({"error":"POST not found"},status.HTTP_404_NOT_FOUND)


class LikeArticle(CreateAPIView):
    serializer_class = LikeArticleSerializer
    
    def get_article(self,article_id):
        try:
            article = Article.objects.get(pk=article_id)
            return {"article": article,"response":Response(status=status.HTTP_200_OK)}
        except Article.DoesNotExist:
            return {"response": Response(status=status.HTTP_404_NOT_FOUND)}
    
    def create(self,request,*args,**kwargs):
        article_id = request.data.get("article_id",None)
        res = self.get_article(article_id)
        response = res.get("response")
        if not response.status_code == 404:
            article = res.get("article")
            try:
                like = article.likes.get(user=request.user,like=True)
                article.likes.remove(like)
                like.delete()
            except Like.DoesNotExist:
                like = Like.objects.create(user=request.user,like=True)
                article.likes.add(like)
            data = {
                    "article": {"headline":article.headline,"body": article.body},
                    "likes": article.likes.all().count()
            }
            return Response(data,status=status.HTTP_201_CREATED)
        return Response({"error":"ARTICLE not found"},status.HTTP_404_NOT_FOUND)

class ListUsers(ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        q = self.request.query_params.get("q")
        queryset = User.objects.all()
        if q is not None:
            queryset = User.objects.filter(Q(name__icontains=q)|Q(email__icontains=q))
            return queryset
        return queryset

class UserPasswordChangeView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPasswordChangeSerializer

    def get_object(self):
        user = User.objects.get(pk=self.request.user.pk)
        return user

    def get_serializer(self,*args,**kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context",self.get_serializer_context())
        return serializer_class(*args,**kwargs)

class UserPasswordResetEmailView(APIView):

    def post(self,request,*args,**kwargs):
        serializer = UserPasswordResetEmailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_id = serializer.validated_data["user_id"]
            email = serializer.validated_data["email"]
            url = reverse_lazy("password-reset",kwargs={"user_id":user_id})
            subject, from_email, to = 'hello', 'bekhruzrakhmonov1@gmail.com', '{}'.format(email)
            text_content = 'This is too important message'
            html_content = '<h3>Welcome to our website !</h3>' + '<a href="%s%s">Login</a>' % (settings.DEFAULT_DOMAIN,url)
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, 'text/html')
            # msg.attach_file('./static/images/logo.png')
            msg.send()
            return Response(serializer.data)

        return Response(serializer.data)

class UserPasswordResetView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserPasswordResetSerializer
    lookup_url_kwarg = "user_id"

    def get_serializer(self,*args,**kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context",self.get_serializer_context())
        return serializer_class(*args,**kwargs)

class FollowView(APIView):
    permissions = [permissions.IsAuthenticated]

    def get_followers_count(self,user_id):
        try:
            user = User.objects.get(id=user_id)
            followers = Follower.get_count(user=user)
            return {"response": Response({"followers": followers},status=status.HTTP_200_OK)}
        except User.DoesNotExist:
            return {"response": Response(status=status.HTTP_404_NOT_FOUND)}

    def get(self,request):
        user_id = request.data.get("user_id",None)
        res = self.get_followers_count(user_id)
        
        response = res.get("response")

        if response.status_code == 200:
            followers = response.get("followers")
            return Resonse({"followers": followers})
        return response
    
    def post(self,request,*args,**kwargs):
        serializer = FollowerSerializer(data=request.data,context={"request":request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.validated_data,status=status.HTTP_201_CREATED)
        return Response(serializer.data,status=status.HTTP_400_BAD_REQUEST)
    
