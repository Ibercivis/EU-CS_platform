from django.urls import path
from . import views

app_name = "profiles"
urlpatterns = [
    path("users/me/", views.ShowProfile.as_view(), name="show_self"),
    path("users/me/edit/", views.EditProfile.as_view(), name="edit_self"),
    path("users/me/privacy/updatePrivacy", views.updatePrivacy, name="updatePrivacy"),
    path("users/me/privacy", views.PrivacyCenter.as_view(), name="privacyCenter"),
    path("users/me/submissions", views.Submissions.as_view(), name="submissions"),
    path("users/<slug:slug>/submissions", views.Submissions.as_view(), name="submissions"),
    path("users/me/bookmarks", views.Bookmarks.as_view(), name="bookmarks"),
    path("users/<slug:slug>/", views.ShowProfile.as_view(), name="show"),
    path("users/me/projects", views.projects, name="self_projects"),
    path("users/me/resources", views.resources, name="self_resources"),
    path("users/me/followed_projects", views.followedProjects, name="followed_projects"),
    path("users/me/organisations", views.organisations, name="self_organisations"),
    path("users/me/my_stats", views.MyStats.as_view(), name="mystats"),
    #path("users/", views.UsersSearch.as_view(), name="users"),
    path("users/", views.userSearch, name="users"),
    path("users/me/usersAutocompleteSearch", views.usersAutocompleteSearch, name="usersAutocompleteSearch")
]
