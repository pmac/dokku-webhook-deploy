from io import StringIO

from sh import ssh

from review_apps import settings


dokku_ssh = ssh.bake(settings.SSH_DOKKU_HOST)


def dokku(cmd):
    return StringIO(str(dokku_ssh(cmd)))


def apps_list():
    return [app.strip() for app in dokku('apps:list') if not app.startswith('===')]


