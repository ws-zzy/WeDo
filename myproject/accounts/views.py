from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView
from django import forms

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

@login_required
def my_account(request):
    my_url = reverse('user_account', kwargs={'user_pk': request.user.pk})
    return redirect(my_url)

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




