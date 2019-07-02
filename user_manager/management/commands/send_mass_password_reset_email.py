from django.core.management import BaseCommand

from user_manager.auth0utils import get_all_users, request_password_reset


class Command(BaseCommand):
    help = 'Send reset email to all users'

    def handle(self, *args, **options):
        users = get_all_users()
        users_with_errors = []
        emails_sent = 0

        for user in users:
            self.stdout.write(str(user))
            # result, status = request_password_reset(user['username'], user['email'])
            # if status == 200:
            #     emails_sent += 1
            # else:
            #     users_with_errors.append('{} - {}'.format(user, result))

        if len(users_with_errors) > 0:
            self.stdout.write('Could not send reset email to {} users'.format(len(users_with_errors)))
            for u in users_with_errors:
                self.stdout.write(u)
        self.stdout.write('{} email{} sent.'.format(emails_sent, '' if emails_sent == 1 else ''))
