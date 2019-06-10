from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.contrib import messages

from .forms import NewTopicForm, PostForm, NewLabForm, NewBlogForm, NewOverflowForm
from .models import Board, Post, Topic
from accounts.models import Favorite
from sensitive import DFAFilter

from fuzzywuzzy import fuzz, process

class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'

    def post(self, request, *args, **kwargs):
        if 'search_submit' in request.POST:
            search_content = request.POST['search_input']
            url = reverse('search', kwargs={'pk':search_content})
            home_url = reverse('home')
            return redirect(url)

def search(request, pk):
    topic_out = list()
    topic_set = Topic.objects.all()
    show_list = list()
    for topic in topic_set:
        ratio_subject = fuzz.partial_ratio(pk, topic.subject)
        ratio_describe = fuzz.partial_ratio(pk, topic.posts.all()[0].message)
        ratio = ratio_subject + 0.7 * ratio_describe
        if ratio > 40:
            topic_out.append((topic, ratio))
    # bubble bubble
    for i in range(len(topic_out)-1, 0, -1):
        for j in range(0, i):
            if topic_out[j+1][1] > topic_out[j][1]:
                temp = topic_out[j]
                topic_out[j] = topic_out[j+1]
                topic_out[j+1] = temp
    for topic in topic_out:
        show_list.append(topic[0])
    return render(request, 'search.html', {'show_list': show_list})

class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset
        
    def post(self, request, *args, **kwargs):
        if 'search_submit' in request.POST:
            search_content = request.POST['search_input']
            url = reverse('search', kwargs={'pk':search_content})
        return redirect(url)



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
        # if self.topic.starter.pk == self.user.pk:   #<-- from here
        #     kwargs['return_url'] = reverse('my_account')
        # else:
        kwargs['return_url'] = reverse('user_account', kwargs={'user_pk': self.topic.starter.pk})   #<--to here
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

    def post(self, request, *args, **kwargs):
        if 'search_submit' in request.POST:
            search_content = request.POST['search_input']
            url = reverse('search', kwargs={'pk':search_content})
        return redirect(url)

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



@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        if 'search_submit' in request.POST:
            search_content = request.POST['search_input']
            url = reverse('search', kwargs={'pk':search_content})
            return redirect(url)

        # if 'subject' in request.POST:
        #     subject_clean = DFAFilter.filter(request.POST['subject'])
        # if 'teachers' in request.POST:
        #     subject_clean = DFAFilter.filter(request.POST['teachers'])
        # if 'direction' in request.POST:
        #     subject_clean = DFAFilter.filter(request.POST['direction'])

        if board.name == '个人创意':
            form = NewTopicForm(request.POST, request.FILES)
        elif board.name == '博客专区':
            form = NewBlogForm(request.POST, request.FILES)
        elif board.name == '实验室':
            form = NewLabForm(request.POST, request.FILES)
        else: # 溢出专区
            form = NewOverflowForm(request.POST, request.FILES)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.photo = request.FILES['photo']
            # filting sensitive words
            topic.subject = DFAFilter.filter(topic.subject)
            topic.teachers = DFAFilter.filter(topic.teachers)
            topic.direction = DFAFilter.filter(topic.direction)
            topic.save()
            Post.objects.create(
                message=DFAFilter.filter(form.cleaned_data.get('message')),
                topic=topic,
                created_by=request.user
            )
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)

    else:
        if board.name == '个人创意':
            form = NewTopicForm()
        elif board.name == '博客专区':
            form = NewBlogForm()
        elif board.name == '实验室':
            form = NewLabForm()
        else: # 溢出专区
            form = NewOverflowForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        if 'search_submit' in request.POST:
            search_content = request.POST['search_input']
            url = reverse('search', kwargs={'pk':search_content})
            return redirect(url)

        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.message = DFAFilter.filter(post.message)
            post.updated_at = timezone.now()
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        # if 'search_submit' in form:
        #     print('in form')
        #     search_content = form['search_input']
        #     url = reverse('search', kwargs={'pk': search_content})
        #     return redirect(url)
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.message = DFAFilter.filter(post.message)
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


    def post(self, request, *args, **kwargs):
        if 'search_submit' in request.POST:
            search_content = request.POST['search_input']
            url = reverse('search', kwargs={'pk':search_content})
            return redirect(url)
        # print(dir(super(PostUpdateView, self).post()))

        return super(PostUpdateView, self).post(self, request, *args, **kwargs)

