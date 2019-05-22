from django.db import models
from django.contrib.auth.models import User

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
