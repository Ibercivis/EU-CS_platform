from .models import Footer, Main, TopBar
from django.template.response import TemplateResponse
import logging

logger = logging.getLogger(__name__)

class TopBarMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if isinstance(response, TemplateResponse):
            print(TopBar.objects.all())
            response.context_data['topbar_items'] = TopBar.objects.all()
            response.context_data['platform_name'] = Main.objects.first().platform_name
        return response
    
class FooterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_template_response(self, request, response):
        # do this only if the response is a TemplateResponse
        if isinstance(response, TemplateResponse):
            response.context_data['footer'] = Footer.objects.first()
        return response

class ThemeSelectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        print("here")
    
    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if isinstance(response, TemplateResponse):
            response.context_data['theme'] = 'eucitizensciencetheme'
            print('Theme selected: eucitizensciencetheme')
        return response