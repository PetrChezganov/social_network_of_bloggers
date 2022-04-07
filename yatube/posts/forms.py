from django import forms

from posts.models import Comment, Post, Profile


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        required = {'text': True}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        required = {'text': True}


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar',)
