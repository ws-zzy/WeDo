from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView
from django import forms

from .forms import SignUpForm
from .models import Favorite, Follow, Letter
from boards.models import Delegation, Topic


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


@login_required
def my_account(request):
    my_url = reverse('user_account', kwargs={'user_pk': request.user.pk})
    return redirect(my_url)


@login_required
def follow(request, user_pk):
    user_url = reverse('user_account', kwargs={'user_pk': user_pk})
    if not request.user.pk == user_pk: # 不能关注自己
        user = get_object_or_404(User, pk=request.user.pk)
        followed_user = get_object_or_404(User, pk=user_pk)
        if Follow.is_followed(user, followed_user):
            Follow.unfollow(user, followed_user)
        else:
            Follow.follow(user, followed_user)
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
        kwargs['me'] = self.request.user
        if self.request.user.is_authenticated():
            if self.request.user.pk == self.user.pk:
                kwargs['is_self'] = True
                kwargs['is_followed'] = False
            else:
                kwargs['is_self'] = False
                kwargs['is_followed'] = Follow.is_followed(self.request.user, self.user)
        else:
            kwargs['is_self'] = False
            kwargs['is_followed'] = False
        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        if 'search_submit' in request.POST:
            search_content = request.POST['search_input']
            url = reverse('search', kwargs={'pk':search_content})
            return redirect(url)

        user = get_object_or_404(User, pk=self.kwargs.get('user_pk'))
        
        if 'new-email' in request.POST:
            user.email = request.POST.get('new-email')
        if 'password1' in request.POST:
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
                    user.set_password(password1)
            # else:
            #     raise render(request, "my_account.html", {'user_pk': user.pk, "stderr": "用户名或密码不正确"})
        user.save()
        account_url = reverse('user_account', kwargs={'user_pk': user.pk})
        return redirect(account_url)


@login_required
def letter(request, user_pk):
    if request.method == 'POST':
        if 'search_submit' in request.POST:
            search_content = request.POST['search_input']
            url = reverse('search', kwargs={'pk': search_content})
            return redirect(url)
    send_letters = Letter.get_send_letters(request.user)
    u_r_letters = Letter.get_unread_receive_letters(request.user)
    a_r_letters = Letter.get_alread_receive_letters(request.user)
    return render(request, 'letter.html', {'send_letters': send_letters,
                                           'unread_receive_letters': u_r_letters,
                                           'alread_receive_letters': a_r_letters, 'user': request.user})


@login_required
def letter_read(request, user_pk, letter_pk):
    letter = Letter.objects.get(pk=letter_pk)
    if request.user.pk == letter.to_user.pk: # 只有收信人可以标记已读
        letter.read = True
        letter.save()
    return redirect(reverse('letter', kwargs={'user_pk': user_pk}))


@login_required
def letter_handle(request, user_pk, letter_pk):
    letter = Letter.objects.get(pk=letter_pk)
    if request.user.pk == letter.to_user.pk: # 只有收信人可以标记已处理
        letter.read = True
        letter.handle = True
        letter.save()
    return redirect(reverse('letter', kwargs={'user_pk': user_pk}))


@login_required
def accept(request, pk, topic_pk, letter_pk):
    topic = Topic.objects.get(pk=topic_pk)
    from_user = Letter.objects.get(pk=letter_pk).from_user
    to_user = Letter.objects.get(pk=letter_pk).to_user
    if request.user.pk == topic.starter.pk: # 只有项目发起人可以同意加入项目
        letter = Letter.objects.get(pk=letter_pk)
        letter.handle = True
        letter.read = True
        letter.save()
        Delegation.delegate(topic, from_user)
    return redirect(reverse('letter', kwargs={'user_pk': to_user.pk}))


@login_required
def allow(request, pk, topic_pk, letter_pk):
    topic = Topic.objects.get(pk=topic_pk)
    from_user = Letter.objects.get(pk=letter_pk).from_user
    to_user = Letter.objects.get(pk=letter_pk).to_user
    if request.user.pk == topic.starter.pk:  # 只有项目发起人可以同意离开项目
        letter = Letter.objects.get(pk=letter_pk)
        letter.handle = True
        letter.read = True
        letter.save()
        Delegation.undelegate(topic, from_user)
    return redirect(reverse('letter', kwargs={'user_pk': to_user.pk}))


@login_required
def acceptgiveup(request, pk, topic_pk, letter_pk):
    topic = Topic.objects.get(pk=topic_pk)
    # from_user = Letter.objects.get(pk=letter_pk).from_user
    to_user = Letter.objects.get(pk=letter_pk).to_user
    if request.user.username == 'admin': # 只有admin可以同意解散团队请求
        letter = Letter.objects.get(pk=letter_pk)
        letter.handle = True
        letter.read = True
        letter.save()
        team = topic.staffs.all()
        for member in team:
            Delegation.undelegate(topic, member)
        topic.state = 4
        topic.save()
    return redirect(reverse('letter', kwargs={'user_pk': to_user.pk}))
