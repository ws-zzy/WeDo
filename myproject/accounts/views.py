from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, reverse, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView

from .forms import SignUpForm
from .models import Favorite


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