from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView

from .forms import SignUpForm
from .models import Favorite, Follow


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class UserUpdateView(ListView):
    model = User
    template_name = 'my_account.html'
    context_object_name = 'user'
    # paginate_by = 20

    def get_queryset(self):
        self.user = get_object_or_404(User, pk=self.request.user.pk)
        queryset = self.user
        return queryset

    def get_context_data(self, **kwargs):
        kwargs['projects'] = self.user.topics
        kwargs['stars'] = Favorite.user_stars(self.user)
        kwargs['follows'] = Follow.user_followed(self.user)
        kwargs['is_self'] = True
        kwargs['is_followed'] = True
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        if 'new-email' in request.POST:
            user.email = request.POST.get('new-email')
        if 'password1' in request.POST:
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
                user.set_password(password1)
        user.save()
        account_url = reverse('my_account')
        return redirect(account_url)

'''
class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True
        kwargs['topic'] = self.topic
        kwargs['star'] = False
        if self.request.user.is_authenticated():
            # print(self.user)
            # print(type(self.user))
            # print(self.topic)
            # print(type(self.topic))
            kwargs['star'] = Favorite.is_star(self.user, self.topic)
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        if self.request.user.is_authenticated():
            self.user = User.objects.get(pk=self.request.user.pk)
        queryset = self.topic.posts.order_by('created_at')
        return queryset
        
@login_required
def favorite(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
    user = get_object_or_404(User, pk=request.user.pk)
    if Favorite.is_star(user, topic):
        Favorite.unstar(user, topic)
    else:
        Favorite.star(user, topic)
    return redirect(topic_url)
'''

@login_required
def follow(request, user_pk):
    user = get_object_or_404(User, pk=request.user.pk)
    followed_user = get_object_or_404(User, pk=user_pk)
    if Follow.is_followed(user, followed_user):
        Follow.unfollow(user, followed_user)
    else:
        Follow.follow(user, followed_user)
    user_url = reverse('user_account', kwargs={'user_pk': user_pk})
    return redirect(user_url)


class UserListView(ListView):
    model = User
    template_name = 'my_account.html'
    context_object_name = 'user'

    def get_queryset(self):
        self.user = get_object_or_404(User, pk=self.kwargs.get('user_pk'))
        queryset = self.user
        return queryset

    def get_context_data(self, **kwargs):
        kwargs['projects'] = self.user.topics
        kwargs['stars'] = Favorite.user_stars(self.user)
        kwargs['follows'] = Follow.user_followed(self.user)
        kwargs['is_self'] = False
        kwargs['is_followed'] = Follow.is_followed(self.request.user, self.user)
        # if self.request.user.is_authenticated():
        #     kwargs['is_self'] = False
        return super().get_context_data(**kwargs)




