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

from .forms import NewTopicForm, PostForm, NewLabForm, NewBlogForm, NewOverflowForm, NewJoinForm, NewQuitForm
from .models import Board, Post, Topic, Delegation
from accounts.models import Favorite, Letter
from sensitive import DFAFilter
from method import paragraph_dividing

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
        kwargs['staffs'] = self.topic.staffs.all()
        kwargs['button'] = 0 # 未登录：0，未发信：1，已发信：2，已同意：3
        if self.request.user.is_authenticated():
            # print(self.user)
            # print(type(self.user))
            # print(self.topic)
            # print(type(self.topic))
            if not self.user.pk == self.topic.starter.pk:
                kwargs['button'] = 1
                # if (Letter.is_letter(self.user, self.topic.starter, self.topic, 0) or Letter.is_letter(self.user, self.topic.starter, self.topic, 1)) and (not Delegation.is_delegation(self.topic, self.user)):
                if not Delegation.is_delegation(self.topic, self.user):
                    letter_list = list()
                    if self.topic.board.name == '个人创意':
                        letter_list = Letter.objects.filter(from_user=self.user, to_user=self.topic.starter, topic=self.topic, kind=0)
                    elif self.topic.board.name == '实验室':
                        letter_list = Letter.objects.filter(from_user=self.user, to_user=self.topic.starter,
                                                            topic=self.topic, kind=1)
                    flag = True
                    for letter in letter_list:
                        if not letter.handle:
                            flag = False
                    if not flag: # 有未处理的信件
                        kwargs['button'] = 2
                elif Delegation.is_delegation(self.topic, self.user):
                    kwargs['button'] = 3
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
            delegation = Delegation.objects.create(topic=topic, user=request.user)
            delegation.save()
            Post.objects.create(
                message=paragraph_dividing(DFAFilter.filter(form.cleaned_data.get('message'))),
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
            post.message = paragraph_dividing(DFAFilter.filter(post.message))
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


@login_required
def join(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    joined = Delegation.is_delegation(topic, request.user)
    if request.method == 'POST':
        if 'search_submit' in request.POST:
            search_content = request.POST['search_input']
            url = reverse('search', kwargs={'pk': search_content})
            return redirect(url)
        if not joined:
            form = NewJoinForm(request.POST)
            if form.is_valid():
                if topic.board.name == '个人创意':
                    letter = Letter.objects.create(from_user=request.user, to_user=topic.starter, kind=0, topic=topic,
                                                   read=False, handle=False)
                    letter.message = '亲爱的 ***' + topic.starter.username + '*** 你好，我想要参与开发你发起的 ***' + topic.subject + '*** 项目。\r\n\r\n' + '***我加入的原因是***：\r\n\r\n' + \
                                     form.cleaned_data.get(
                                         '加入原因') + '\r\n\r\n***我的技能有***：\r\n\r\n' + form.cleaned_data.get('我的技能') + \
                                     '\r\n\r\n希望能得到你的同意！'
                    letter.save()
                elif topic.board.name == '实验室':
                    letter = Letter.objects.create(from_user=request.user, to_user=topic.starter, kind=1, topic=topic,
                                                   read=False, handle=False)
                    letter.message = '尊敬的 ***' + topic.starter.username + '*** 同学你好，我想要加入 ***' + topic.subject + '*** 实验室。\r\n\r\n' + '***我加入的原因是***：\r\n\r\n' + \
                                     form.cleaned_data.get(
                                         '加入原因') + '\r\n\r\n***我的技能有***：\r\n\r\n' + form.cleaned_data.get('我的技能') + \
                                     '\r\n\r\n希望能得到你的同意！'
                    letter.save()
                topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
                return redirect(topic_url)
        else:
            form = NewQuitForm(request.POST)
            if form.is_valid():
                if topic.board.name == '个人创意':
                    letter = Letter.objects.create(from_user=request.user, to_user=topic.starter, kind=4, topic=topic,
                                                   read=False, handle=False)
                    letter.message = '亲爱的 ***' + topic.starter.username + '*** 你好，很遗憾，我不能再担任你 ***'+ topic.subject + '*** 项目的开发团队的一员。\r\n\r\n' + \
                        '***我退出的原因是***：\r\n\r\n' + form.cleaned_data.get('退出原因') + '\r\n\r\n希望能得到你的同意！'
                    letter.save()
                elif topic.board.name == '实验室':
                    letter = Letter.objects.create(from_user=request.user, to_user=topic.starter, kind=5, topic=topic,
                                                   read=False, handle=False)
                    letter.message = '尊敬的 ***' + topic.starter.username + '*** 同学你好，我想要退出 ***' + topic.subject + '*** 实验室。\r\n\r\n' + \
                                     '***我退出的原因是***：\r\n\r\n' + form.cleaned_data.get('退出原因') + '\r\n\r\n希望能得到你的同意！'
                    letter.save()
                topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
                return redirect(topic_url)

    else:
        if not joined:
            form = NewJoinForm()
        else:
            form = NewQuitForm()
    return render(request, 'join.html', {'topic': topic, 'form': form})


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
        post.message = paragraph_dividing(DFAFilter.filter(post.message))
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


    def post(self, request, *args, **kwargs):
        if 'search_submit' in request.POST:
            search_content = request.POST['search_input']
            url = reverse('search', kwargs={'pk':search_content})
            return redirect(url)
        # print(dir(super(PostUpdateView, self).post()))

        return super(PostUpdateView, self).post(self, request, *args, **kwargs)

