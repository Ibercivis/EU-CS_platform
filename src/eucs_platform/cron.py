from django_cron import CronJobBase, Schedule
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

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
                
                