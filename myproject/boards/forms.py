from django import forms
from .models import Topic, Post

class NewTopicForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'What is on your mind?'}
        ),
        max_length=4000,
        help_text='The max length of the text is 4000.'
    )
    photo = forms.FileField()
    
    class Meta:
        model = Topic
        fields = ['subject', 'message', 'photo']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', ]