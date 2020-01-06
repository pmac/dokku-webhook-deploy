from pathlib import Path
from uuid import uuid4

from everett.manager import (
    ConfigEnvFileEnv,
    ConfigManager,
    ConfigOSEnv,
    ListOf,
)
from slugify import slugify

BASE_PATH = Path(__file__).parents[1]
REPOS_BASE_PATH = BASE_PATH / 'repos'
DEPLOY_LOGS_BASE_PATH = BASE_PATH / 'deploy-logs'


config = ConfigManager([
    # first check for environment variables
    ConfigOSEnv(),
    # then look in the .env file
    ConfigEnvFileEnv('.env'),
])


LOG_LEVEL = config('LOG_LEVEL', default='INFO')
SECRET_KEY = str(uuid4())
GITHUB_SECRET = config('GITHUB_SECRET', raise_error=False)
SSH_DOKKU_HOST = config('SSH_DOKKU_HOST', raise_error=False)
SSH_DOKKU_PORT = config('SSH_DOKKU_PORT', parser=int, default='22')
SSH_DOKKU_USER = config('SSH_DOKKU_USER', default='dokku')
APPS_DOKKU_DOMAIN = config('APPS_DOKKU_DOMAIN', default=SSH_DOKKU_HOST or '')
APPS_LETSENCRYPT = config('APPS_LETSENCRYPT', parser=bool, default='False')
# the prefix of the branch names to deploy as demos
DEMO_BRANCH_PREFIX = config('DEMO_BRANCH_PREFIX', default='demo/')
# default extra branch names to deploy
# can be overridden by repo specific config: `<owner>_<repo>_BRANCHES`
DEFAULT_DEPLOY_BRANCHES = config('DEFAULT_DEPLOY_BRANCHES', parser=ListOf(str), default='')
# use `repo_full_name` to include github owner in name
APP_NAME_TEMPLATE = config('APP_NAME_TEMPLATE', default='{repo_name}-{branch_name}')

# notifications stuff
# configure these if you want slack notifications
# see
SLACK_API_TOKEN = config('SLACK_API_TOKEN', raise_error=False)
SLACK_CHANNEL = config('SLACK_CHANNEL', raise_error=False)


def get_deploy_branches(repo_full_name):
    """
    Get repo specific branch list to deploy if configured.

    :return: list of branch names
    """
    env_var = slugify(repo_full_name).replace('-', '_').upper()
    env_var = f'{env_var}_BRANCHES'
    branches = config(env_var, parser=ListOf(str), default='')
    if not branches:
        branches = DEFAULT_DEPLOY_BRANCHES

    return branches
