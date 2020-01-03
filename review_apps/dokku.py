from io import StringIO
from uuid import uuid4

from everett.manager import parse_env_file
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


def config_set(app_name, env_file):
    env_data = parse_env_file(env_file)
    configs = []
    for k, v in env_data.values():
        if v == '{uuid}':
            v = str(uuid4())

        configs.append(f'{k}={v}')

    dokku('config:set', '--no-restart', app_name, *configs)
