from slacker import Slacker

from review_apps import settings


SLACK_CLIENT = None
STATUSES = {
    'default': ':sparkles:',
    'shipped': ':ship:',
    'succeeded': ':tada:',
    'deleted': ':boom:',
    'failed': ':rotating_light:',
    'warning': ':warning:',
}


def slack_client():
    global SLACK_CLIENT
    token = settings.SLACK_API_TOKEN
    if not token:
        return

    if not SLACK_CLIENT:
        SLACK_CLIENT = Slacker(token)

    return SLACK_CLIENT


def notify(user, app_name, status):
    slack = slack_client()
    if slack is None:
        return

    protocol = 'https' if settings.APPS_LETSENCRYPT else 'http'
    app_url = f'{protocol}://{app_name}.{settings.APPS_DOKKU_DOMAIN}'
    log_url = f'https://review-apps.{settings.APPS_DOKKU_DOMAIN}/deploy-logs/{app_name}.txt'
    status_emoji = STATUSES.get(status, STATUSES['default'])
    message = (f'{status_emoji} *{user}* *{status.upper()}*: '
               f'<{app_url}|{app_name}> | '
               f'<{log_url}|deploy log>')
    slack.chat.post_message(settings.SLACK_CHANNEL, message)
