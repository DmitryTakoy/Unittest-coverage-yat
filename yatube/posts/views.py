from django.shortcuts import render, get_object_or_404, redirect
from .forms import CommentForm, PostForm
from .models import Comment, Follow, Post, Group, User
from django.contrib.auth.decorators import login_required
from .utils import my_paginator


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('author').all()
    page_obj = my_paginator(request, posts)
    context = {
        'page_obj': page_obj,
        'posts': posts,
        'title': 'whatsapp'}
    return render(request, template, context)


def group_posts(request, slug):
    grouper = get_object_or_404(Group, slug=slug)
    posts = grouper.groups.all().select_related('group')
    page_obj = my_paginator(request, posts)
    context = {
        'page_obj': page_obj,
        'group': grouper,
        'posts': posts}
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author').all()
    posts_counter = posts.count()
    page_obj = my_paginator(request, posts)
    follows = Follow.objects.filter(
        user=request.user.pk
    ).filter(author=author).exists()
    context = {
        'page_obj': page_obj,
        'posts_counter': posts_counter,
        'author': author,
        'following': follows,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    cnt = Post.objects.filter(author=post.author).count()
    comments = Comment.objects.filter(post_id=post_id)
    form = CommentForm(request.POST)
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'cnt': cnt,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(request.POST,
                        files=request.FILES,
                        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()  # post.save()
            return redirect("posts:profile", request.user)
    form = PostForm(request.POST,
                    files=request.FILES,
                    )
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    if not post.author == request.user:
        return redirect('posts:post_detail',
                        post_id,
                        )
    form = PostForm(request.POST,
                    files=request.FILES,
                    instance=post,
                    )
    if form.is_valid() and request.method == 'POST':
        # form = PostForm(request.POST,
        #                instance=post,
        #                files=request.FILES or None,
        #                )
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'is_edit': is_edit,
        'post': post}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = my_paginator(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    # follows = Follow.objects.filter(user=request.user)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
        return redirect('posts:profile', username)
    return redirect('posts:profile', username)
    # if author.not in follows:
    #    following = True
    #    context = {'following': following}
    #    return context
    # following = True
    # context = {'following': following}
    # return render(request, template)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    author = get_object_or_404(User, username=username)
    Follow.objects.get(author=author.id).delete()
    return redirect('posts:profile', username)
    # if request.user != author:
    #    Follow.objects.delete(
    #        user = request.user,
    #        author = author,
    #    )
    # return redirect('posts:profile', username)
