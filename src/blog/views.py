from django.views import generic
from django.shortcuts import render, get_object_or_404
from .models import Post

class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-sticky', '-created_on')
    template_name = 'blog.html'


def post_detail(request,year,month,day,slug):
    post = get_object_or_404(Post, slug=slug, status=1)
    return render(request,'post_detail.html',{'post':post})


def post_review(request, pk):
    return render(request, 'post_review.html', {'postID': pk})
