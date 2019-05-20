from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from .forms import SignUpForm
from .models import User, Favorite


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
class UserUpdateView(UpdateView):
    model = User
    fields = ('username', 'email', )
    template_name = 'my_account.html'
    # success_url = reverse_lazy('my_account')
    context_object_name = 'user'

    def get_object(self):
        return self.request.user

    # def get_context_data(self, **kwargs):
    #     kwargs['project'] = self.topic
    #     kwargs['stars'] = Fa
    #     return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        if 'new-name' in request.POST:
            user.username = request.POST.get('new-name')
        if 'password1' in request.POST:
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            if password1 == password2:
                user.set_password(password1)
        user.save()
        return render(request, 'my_account.html')
