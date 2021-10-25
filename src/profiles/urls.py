from django.urls import path
from . import views

app_name = "profiles"
urlpatterns = [
    path("me/", views.ShowProfile.as_view(), name="show_self"),
    path("me/edit/", views.EditProfile.as_view(), name="edit_self"),
    path("me/privacy/updatePrivacy", views.updatePrivacy, name="updatePrivacy"),
    path("me/privacy", views.PrivacyCenter.as_view(), name="privacyCenter"),
    path("me/submissions", views.Submissions.as_view(), name="submissions"),
    path("<slug:slug>/submissions", views.Submissions.as_view(), name="submissions"),
    path("me/bookmarks", views.Bookmarks.as_view(), name="bookmarks"),
    path("<slug:slug>/", views.ShowProfile.as_view(), name="show"),
    path("me/projects", views.projects, name="self_projects"),
    path("me/resources", views.resources, name="self_resources"),
    path("me/followed_projects", views.followedProjects, name="followed_projects"),
    path("me/saved_resources", views.savedResources, name="saved_resources"),
    path("me/organisations", views.organisations, name="self_organisations"),
]
