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

class NewLabForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'What is on your mind?'}
        ),
        max_length=4000,
        help_text='The max length of the text is 4000.'
    )
    teachers = forms.CharField(
        # widget=forms.Textarea(
        #     attrs = {'rows': 2, 'placeholder': 'Who are your teachers? Please use \'space\' as separator between names.'}
        # ),
        # max_length=50
        help_text='Who are your teachers? Please use \'space\' as separator between names.'
    )
    direction = forms.CharField(
        # widget=forms.Textarea(
        #     attrs = {'rows': 2, 'placeholder': 'Please describe what are you doing.'}
        # ),
        # max_length=50
        help_text='Please describe what is your team doing now.'
    )
    photo = forms.FileField()

    class Meta:
        model = Topic
        fields = ['subject', 'teachers', 'direction', 'staff', 'message', 'photo']

class NewBlogForm(forms.ModelForm):
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


class NewOverflowForm(forms.ModelForm):
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
        fields = ['subject', 'direction', 'message', 'photo']

