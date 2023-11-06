from .models import TopBar
import logging

logger = logging.getLogger(__name__)

class TopBarMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        response.context_data['topbar_items'] = TopBar.objects.all()
        return response