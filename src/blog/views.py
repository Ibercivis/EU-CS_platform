from django.views import generic
from django.shortcuts import render, get_object_or_404
from urllib.parse import urlencode
from django.conf import settings
from .models import Post


class PostList(generic.ListView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query_params = self.request.GET.copy()
        query_params.pop('page', None)
        context['query_params'] = urlencode(query_params)
        return context
    queryset = Post.objects.filter(status=1).order_by('-sticky', '-created_on')
    template_name = 'blog.html'
    paginate_by = '12'


def post_detail(request, year, month, day, slug):
    post = get_object_or_404(Post, slug=slug, status=1)
    return render(request, 'post_detail.html', {'post': post, "domain": settings.HOST})


def post_review(request, pk):
    return render(request, 'post_review.html', {'postID': pk})
