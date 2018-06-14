from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models import MembershipType, Membership, LinkedInUser
from django.utils import timezone
import datetime
from django.conf import settings

User = get_user_model()


class Command(BaseCommand):

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print('first')
        pass

    def check_expired_user(self):
        users = User.objects.all()
        memberships = Membership.objects.all()

        expired_users = []
        expiring_users = []
        for membership in memberships:
            try:
                user = membership.user
                join_date = user.date_joined
                live_date = membership.membership_type.day_to_live
                now = timezone.now()
                expiring_date = join_date + datetime.timedelta(days=live_date-3)
                expired_date = join_date + datetime.timedelta(days=live_date)
                if now > expired_date:
                    self.send_three_day_email(user)
                elif now > expiring_date:
                    self.send_expired_email(user)
                else:
                    pass
            except Exception as e:
                print('------>', e)

    def send_three_day_email(self, user):
        subject = 'Getting started with {0}'.format(settings.SITE_TITLE)
        message = render_to_string('app/account_activate_expiring_email.html', {
            'current_date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'site_title': settings.SITE_TITLE,
            'user': user,
        })
        user.email_user(subject, message)
        pass

    def send_expired_email(self, user):
        subject = 'Getting started with {0}'.format(settings.SITE_TITLE)
        message = render_to_string('app/account_activate_expired_email.html', {
            'current_date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'site_title': settings.SITE_TITLE,
            'user': user,
        })
        user.email_user(subject, message)
        pass

    def delete_linkedin_user(self, user):
        linkedin_users = LinkedInUser(user=user)
        for linkedin_user in linkedin_users:
            linkedin_user.is_deleted = True
            linkedin_user.save()
        pass
