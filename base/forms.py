from django import forms
from django.forms import ModelForm
from .models import User, Post, Comment, Article, Appointment
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import ReadOnlyPasswordHashField, PasswordChangeForm, SetPasswordForm


class UserLoginForm(forms.Form):
    email = forms.CharField(label='Email')
    password = forms.CharField(
        label='Password', widget=forms.PasswordInput(attrs={'autocomplete': 'on'}))

PATIENT_CHOICES = (
    ("HEADACHE","Headache"),
    ("TEETHACHE","Teethache"),

)
class SurveyForm(forms.Form):
    patients = forms.MultipleChoiceField(choices=PATIENT_CHOICES,widget=forms.CheckboxSelectMultiple)

# https://www.sgu.edu/blog/medical/types-of-physicians-in-demand/
CATEGORIES = (
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

class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)
    categories = forms.ChoiceField(choices=CATEGORIES)
    class Meta:
        model = User
        fields = ['email', 'name', 'bio', 'image']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password2"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = '__all__'


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["old_password", "new_password1", "new_password2"]


class UserSetPasswordForm(SetPasswordForm):
    error_messages = {
        'password_mismatch': "Parollar to'g'ri kelmadi.",
    }
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False
    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )


class ChangeUserForm(forms.Form):
    name = forms.CharField(label="New Name", widget=forms.TextInput(
        attrs={'placeholder': 'Enter a new name'}), required=False)
    email = forms.EmailField(label="New email", widget=forms.EmailInput(
        attrs={'placeholder': 'Enter a new email...'}), required=False)
    image = forms.ImageField(label="New image", required=False)

class CreatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('owner', 'text', 'photo', 'video',)

    def __init__(self, user, *args, **kwargs):
        super(CreatePostForm, self).__init__(*args, **kwargs)
        self.fields["owner"].widget = forms.HiddenInput()
        self.fields["owner"].initial = user


class PostCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["post", "comment"]

    def __init__(self, *args, **kwargs):
        super(PostCommentForm, self).__init__(*args, **kwargs)
        #self.fields["user"].widget = forms.HiddenInput()
        #self.fields["user"].initial = user
        self.fields["post"].widget = forms.HiddenInput()
        # self.fields["post"].initial = post_id


class CreateArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["headline","body"]

class AppointmentForm(forms.Form):
    reason = forms.CharField(label="Reason",widget=forms.Textarea(attrs={"placeholder":"Write about your ache...",}),max_length=2048)
