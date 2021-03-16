from django.db.models import Q
from django.core.mail import EmailMessage
from django_cron import CronJobBase, Schedule
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from machina.apps.forum_conversation.models import Topic, Post
from machina.apps.forum.models import Forum
from machina.apps.forum_member.models import ForumProfile
from django.template.loader import render_to_string

User = get_user_model()

class ExpiredUsersCronJob(CronJobBase):
    RUN_EVERY_MINS = 1440

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'eucs_platform.expired_users_cron_job'

    def do(self):
        users = User.objects.get_queryset().filter(is_active=False)
        N = 7
        date_N_days_ago = datetime.now() - timedelta(days=N)
        for user in users:
            if not user.is_active:
                if date_N_days_ago.timestamp() > user.date_joined.timestamp():
                    print("Deleting user " + str(user))
                    user.delete()
                else:
                    print("Not yet")

class NewForumResponseCronJob(CronJobBase):
    print("running messages cron")
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'eucs_platform.new_forum_response_cron_job'

    def do(self):
        this_hour = timezone.now()
        one_hour_before = this_hour + timedelta(minutes=-2)
        topics = Topic.objects.get_queryset().filter(status=0).filter(updated__range=(one_hour_before, this_hour))
        print(topics)
        print(this_hour)
        print(one_hour_before)
        for topic in topics:            
            owner = topic.poster_id
            user = User.objects.get(pk=owner)

            #Send email to owner
            mail_subject = 'EU-Citizen.Science - New forum message'
            slug = '' + topic.slug + '-' + str(topic.id)
            forum = get_object_or_404(Forum, id=topic.forum_id)
            forum_slug = forum.slug + '-' + str(forum.id)
            message = render_to_string('forum_emails/forum_answer.html', {'topic': topic, 'slug': slug, 'forum': forum_slug, "domain": settings.HOST})
            to_email = user.email
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.content_subtype = "html"
            email.send()
            print("email sent to"+str(to_email))


            users = User.objects.get_queryset().filter(~Q(pk=owner))

            for user in users:
                isSubscripted = topic in user.topic_subscriptions.all()
                if isSubscripted:
                    #Send email to subscriber
                    posts = Post.objects.get_queryset().filter(topic_id=topic.id,updated__range=(one_hour_before, this_hour))
                    for post in posts:
                        if user.id is not post.poster_id:
                            mail_subject = 'EU-Citizen.Science - New forum message'
                            slug = '' + topic.slug + '-' + str(topic.id)
                            forum = get_object_or_404(Forum, id=topic.forum_id)
                            forum_slug = forum.slug + '-' + str(forum.id)
                            message = render_to_string('forum_emails/forum_subscription_new_message.html', {'topic': topic, 'slug': slug, 'forum': forum_slug, "domain": settings.HOST})
                            to_email = user.email
                            email = EmailMessage(
                                        mail_subject, message, to=[to_email]
                            )
                            email.content_subtype = "html"
                            email.send()
                        else:
                            print("Do not send email")





            
                
                
