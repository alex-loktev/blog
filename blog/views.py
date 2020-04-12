from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from .models import Post
from .forms import *
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count


class PostList(ListView):
    model = Post
    template_name = 'blog/PostList.html'
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 2


class PostDetail(View):
    def get(self, request, slug):
        post = Post.published.get(slug=slug)
        comments = post.comments.filter(active=True)
        form = CommentForm()
        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
        similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
        return render(request, 'blog/PostDetail.html',
                      {'post': post, 'form': form, 'comments': comments, 'similar_posts': similar_posts})

    def post(self, request, slug):
        post = Post.published.get(slug=slug)
        comments = post.comments.filter(active=True)
        form = CommentForm(request.POST)
        post_tags_ids = post.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
        similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            form = CommentForm()
        else:
            form = CommentForm()
        return render(request, 'blog/PostDetail.html',
                      {'post': post, 'form': form, 'comments': comments, 'similar_posts': similar_posts})


class PostTagsList(View):
    def get(self, request, tag_slug):
        tag = Tag.objects.get(slug=tag_slug)
        posts = Post.published.all().filter(tags=tag)
        return render(request, 'blog/PostList.html', {'tag': tag, 'posts': posts})


class PostShare(View):
    def get(self, request, post_id):
        form = EmailPostForm()
        return render(request, 'blog/PostShare.html', {'form': form})

    def post(self, request, post_id):
        post = Post.objects.get(id=post_id)
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = "from django blog: {}".format(cd['name'])
            message = "{}  {}".format(post_url, cd['comments'])
            send_mail(subject, message, 'loktev.lesha@gmail.com', [cd['to']])
            sent = True
        else:
            form = EmailPostForm()
            sent = False
        return render(request, 'blog/PostShare.html',  {'post': post, 'form': form, 'sent': sent})


class SearchPost(View):
    def get(self, request):
        form = SearchPostForm()
        return render(request, 'blog/PostSearch.html', {'form': form})

    def post(self, request):
        form = SearchPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            title = cd['title']
            posts = Post.published.filter(title__search=title)
        else:
            form = SearchPostForm()
        return render(request, 'blog/PostList.html', {'form': form, 'posts': posts, 'title': title})