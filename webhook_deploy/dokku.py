import json
from datetime import datetime
from io import StringIO
from textwrap import dedent
from uuid import uuid4

from everett.manager import parse_env_file
from sh import pushd, ssh, ErrorReturnCode
from sh.contrib import git

from webhook_deploy import settings

SSH_CONNECT_STRING = f'{settings.SSH_DOKKU_USER}@{settings.SSH_DOKKU_HOST}'

dokku = ssh.bake('-tp', settings.SSH_DOKKU_PORT, SSH_CONNECT_STRING, '--')


def apps_list():
    apps = StringIO(str(dokku('apps:list')))
    return [app.strip() for app in apps if not app.startswith('===')]


def apps_create(app_name):
    try:
        dokku('apps:create', app_name)
    except ErrorReturnCode:
        # app already exists
        pass


def apps_destroy(app_name):
    dokku('apps:destroy', app_name, force=True)


def config_set(app_name, app_json, log_file):
    log_file.write('=======================\n')
    if not app_json:
        log_file.write('No app.json file found\n')
        log_file.write('=======================\n')
        return

    try:
        data = json.loads(app_json)
    except json.JSONDecodeError:
        log_file.write('JSON decoding error\n')
        log_file.write('=======================\n')
        return

    if 'env' not in data:
        log_file.write('No configuration to set\n')
        log_file.write('=======================\n')
        return

    configs = []
    for k, v in data['env'].items():
        if isinstance(v, dict):
            if 'value' in v:
                v = v['value']
            elif 'generator' in v:
                if v['generator'] in ['secret', 'uuid']:
                    v = str(uuid4())
            else:
                continue

        configs.append(f'{k}={v}')

    if configs:
        log_file.write('Setting app configuration variables:\n')
        log_file.write(', '.join(data['env'].keys()) + '\n')
        log_file.write('=======================\n')
        dokku('config:set', '--no-restart', app_name, *configs)
    else:
        log_file.write('No configuration to set\n')
        log_file.write('=======================\n')


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
            git.clone(repo_url, '.', bare=True)
    else:
        with pushd(repo_path):
            git.fetch('origin', data['ref'])


def push_repo(data, app_name):
    repo_name = data['repository']['name']
    repo_owner = data['repository']['owner']['name']
    head_commit = data['head_commit']['id']
    repo_path = get_repo_path(repo_owner, repo_name)
    dokku_host = f'{SSH_CONNECT_STRING}:{settings.SSH_DOKKU_PORT}'
    if not settings.DEPLOY_LOGS_BASE_PATH.exists():
        settings.DEPLOY_LOGS_BASE_PATH.mkdir()

    deploy_log_file = settings.DEPLOY_LOGS_BASE_PATH / f'{app_name}.txt'
    with deploy_log_file.open('wb') as dlfo:
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
                app_json = str(git.show(f'{head_commit}:app.json'))
            except ErrorReturnCode:
                app_json = None

            config_set(app_name, app_json, dlfo)

            git.push('--force',
                     f'ssh://{dokku_host}/{app_name}',
                     f'{head_commit}:refs/heads/master',
                     _err_to_out=True,
                     _out=dlfo)
            if settings.APPS_LETSENCRYPT:
                dlfo.write(dedent(f"""\
                    ================================
                    Let's Encrypt: Add or renew cert
                    ================================
                """).encode('utf-8'))
                dokku('letsencrypt:auto-renew', app_name, _out=dlfo)
