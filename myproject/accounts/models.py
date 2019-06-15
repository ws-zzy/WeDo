from django.db import models
from django.contrib.auth.models import User
from django.utils.html import mark_safe
from markdown import markdown

from boards.models import Topic


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='follower', on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followed', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return f'{self.follower} follow {self.followed}'

    @staticmethod 
    def follow(from_user, to_user):
        Follow(follower=from_user,
               followed=to_user).save() #关注方法

    @staticmethod
    def unfollow(from_user, to_user):
        f = Follow.objects.filter(follower=from_user, followed=to_user).all()
        if f:
            f.delete() #取关

    @staticmethod
    def user_followed(from_user):
        followeders = Follow.objects.filter(follower=from_user).all()
        user_followed = []
        for followeder in followeders:
            user_followed.append(followeder.followed)
        return user_followed #得到from_user关注的人，返回列表

    @staticmethod
    def is_followed(from_user, to_user):
        f = Follow.objects.filter(follower=from_user, followed=to_user).all()
        if f:
            return True
        return False

class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='faverer', on_delete=models.CASCADE)
    project = models.ForeignKey(Topic, related_name='favered', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return f'{self.user} star {self.project}'

    @staticmethod 
    def star(user, project):
        Favorite(user=user,
                 project=project).save()

    @staticmethod
    def unstar(user, project):
        f = Favorite.objects.filter(user=user, project=project).all()
        if f:
            f.delete() #取关

    @staticmethod
    def is_star(user, project):
        f = Favorite.objects.filter(user=user, project=project).all()
        if f:
            return True
        return False

    @staticmethod
    def user_stars(user):
        projects = Favorite.objects.filter(user=user).all()
        stars = []
        for project in projects:
            stars.append(project.project)
        return stars


class Letter(models.Model):
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name='+', on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, related_name='send_letters', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='receive_letters', on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    handle = models.BooleanField(default=False)
    kind = models.PositiveIntegerField(default=0) # 0-入团申请 1-加入实验室申请 2-回复通知 3-回信 4-退团申请 5-退出实验室申请 10-解散项目团队 11-解散实验室 12-提交项目审核
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'A ' + str(self.kind) + ' Letter from ' + self.from_user.username + ' to ' + self.to_user.username

    @staticmethod
    def get_send_letters(user):
        send_letters = Letter.objects.filter(from_user=user).all()
        return send_letters

    @staticmethod
    def get_receive_letters(user):
        receive_letters = Letter.objects.filter(to_user=user).all()
        return receive_letters

    @staticmethod
    def get_unread_receive_letters(user):
        unread_receive_letters = Letter.objects.filter(to_user=user, read=False)
        return unread_receive_letters

    @staticmethod
    def get_alread_receive_letters(user):
        alread_receive_letters = Letter.objects.filter(to_user=user, read=True)
        return alread_receive_letters

    @staticmethod
    def is_letter(from_user, to_user, topic, kind):
        letter = Letter.objects.filter(from_user=from_user, to_user=to_user, topic=topic, kind=kind).all()
        if letter:
            return True
        return False

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))