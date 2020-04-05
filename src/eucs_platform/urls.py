from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.conf.urls import url
import profiles.urls
import accounts.urls
import projects.urls
import resources.urls
import contact.urls
from . import views

# Personalized admin site settings like title and header
admin.site.site_title = "Eucs_Platform Site Admin"
admin.site.site_header = "Eucs_Platform Administration"

urlpatterns = [
    path("", views.home, name="home"),
    path("results/", views.results, name="results"),
    path("curated/", views.curated,name="curated"),
    path("imprint/", views.imprint,name="imprint"),
    path("terms/", views.terms,name="terms"),
    path("privacy/", views.privacy,name="privacy"),
    path("faq/", views.faq,name="faq"),
    path("subscribe/", views.subscribe,name="subscribe"),
    path("moderation/", views.moderation,name="moderation"),
    path("home_autocomplete/", views.home_autocomplete,name="home_autocomplete"),
    path("development/", views.development,name="development"),
    path("about/", views.AboutPage.as_view(), name="about"),
    path("events/", views.EventsPage.as_view(), name="events"),
    path("users/", include(profiles.urls)),
    path("admin/", admin.site.urls),
    path("", include(contact.urls)),
    path("", include(accounts.urls)),
    path("", include(projects.urls)),
    path("", include(resources.urls)),
    path('', include('blog.urls')),
    path('summernote/', include('django_summernote.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^reviews/', include('reviews.urls')),

]

# User-uploaded files like profile pics need to be served in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Include django debug toolbar if DEBUG is on
if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]
