from django.shortcuts import render, get_object_or_404, redirect
from posts.models import Group, Follow, Post, Profile
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from .forms import CommentForm, PostForm, ProfileForm
from .utils import page_obj_create

User = get_user_model()


def index(request):
    keyword = request.GET.get('srch')
    if keyword:
        posts = (
            Post.objects.select_related('author', 'group').
            filter(
                Q(text__contains=keyword.lower())
                | Q(text__contains=keyword.upper())
                | Q(text__contains=keyword.capitalize())
            ).all()
        )
    else:
        posts = Post.objects.all()
    page_obj = page_obj_create(request, posts)
    context = {
        'page_obj': page_obj,
        'keyword': keyword,
    }
    template = 'posts/index.html'
    return render(request, template, context)


def group_posts(request, url):
    selected_group = get_object_or_404(Group, slug=url)
    group_posts = selected_group.posts.all()
    page_obj = page_obj_create(request, group_posts)
    context = {
        'page_obj': page_obj,
        'group': selected_group,
    }
    template = 'posts/group_list.html'
    return render(request, template, context)


def profile(request, username):
    selected_author = get_object_or_404(User, username=username)
    author_posts = selected_author.posts.all()
    page_obj = page_obj_create(request, author_posts)
    count = selected_author.posts.all().count()
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            user=request.user,
            author=selected_author
        ).exists()
    )
    context = {
        'page_obj': page_obj,
        'author': selected_author,
        'count': count,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    selected_post = get_object_or_404(Post, id=post_id)
    count = selected_post.author.posts.all().count()
    comments = selected_post.comments.all()
    form = CommentForm()
    context = {
        'post': selected_post,
        'user': request.user,
        'count': count,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def add_comment(request, post_id):
    selected_post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = selected_post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    selected_post = get_object_or_404(Post, id=post_id)
    if selected_post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=selected_post
    )
    if form.is_valid():
        selected_post.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'form': form,
        'post_id': post_id,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_delete(request, post_id):
    selected_post = get_object_or_404(Post, id=post_id)
    author = selected_post.author
    if author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    selected_post.delete()
    return redirect('posts:profile', username=author)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user).all()
    page_obj = page_obj_create(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author == request.user:
        return redirect('posts:profile', username=request.user)
    Follow.objects.get_or_create(
        user=request.user,
        author=author,
    )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author__username=username
    ) .delete()
    return redirect('posts:profile', username=username)


@login_required
def avatar_create(request, username):
    author = get_object_or_404(User, username=username)
    count = author.posts.all().count()
    if author != request.user:
        return redirect('posts:profile', username=username)
    if Profile.objects.filter(user=author).exists():
        selected_profile = get_object_or_404(Profile, user=author)
        form = ProfileForm(
            request.POST or None,
            files=request.FILES or None,
            instance=selected_profile,
        )
        if form.is_valid():
            selected_profile.save()
            return redirect('posts:profile', username=request.user)
    else:
        form = ProfileForm(
            request.POST or None,
            files=request.FILES or None,
        )
        if form.is_valid():
            new_profile = form.save(commit=False)
            new_profile.user = request.user
            new_profile.save()
            return redirect('posts:profile', username=request.user)
    context = {
        'author': author,
        'count': count,
        'form': form,
    }
    return render(request, 'posts/avatar.html', context)
