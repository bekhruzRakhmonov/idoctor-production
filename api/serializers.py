from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from base.models import User,Comment,CommentArticle,ChildCommentArticle,ChildComment,Post,Article,Follower
from base.exceptions import FollowerError
from django.core import serializers as dj_serializers
import json

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__' #["id","email","name","bio","image","password"]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self,validated_data):
        user = User(email=validated_data["email"],name=validated_data["name"],bio=validated_data["bio"],image=validated_data["image"])
        user.set_password(validated_data["password"])
        user.save()
        # User(**validated_data)
        return user

class UserPasswordChangeSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True,required=True,max_length=30)
    new_password1 = serializers.CharField(write_only=True,required=True,max_length=30)
    new_password2 = serializers.CharField(write_only=True,required=True,max_length=30)

    class Meta:
        model = User
        fields = ["old_password","new_password1","new_password2"]

    def validate(self,data):
        old_password = data["old_password"]
        new_password1 = data["new_password1"]
        new_password2 = data["new_password2"]

        context = self.context
        user = context["request"].user
        
        # https://stackoverflow.com/questions/62890249/assertionerror-validate-should-return-the-validated-data

        if user.check_password(old_password):
            if new_password2 != new_password1:
                raise serializers.ValidationError({"new_password2": "Passwords didn't match!"})
        else:
            raise serializers.ValidationError({"old_password": "Wrong password!"})

        return data

    def update(self,instance,validated_data):
        new_password = validated_data.get("new_password1")
        instance.set_password(new_password)
        instance.save()
        return instance

    # should add to_representation here

class UserPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True,required=True)
    
    def to_internal_value(self,data):
        useful_data = {}
        useful_data["email"] = data["email"]
        return super().to_internal_value(useful_data)
    
    def to_representation(self,instance):
        ret = super().to_representation(instance)
        instance = dict(instance)
        ret["email"] = instance["email"]
        ret["user_id"] = instance["user_id"]
        return ret

    def validate(self,data):
        email = data["email"]
        try:
            user = User.objects.get(email=email)
            data["user_id"] = user.pk
            print(data)
            return data
        except User.DoesNotExist:
            raise serializers.ValidationError({"email":"This email does not exist."})

class UserPasswordResetSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True,required=True,max_length=30)
    password2 = serializers.CharField(write_only=True,required=True,max_length=30)

    class Meta:
        model = User
        fields = ["password1","password2"]
    
    def validate(self,data):
        pswd1 = data["password1"]
        pswd2 = data["password2"]

        if pswd2 != pswd1:
            raise serializers.ValidationError("Passwords didn't match.")

        return data
    
    def update(self,instance,validated_data):
        new_password = validated_data["password1"]
        instance.set_password(new_password)
        instance.save()
        return instance

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls,user):
        token = super().get_token(user)

        # username = dj_serializers.serialize("json",User.objects.get(email=user.email).name)
        # person = serializers.serialize("json", Person.objects.get(id = 25), fields = ("firstName", "middleName", "lastName"))
        # print(user_json)
        # Adding custom token
        token["user"] = user.email,user.name,user.bio

        return token

class CommentSerializer(serializers.ModelSerializer):
    url = serializers.CharField(source="get_absolute_url",read_only=True)
    uri = serializers.HyperlinkedIdentityField(view_name="get-comment-by-id")
    class Meta:
        model = Comment
        fields = '__all__'

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["text","post","likes"]

class CreateAndUpdatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["owner","text","photo"]
        
    def to_internal_value(self, data):
        useful_data = {}
        useful_data["text"],useful_data["photo"] = data.get("text",None),data.get("photo",None)
        print("Useful Data:",useful_data)
        return super().to_internal_value(useful_data)

    def to_representation(self,instance):
        representation = super().to_representation(instance)
        representation["username"] = instance.owner.name
        comments = Comment.objects.filter(post=instance)
        elements = []
        for comment in comments:
            for child_comment in comment.comment.all():
                for el in child_comment.child_comment.all():
                    elements.append((el.user.email,(child_comment.content,child_comment.date)))
        representation["comments"] = elements        
        return representation
    
    def update(self,instance,validated_data):
        instance.text = validated_data.get("text")
        instance.photo = validated_data.get("photo")

    def __init__(self,owner,*args,**kwargs):
        super(PostSerializer,self).__init__(*args,**kwargs)
        self.fields["owner"].default = owner
        self.fields["owner"].required = False


class ChildCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildComment
        fields = ["content"]

class CreateCommentSerializer(serializers.Serializer):
    post_id = serializers.UUIDField(required=True)
    content = serializers.CharField(max_length=255,required=True)

    def to_internal_value(self,data):
        useful_data = {}
        try:
            useful_data["post_id"],useful_data["content"] = data["post_id"],data["content"]
            return super().to_internal_value(useful_data)
        except KeyError:
            return super().to_internal_value(data)

class ArticleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="get-article-by-id")
    class Meta:
        model = Article
        fields = ["id","url","headline","body","date","likes"]
    
    def to_representation(self,instance):
        print(instance)
        representation = super().to_representation(instance)
        comments = CommentArticle.objects.filter(article=instance)
        elements = []
        for comment in comments:
            for child_comment in comment.comment.all():
                for el in child_comment.child_comment_article.all():
                    elements.append((el.user.email,(child_comment.content,child_comment.date)))
        representation["comments"] = elements
        return representation

class ArticleCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentArticle
        fields = ["user","article","comment"]


class CreateArticleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="get-article-by-id")
    class Meta:
        model = Article
        fields = ["url","author","headline","body"]
    
    def to_representation(self,instance):
        representation = super().to_representation(instance)
        representation["author"] = instance.author.name
        return representation

    def update(self,instance,validated_data):
        instance.headline = validated_data.get("headline")
        instance.body = validated_data.get("body")
        instance.save()
        return instance

    def __init__(self,author,*args,**kwargs):
        super(CreateArticleSerializer,self).__init__(*args,**kwargs)
        self.fields["author"].default = author
        self.fields["author"].required = False

class ArticleCommentSerializer(serializers.Serializer):
    article_id = serializers.IntegerField()
    content = serializers.CharField(max_length=255)

    def to_internal_value(self,data):
        useful_data = {}
        try:
            useful_data["article_id"] = data["article_id"]
            useful_data["content"] = data["content"]
            return super().to_internal_value(useful_data)
        except KeyError:
            return super().to_internal_value(data)

class LikePostSerializer(serializers.Serializer):
    post_id = serializers.UUIDField()

    def to_internal_value(self,data):
        useful_data = {}
        useful_data["post_id"] = data["post_id"]
        return super().to_internal_value(useful_data)

class LikeArticleSerializer(serializers.Serializer):
    article_id = serializers.IntegerField()

class FollowerSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(write_only=True,required=True)
    
    def save(self):
        user_id = self.validated_data["user_id"]
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")
        follower_user = self.context["request"].user
        try:
            follower = Follower.objects.get(user=user)
            followers = follower.follower.all()
            if follower_user in followers:
                Follower.unfollow(user=user, follower=follower_user)
            else:
                raise FollowerError("UserDoesNotExist")
        except (FollowerError,Follower.DoesNotExist):
            if not follower_user == user:
                Follower.follow(user=user, follower=follower_user)

