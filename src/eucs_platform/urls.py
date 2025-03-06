from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.views.decorators.cache import never_cache
from django.views.defaults import server_error
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from machina import urls as machina_urls
from rest_framework import permissions
import profiles.urls
import accounts.urls
import organisations.urls
import projects.urls
import resources.urls
import events.urls
import contact.urls
import digest.urls
import platforms.urls
import pages.urls
import blog.urls
import eucitizensciencetheme.urls
#import ecsa_integration.urls
import ckeditor_uploader.views
from . import views


schema_view = get_schema_view(
   openapi.Info(
      title="EUCS PLATFORM API",
      default_version='v1',
      description="This is the EUCS plaftorm API",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


def custom_server_error(request, *args, **kwargs):
    return server_error(request, template_name="500.html", *args, **kwargs)

handler500 = custom_server_error

# Personalized admin site settings like title and header
admin.site.site_title = "EU-Citizen.Science Site Admin"
admin.site.site_header = "EU-Citizen.Science Administration"


urlpatterns = [
    path("curated/", views.curated, name="curated"),
    path("home_autocomplete/", views.home_autocomplete, name="home_autocomplete"),
    path("", include(profiles.urls)),
    path("admin/", admin.site.urls),
    path("select2/", include("django_select2.urls")),
    path("", include(contact.urls)),
    path("", include(accounts.urls)),
    path("", include(organisations.urls)),
    path("", include(projects.urls)),
    path("", include(resources.urls)),
    path("", include(blog.urls)),
    path("", include(events.urls)),
    path("", include(digest.urls)),
    path("", include(platforms.urls)),
    path("", include(pages.urls)),
    path("", include(eucitizensciencetheme.urls)),
    #path("", include(ecsa_integration.urls)),
    path('summernote/', include('django_summernote.urls')),
    path('forum/', include(machina_urls)),
    path('getTopicsResponded', views.getTopicsResponded, name='getTopicsResponded'),
    path('getForumResponsesNumber', views.getForumResponsesNumber, name='getForumResponsesNumber'),
    re_path(r'^i18n/', include('django.conf.urls.i18n')),
    re_path(r'^reviews/', include('reviews.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #url(r'^api/auth/', include('djoser.urls')),
    re_path(r'^api/auth/', include('djoser.urls.authtoken')),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^openid/', include('oidc_provider.urls', namespace='oidc_provider')),
    re_path(r"^upload/", ckeditor_uploader.views.upload, name="ckeditor_upload"),
    re_path(r"^browse/", never_cache(ckeditor_uploader.views.browse), name="ckeditor_browse",),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
]

# User-uploaded files like profile pics need to be served in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Include django debug toolbar if DEBUG is on
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
