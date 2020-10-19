from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from users.forms import User

from posts.models import Comment, Follow, Group, Post

from .forms import CommentForm, PostForm


@cache_page(20)
def index(request):
    """Render the main page and 10 latest posts per page."""
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
        )


def group_post(request, slug):
    """Render the group page and 10 posts per page."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'group.html',
        {'group': group, 'page': page, 'paginator': paginator},
        )


@login_required
def new_post(request):
    """Render new post page.

    Add new post in database if new post contains text.
    """
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form})


def post_view(request, username, post_id):
    """Render post page."""
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm()
    сomments = Comment.objects.filter(post=post_id)
    return render(
        request,
        'post.html',
        {
            'post': post,
            'author': post.author,
            'сomments': сomments,
            'form': form,
            },
        )


@login_required
def add_comment(request, username, post_id):
    """Adds text comment to post."""
    post = get_object_or_404(Post, author__username=username, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
        return redirect('post', username, post_id)
    return redirect('post', username, post_id)


def profile(request, username):
    """Render user profile page with 10 posts per page.

    Include athor block.
    """
    author = get_object_or_404(
        User.objects.prefetch_related('posts'),
        username=username,
        )
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = None
    if not request.user.is_anonymous or request.user.is_authenticated:
        following = Follow.objects.filter(
            user = request.user,
            author = author)
    return render(
        request, 'profile.html',
        {
            'author': author,
            'page': page,
            'paginator': paginator,
            'following': following,
            },
        )


@login_required
def post_edit(request, username, post_id):
    """Render edit post page.

    Change post text or/and group in database.
    """
    user = get_object_or_404(User, username=username)
    if request.user != user:
        return redirect('post', username, post_id)
    post = get_object_or_404(
        Post,
        pk=post_id,
        author__username=username,
        )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
        )
    if form.is_valid():
        post = form.save()
        return redirect('post', username, post_id)
    return render(request, 'new_post.html', {'form': form, 'post': post})


def page_not_found(request, exception):
    """Render 404 status page."""
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
        )


def server_error(request):
    """Render 500 status page."""
    return render(
        request,
        "misc/500.html",
        status=500,
        )


@login_required
def follow_index(request):
    """Render page with 10 following author posts per page."""
    latest = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(latest, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {'page': page, 'paginator': paginator},
        )


@login_required
def profile_follow(request, username):
    follower = request.user
    following = get_object_or_404(User, username=username)
    if follower != following:
        try:
            Follow.objects.create(user=follower, author=following)
        except IntegrityError:
            profile(request, username)
    return profile(request, username)


@login_required
def profile_unfollow(request, username):
    follower = request.user
    following = get_object_or_404(User, username=username)
    Follow.objects.get(user=follower, author=following).delete()
    return profile(request, username)
