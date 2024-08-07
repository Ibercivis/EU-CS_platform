from .models import Footer, Main, TopBar
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
        response.context_data['platform_name'] = Main.objects.first().platform_name
        print(TopBar.objects.all())
        return response
    
class FooterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_template_response(self, request, response):
        response.context_data['footer'] = Footer.objects.first()
        print('middleware footer')
        return response