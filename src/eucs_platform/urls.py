from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path, re_path
from django.conf.urls import url
from django.views.decorators.cache import never_cache
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

# Personalized admin site settings like title and header
admin.site.site_title = "EU-Citizen.Science Site Admin"
admin.site.site_header = "EU-Citizen.Science Administration"


urlpatterns = [
    path("", views.home, name="home"),
    path("all/", views.all, name="all"),
    path("curated/", views.curated, name="curated"),
    path("imprint/", views.imprint, name="imprint"),
    path("terms/", views.terms, name="terms"),
    path("privacy/", views.privacy, name="privacy"),
    path("faq/", views.faq, name="faq"),
    path("subscribe/", views.subscribe, name="subscribe"),
    path("moderation/", views.moderation, name="moderation"),
    path("criteria/", views.criteria, name="criteria"),
    path("moderation_quality_criteria", views.moderation_quality_criteria, name="moderation_quality_criteria"),
    path("translations/", views.translations, name="translations"),
    path("call/", views.call, name="call"),
    path("policy_maker_event_2021/", views.policy_maker_event_2021, name="policy_maker_event_2021"),
    path("final_launch/", views.final_launch, name="final_launch"),
    path("home_autocomplete/", views.home_autocomplete, name="home_autocomplete"),
    path("development/", views.development, name="development"),
    path("about/", views.AboutPage.as_view(), name="about"),
    path("policy_brief/", views.policy_brief, name="policy_brief"),
    path("users/", include(profiles.urls)),
    path("admin/", admin.site.urls),
    path("select2/", include("django_select2.urls")),
    path("", include(contact.urls)),
    path("", include(accounts.urls)),
    path("", include(organisations.urls)),
    path("", include(projects.urls)),
    path("", include(resources.urls)),
    path('', include('blog.urls')),
    path("", include(events.urls)),
    path("", include(digest.urls)),
    path("", include(platforms.urls)),
    path('summernote/', include('django_summernote.urls')),
    path('forum/', include(machina_urls)),
    path('getTopicsResponded', views.getTopicsResponded, name='getTopicsResponded'),
    path('getForumResponsesNumber', views.getForumResponsesNumber, name='getForumResponsesNumber'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^reviews/', include('reviews.urls')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/auth/', include('djoser.urls')),
    url(r'^api/auth/', include('djoser.urls.authtoken')),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    url(r'^openid/', include('oidc_provider.urls', namespace='oidc_provider')),
    re_path(r"^upload/", ckeditor_uploader.views.upload, name="ckeditor_upload"),
    re_path(r"^browse/", never_cache(ckeditor_uploader.views.browse), name="ckeditor_browse",),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]

# User-uploaded files like profile pics need to be served in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Include django debug toolbar if DEBUG is on
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
