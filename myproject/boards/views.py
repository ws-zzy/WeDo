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

from .forms import NewTopicForm, PostForm, NewLabForm, NewBlogForm, NewOverflowForm, NewJoinForm, NewQuitForm, NewGiveupForm, NewSubmitForm
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
    if request.method == 'POST':
        if 'search_submit' in request.POST:
            search_content = request.POST['search_input']
            url = reverse('search', kwargs={'pk':search_content})
            return redirect(url)
    for topic in topic_set:
        ratio_subject = fuzz.partial_ratio(pk, topic.subject)
        ratio_describe = 0
        if topic.posts.all():
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
    # self_topic = Topic.objects.get(pk=0)

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True
        kwargs['topic'] = self.topic
        kwargs['star'] = False
        kwargs['is_self'] = False
        # if self.topic.starter.pk == self.user.pk:   #<-- from here
        #     kwargs['return_url'] = reverse('my_account')
        # else:
        kwargs['return_url'] = reverse('user_account', kwargs={'user_pk': self.topic.starter.pk})   #<--to here
        kwargs['staffs'] = self.topic.staffs.all()
        kwargs['percent_blue'] = '0%'; kwargs['percent_green'] = '0%'; kwargs['percent_yellow'] = '0%'; kwargs['percent_red'] = '0%'
        if self.topic.state == 1:
            percent = self.topic.percent
            if percent <= 25:
                kwargs['percent_blue'] = str(percent) + '%'
            elif percent > 25 and percent <= 50:
                kwargs['percent_blue'] = '25%'
                kwargs['percent_green'] = str(percent - 25) + '%'
            elif percent > 50 and percent <= 75:
                kwargs['percent_blue'] = '25%'
                kwargs['percent_green'] = '25%'
                kwargs['percent_yellow'] = str(percent - 50) + '%'
            elif percent > 75 and percent <= 100:
                kwargs['percent_blue'] = '25%'
                kwargs['percent_green'] = '25%'
                kwargs['percent_yellow'] = '25%'
                kwargs['percent_red'] = str(percent - 75) + '%'
            else:
                kwargs['percent_blue'] = '25%'
                kwargs['percent_green'] = '25%'
                kwargs['percent_yellow'] = '25%'
                kwargs['percent_red'] = '25%'
        kwargs['button'] = 0 # 未登录：0，加入未发信：1，加入已发信：2，退出未发信：3，退出已发信：4
        kwargs['ok'] = 0 # 未登录或不是发起者：0，有未处理信件：1，无未处理信件：2，项目开始开发但未完成：3，项目开发完成：4，项目已交付审核：5，不显示
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
                        letter_list = Letter.objects.filter(from_user=self.user, to_user=self.topic.starter, topic=self.topic, kind=0).all()
                    elif self.topic.board.name == '实验室':
                        letter_list = Letter.objects.filter(from_user=self.user, to_user=self.topic.starter,
                                                            topic=self.topic, kind=1).all()
                    flag = True
                    for letter in letter_list:
                        if not letter.handle:
                            flag = False
                            break
                    if not flag: # 有未处理的信件
                        kwargs['button'] = 2
                elif Delegation.is_delegation(self.topic, self.user):
                    kwargs['button'] = 3
                    letter_list = list()
                    if self.topic.board.name == '个人创意':
                        letter_list = Letter.objects.filter(from_user=self.user, to_user=self.topic.starter,
                                                            topic=self.topic, kind=4).all() # 退团信
                    elif self.topic.board.name == '实验室':
                        letter_list = Letter.objects.filter(from_user=self.user, to_user=self.topic.starter,
                                                            topic=self.topic, kind=5).all() # 退实验室信
                    flag = True
                    for letter in letter_list:
                        if not letter.handle:
                            flag = False
                            break
                    if not flag:  # 有未处理的信件
                        kwargs['button'] = 4

            else:
                kwargs['is_self'] = True
                if self.topic.state == 1:
                    if self.topic.percent < 100: # 开发未完成
                        kwargs['ok'] = 3
                    else: # 开发完成
                        kwargs['ok'] = 4
                elif self.topic.state == 2:
                    kwargs['ok'] = 5
                elif self.topic.state == 0:
                    kwargs['ok'] = 2
                    letter_list = list()
                    if self.topic.board.name == '个人创意':
                        letter_list = Letter.objects.filter(to_user=self.user, topic=self.topic, kind=0).all()
                    elif self.topic.board.name == '实验室':
                        letter_list = Letter.objects.filter(to_user=self.user, topic=self.topic, kind=1).all()
                    flag = True
                    for letter in letter_list:
                        if not letter.handle:
                            flag = False
                            break
                    if not flag:  # 有未处理的信件
                        kwargs['ok'] = 1
            kwargs['star'] = Favorite.is_star(self.user, self.topic)

        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        if self.request.user.is_authenticated():
            self.user = User.objects.get(pk=self.request.user.pk)
        queryset = self.topic.posts.order_by('created_at')
        return queryset

    def post(self, request, *args, **kwargs):
        # if 'percent_submit' in request.POST:
        #     url = reverse('changepercent', self.topic.board.pk, self.topic.pk, request.POST['percent_input'])
        #     return redirect(url)
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
    topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    joined = Delegation.is_delegation(topic, request.user)
    if request.user.pk == topic.starter.pk: # 项目发起者不能申请
        return redirect(topic_url)
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
                                     '\r\n\r\n***我的联系方式是***：\r\n\r\n' + form.cleaned_data.get('联系方式') + '\r\n\r\n希望能得到你的同意！'
                    letter.save()
                elif topic.board.name == '实验室':
                    letter = Letter.objects.create(from_user=request.user, to_user=topic.starter, kind=1, topic=topic,
                                                   read=False, handle=False)
                    letter.message = '尊敬的 ***' + topic.starter.username + '*** 同学你好，我想要加入 ***' + topic.subject + '*** 实验室。\r\n\r\n' + '***我加入的原因是***：\r\n\r\n' + \
                                     form.cleaned_data.get(
                                         '加入原因') + '\r\n\r\n***我的技能有***：\r\n\r\n' + form.cleaned_data.get('我的技能') + \
                                     '\r\n\r\n***我的联系方式是***：\r\n\r\n' + form.cleaned_data.get('联系方式') + '\r\n\r\n希望能得到你的同意！'
                    letter.save()
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

@login_required
def changestate(request, pk, topic_pk):
    url = reverse('topic_posts', kwargs={'pk':pk, 'topic_pk':topic_pk})
    topic = Topic.objects.get(pk=topic_pk)
    if request.user.pk == topic.starter.pk and topic.state == 0: # 只有项目发起者可以改变状态，只有状态为0时可以改变状态
        topic.state += 1
        topic.save()
    return redirect(url)

@login_required
def changepercent(request, pk, topic_pk, percent):
    url = reverse('topic_posts', kwargs={'pk':pk, 'topic_pk':topic_pk})
    topic = Topic.objects.get(pk=topic_pk)
    if request.user.pk == topic.starter.pk and topic.state == 1: # 只有项目发起者可以改变进度，只有状态为1时可以改变进度
        if percent == '0':
            if topic.percent >= 5:
                topic.percent -= 5
                topic.save()
        elif percent == '1':
            if topic.percent <= 95:
                topic.percent += 5
                topic.save()
    print(topic.percent)
    return redirect(url)

@login_required
def giveup(request, pk, topic_pk):
    url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
    # print(url)
    topic = Topic.objects.get(pk=topic_pk)
    if not request.user.pk == topic.starter.pk: # 非项目发起者不能申请
        return redirect(url)
    if request.method == 'POST':
        if 'search_submit' in request.POST:
            search_content = request.POST['search_input']
            url = reverse('search', kwargs={'pk': search_content})
            return redirect(url)
        form = NewGiveupForm(request.POST)
        if form.is_valid():
            if topic.board.name == '个人创意':
                team = topic.staffs.all()
                # 发给所有团队成员
                for member in team:
                    if not member.pk == topic.starter.pk: # 不用发给自己
                        letter = Letter.objects.create(from_user=request.user, to_user=member, kind=10, topic=topic,
                                                   read=False, handle=False)
                        letter.message = '亲爱的 ***' + member.username + '*** 你好。\r\n\r\n很遗憾，我们的 ***' + topic.subject + \
                                     '*** 项目无法再进行下去了。\r\n\r\n***原因如下***：\r\n\r\n' + form.cleaned_data.get(
                        '放弃原因') + '\r\n\r\n感谢你一直以来的付出，我们后会有期。'
                        letter.save()
                # 发给管理员
                letter = Letter.objects.create(from_user=request.user, to_user=User.objects.get(username='admin'), kind=10,
                                               topic=topic,
                                               read=False, handle=False)
                letter.message = '***' + topic.subject + \
                                 '*** 项目的管理员发起了解散团队请求。\r\n\r\n***原因如下***：\r\n\r\n' + form.cleaned_data.get('放弃原因')
                letter.save()
            elif topic.board.name == '实验室':
                team = topic.staffs.all()
                for member in team:
                    if not member.pk == topic.starter.pk:  # 不用发给自己
                        letter = Letter.objects.create(from_user=request.user, to_user=member, kind=11, topic=topic,
                                                   read=False, handle=False)
                        letter.message = '尊敬的 ***' + member.username + '*** 同学你好。\r\n\r\n很遗憾，我们的 ***' + topic.subject + \
                                     '*** 实验室不再继续开放。\r\n\r\n***原因如下***：' + form.cleaned_data.get(
                        '放弃原因') + '\r\n\r\n感谢你一直以来的付出，愿你前程似锦。'
                        letter.save()
                # 发给管理员
                letter = Letter.objects.create(from_user=request.user, to_user=User.objects.get(username='admin'), kind=11,
                                               topic=topic,
                                               read=False, handle=False)
                letter.message = '***' + topic.subject + \
                                 '*** 项目的管理员发起了关闭实验室请求。\r\n\r\n***原因如下***：\r\n\r\n' + form.cleaned_data.get('放弃原因')
                letter.save()
            return redirect(url)
    else:
        form = NewGiveupForm()
    print(url)
    return render(request, 'join.html', {'topic': topic, 'form': form} )

@login_required
def submit(request, pk, topic_pk):
    url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
    topic = Topic.objects.get(pk=topic_pk)
    if not request.user.pk == topic.starter.pk: # 非项目发起者不能申请
        return redirect(url)
    if request.method == 'POST':
        if 'search_submit' in request.POST:
            search_content = request.POST['search_input']
            url = reverse('search', kwargs={'pk': search_content})
            return redirect(url)
        form = NewSubmitForm(request.POST)
        if form.is_valid():
            if topic.board.name == '个人创意':
                team = topic.staffs.all()
                # 发给所有团队成员
                for member in team:
                    if not member.pk == topic.starter.pk:  # 不用发给自己
                        letter = Letter.objects.create(from_user=request.user, to_user=member, kind=12, topic=topic,
                                                   read=False, handle=False)
                        letter.message = '亲爱的 ***' + member.username + '*** 你好。\r\n\r\n我们的 ***' + topic.subject + \
                                     '*** 项目已经开发完成，正在交付审核！\r\n\r\n感谢你一直以来的付出！'
                        letter.save()
                # 发给管理员
                letter = Letter.objects.create(from_user=request.user, to_user=User.objects.get(username='admin'), kind=12,
                                               topic=topic,
                                               read=False, handle=False)
                letter.message = '***' + topic.subject + \
                                 '*** 项目的管理员发起了审核请求。\r\n\r\n***留言***：\r\n\r\n' + form.cleaned_data.get('留言')
                letter.save()
                topic.state += 1 # 进入审核状态
                topic.save()
            return redirect(url)
    else:
        form = NewSubmitForm()
    return render(request, 'join.html', {'topic': topic, 'form':form} )





