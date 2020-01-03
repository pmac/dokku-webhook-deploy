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
# the prefix of the branch names to deploy as demos
DEMO_BRANCH_PREFIX = config('DEMO_BRANCH_PREFIX', default='demo/')
# use `repo_full_name` to include github owner in name
APP_NAME_TEMPLATE = config('APP_NAME_TEMPLATE', default='{repo_name}-{branch_name}')
