from io import StringIO

from sh import ssh

from review_apps import settings


dokku_ssh = ssh.bake(settings.SSH_DOKKU_HOST)


def dokku(*cmds):
    return StringIO(str(dokku_ssh(*cmds)))


def apps_list():
    return [app.strip() for app in dokku('apps:list') if not app.startswith('===')]


def apps_create(app_name):
    if app_name in apps_list():
        return

    dokku('apps:create', app_name)
