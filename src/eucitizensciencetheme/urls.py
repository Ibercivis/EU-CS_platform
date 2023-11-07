from django.urls import path, include
from django.conf.urls import url
from . import views

''' Paths of eucitizensciencetheme, in alphabetical order '''
urlpatterns = [
    path("about/", views.about, name="about"),
    path("all/", views.all, name="all"),
    path("call/", views.call, name="call"),
    path("call_ambassadors/", views.call_ambassadors, name="call_ambassadors"),
    path("criteria/", views.criteria, name="criteria"),
    path("development", views.development, name="development"),
    path("ecs_project_ambassadors/", views.ecs_project_ambassadors, name="ecs_project_ambassadors"),
    path("ecs_project/ambassadors", views.ecs_project_ambassadors, name="ecs_project_ambassadors"),
    path("faq/", views.faq, name="faq"),   
    path("final_event/", views.final_event, name="final_event"),
    path("final_launch/", views.final_launch, name="final_launch"),
    path('get_markers/', views.get_markers, name='get_markers'),
    path("imprint/", views.imprint, name="imprint"),
    path("moderation/", views.moderation, name="moderation"),
    path("moderation_quality_criteria/", views.moderation_quality_criteria, name="moderation_quality_criteria"),
    path("policy_brief/", views.policy_brief, name="policy_brief"),
    path("policy_maker_event_2021/", views.policy_maker_event_2021, name="policy_maker_event_2021"),
    path("privacy/", views.privacy, name="privacy"),
    path("projects_map/", views.projects_map, name="projects_map"),
    path("subscribe/", views.subscribe, name="subscribe"),
    path("terms/", views.terms, name="terms"),
    path("translations/", views.translations, name="translations"),
    


]