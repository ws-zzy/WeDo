import math
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.db import models
from django.utils.html import mark_safe
from django.utils.text import Truncator

from markdown import markdown


class Board(models.Model):
    name = models.CharField(max_length=15, unique=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count()

    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by('-created_at').first()


class Topic(models.Model):
    subject = models.CharField(max_length=20)
    last_updated = models.DateTimeField(auto_now_add=True)
    board = models.ForeignKey(Board, related_name='topics', on_delete=models.CASCADE)
    starter = models.ForeignKey(User, related_name='topics', on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)
    photo = models.ImageField(null=True)
    direction = models.CharField(null=True, max_length=50)  # 实验室：研究方向；溢出专区：错误方面（java？django？c文件读写？）
    staff = models.PositiveIntegerField(null=True, default=0)  # 创意、实验室：当前团队人数
    teachers = models.CharField(null=True, max_length=50)  # 实验室：教师名单
    staffs = models.ManyToManyField(User, related_name='joins', through='Delegation')
    #TODO 技术博客源代码上传?

    def __str__(self):
        return self.subject

    def get_page_count(self):
        count = self.posts.count()
        pages = count / 20
        return math.ceil(pages)

    def has_many_pages(self, count=None):
        if count is None:
            count = self.get_page_count()
        return count > 6

    def get_page_range(self):
        count = self.get_page_count()
        if self.has_many_pages(count):
            return range(1, 5)
        return range(1, count + 1)

    def get_last_ten_posts(self):
        return self.posts.order_by('-created_at')[:10]


class Post(models.Model):
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, null=True, related_name='+', on_delete=models.CASCADE)

    def __str__(self):
        truncated_message = Truncator(self.message)
        return truncated_message.chars(50)

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))


class Delegation(models.Model):
    topic = models.ForeignKey(Topic, related_name='del_staffs', on_delete=models.CASCADE)
    user = models.ForeignKey(User,related_name='del_joins', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ' joins ' + self.topic.subject
