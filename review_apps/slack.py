from slacker import Slacker

from review_apps import settings


SLACK_CLIENT = None
STATUSES = {
    'default': ':sparkles:',
    'shipped': ':ship:',
    'success': ':tada:',
    'failure': ':rotating_light:',
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


def notify(message, status=None, app_name=None, app_url=None, log_url=None):
    slack = slack_client()
    if slack is None:
        return

    status_emoji = STATUSES.get(status, STATUSES['default'])
    message = f'{status_emoji} *{status.upper()}*: {message}'
    if app_url:
        message += f' | <{app_url}|{app_name}>'
    if log_url:
        message += f' | <{log_url}|deploy log>'
    slack.chat.post_message(settings.SLACK_CHANNEL, message)
