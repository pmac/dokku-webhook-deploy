from sh import git, pushd

from review_apps import dokku, settings


def get_repo_path(repo_owner, repo_name):
    return settings.REPOS_BASE_PATH / repo_owner / f'{repo_name}.git'


def update(data):
    repo_name = data['repository']['name']
    repo_owner = data['repository']['owner']['name']
    repo_url = data['repository']['clone_url']
    repo_path = get_repo_path(repo_owner, repo_name)
    if not repo_path.exists():
        repo_path.mkdir(parents=True)
        with pushd(repo_path):
            print(f'git clone')
            print(git.clone(repo_url, '.', bare=True, _err_to_out=True))
    else:
        with pushd(repo_path):
            print(git.fetch('origin', data['ref'], _err_to_out=True))


def push(data, app_name):
    repo_name = data['repository']['name']
    repo_owner = data['repository']['owner']['name']
    head_commit = data['head_commit']['id']
    repo_path = get_repo_path(repo_owner, repo_name)
    dokku_host = settings.SSH_DOKKU_HOST
    if not settings.DEPLOY_LOGS_BASE_PATH.exists():
        settings.DEPLOY_LOGS_BASE_PATH.mkdir()

    deploy_log_file = str(settings.DEPLOY_LOGS_BASE_PATH / f'{app_name}.txt')
    dokku.apps_create(app_name)
    with pushd(repo_path):
        git.push(f'{dokku_host}:{app_name}',
                 f'{head_commit}:refs/heads/master',
                 _err_to_out=True,
                 _out=deploy_log_file,
                 _bg=True)


