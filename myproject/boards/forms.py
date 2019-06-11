# -*- coding:utf-8 -*-

from django import forms
from .models import Topic, Post

class NewTopicForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'What is on your mind?'}
        ),
        max_length=4000,
        help_text='最多输入4000字符。'
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
            attrs={'rows': 5, 'placeholder': '请输入实验室详细介绍。'}
        ),
        max_length=4000,
        help_text='最多输入4000字符。'
    )
    teachers = forms.CharField(
        # widget=forms.Textarea(
        #     attrs = {'rows': 2, 'placeholder': 'Who are your teachers? Please use \'space\' as separator between names.'}
        # ),
        # max_length=50
        help_text='请输入本实验室指导老师的名字（用空格分隔）。'
    )
    direction = forms.CharField(
        # widget=forms.Textarea(
        #     attrs = {'rows': 2, 'placeholder': 'Please describe what are you doing.'}
        # ),
        # max_length=50
        help_text='请简要描述本实验室研究方向。'
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
        help_text='最多输入4000字符。'
    )
    photo = forms.FileField()

    class Meta:
        model = Topic
        fields = ['subject', 'message', 'photo']


class NewOverflowForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': '请描述你的问题。'}
        ),
        max_length=4000,
        help_text='最多输入4000字符。'
    )
    photo = forms.FileField()

    class Meta:
        model = Topic
        fields = ['subject', 'direction', 'message', 'photo']


class NewJoinForm(forms.Form):
    加入原因 = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 2, 'placeholder': '请描述你想要加入本项目/实验室的原因。'}
        ),
        max_length=500,
        help_text='最多输入500字符。'
    )
    我的技能 = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 2, 'placeholder': '介绍一下你自己！'}
        ),
        max_length=500,
        help_text='最多输入500字符。'
    )

