from pathlib import Path
from uuid import uuid4

from everett.manager import (
    ConfigEnvFileEnv,
    ConfigManager,
    ConfigOSEnv,
)

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
# use `repo_full_name` to include github owner in name
APP_NAME_TEMPLATE = config('APP_NAME_TEMPLATE', default='{repo_name}-{branch_name}')

# notifications stuff
# configure these if you want slack notifications
# see
SLACK_API_TOKEN = config('SLACK_API_TOKEN', raise_error=False)
SLACK_CHANNEL = config('SLACK_CHANNEL', raise_error=False)
