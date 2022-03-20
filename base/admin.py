from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User,AnonymousUser,Article,Post,Like,Comment,ChildComment,CommentArticle,ChildCommentArticle,ChatMessage,ChatRoom,Follower,Notification
from .forms import UserCreationForm,UserChangeForm

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    
    list_display = ('id','email','name','bio','image',)
    list_filter = ('email',)
    fieldsets = (
        (None,{'fields':('email','password',)}),
        ('Personal info',{'fields':('name','bio','image','last_login',)}),
        ('Permissions',{'fields':('is_superuser','is_staff','is_active',)})
    )

    # add fieldsets
    add_fieldsets = (
        (None,{
            'classes': ('wide',),
            'fields': ('email','name','bio','image','is_superuser','is_active','is_staff','password1','password2'),
        }),
    )

    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

class CommentInLine(admin.TabularInline):
    model = Comment
    extra = 0

class PostAdmin(admin.ModelAdmin):
    inlines = [CommentInLine]
    list_display = ("owner","text", "photo",)
    ordering = ("pub_date",)

class CommentAdmin(admin.ModelAdmin):
    list_display = ("user","post",)

class ChildCommentAdmin(admin.ModelAdmin):
    list_display = ("content","date",)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ("from_user","to_user","notf_type",)

class ArticleAdmin(admin.ModelAdmin):
    list_display = ("author","headline","date",)

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("message","date",)

class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("room_id","outgoing","incoming",)

admin.site.register(User,UserAdmin)
admin.site.register(AnonymousUser)
admin.site.register(Article,ArticleAdmin)
admin.site.register(Post,PostAdmin)
admin.site.register(Like)
admin.site.register(Comment,CommentAdmin)
admin.site.register(ChildComment,ChildCommentAdmin)
admin.site.register(CommentArticle)
admin.site.register(ChildCommentArticle)
admin.site.register(ChatMessage,ChatMessageAdmin)
admin.site.register(ChatRoom,ChatRoomAdmin)
admin.site.register(Follower)
admin.site.register(Notification,NotificationAdmin)
admin.site.unregister(Group)
