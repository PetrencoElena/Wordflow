from typing import Any
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView, 
    DetailView, 
    CreateView,
    UpdateView,
    DeleteView,
    View
    )
from .models import Post, Comment
from .forms import CommentForm



class PostListView(ListView):  
    model = Post
    template_name = 'blog/home.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_posts'] = Post.objects.order_by('-date_posted')[:4]
        return context


class UserPostListView(ListView):  
    model = Post
    template_name = 'blog/user_posts.html'   # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_posts'] = Post.objects.order_by('-date_posted')[:4]
        return context



class PostDetailView(View):  
    template_name = 'blog/post_detail.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        content = request.POST.get('comment-content')

        if content:
            post = Post.objects.get(id=kwargs['pk'])
            Comment.objects.create(
                author=request.user,
                post=post,
                content=content
            )
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = {}
        post = Post.objects.get(id=kwargs['pk'])

        context['post'] = post
        context['comments'] = Comment.objects.filter(post=post)
        context['recent_posts'] = Post.objects.order_by('-date_posted')[:4]
        return context



class PostCreateView(LoginRequiredMixin, CreateView):  
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):  
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False



class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):  
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False



def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})

