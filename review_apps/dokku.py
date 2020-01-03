from datetime import datetime
from io import StringIO
from textwrap import dedent
from uuid import uuid4

from everett.manager import parse_env_file
from sh import pushd, ssh, ErrorReturnCode
from sh.contrib import git

from review_apps import settings


dokku = ssh.bake(settings.SSH_DOKKU_HOST)


def apps_list():
    apps = StringIO(str(dokku('apps:list')))
    return [app.strip() for app in apps if not app.startswith('===')]


def apps_create(app_name):
    if app_name in apps_list():
        return

    dokku('apps:create', app_name)


def config_set(app_name, env_file):
    env_data = parse_env_file(env_file)
    configs = []
    for k, v in env_data.items():
        if v == '{uuid}':
            v = str(uuid4())

        configs.append(f'{k}={v}')

    if configs:
        dokku('config:set', '--no-restart', app_name, *configs)


def get_repo_path(repo_owner, repo_name):
    return settings.REPOS_BASE_PATH / repo_owner / f'{repo_name}.git'


def update_repo(data):
    repo_name = data['repository']['name']
    repo_owner = data['repository']['owner']['name']
    repo_url = data['repository']['clone_url']
    repo_path = get_repo_path(repo_owner, repo_name)
    if not repo_path.exists():
        repo_path.mkdir(parents=True)
        with pushd(repo_path):
            git.clone(repo_url, '.', bare=True, _err_to_out=True)
    else:
        with pushd(repo_path):
            git.fetch('origin', data['ref'], _err_to_out=True)


def push_repo(data, app_name):
    apps_create(app_name)
    repo_name = data['repository']['name']
    repo_owner = data['repository']['owner']['name']
    head_commit = data['head_commit']['id']
    repo_path = get_repo_path(repo_owner, repo_name)
    dokku_host = settings.SSH_DOKKU_HOST
    if not settings.DEPLOY_LOGS_BASE_PATH.exists():
        settings.DEPLOY_LOGS_BASE_PATH.mkdir()

    deploy_log_file = settings.DEPLOY_LOGS_BASE_PATH / f'{app_name}.txt'
    dlfo = deploy_log_file.open('wb')
    dlfo.write(dedent(f"""\
        =====================================================
        Deployment:  {datetime.utcnow().isoformat()}
        Repository:  {data['repository']['full_name']}
        Branch name: {data['ref']}
        App name:    {app_name}
        Github user: {data['pusher']['name']}
        Commit:      {head_commit}
        =====================================================
    """).encode('utf-8'))
    with pushd(repo_path):
        try:
            config_file = StringIO(str(git.show(f'{head_commit}:.review-apps-config')))
        except ErrorReturnCode:
            config_file = None

        if config_file:
            config_set(app_name, config_file)

        git.push('--force',
                 f'{dokku_host}:{app_name}',
                 f'{head_commit}:refs/heads/master',
                 _err_to_out=True,
                 _out=dlfo,
                 _bg=True)
