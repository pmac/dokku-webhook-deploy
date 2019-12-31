from uuid import uuid4

from everett.manager import (
    ConfigEnvFileEnv,
    ConfigManager,
    ConfigOSEnv,
)


config = ConfigManager([
    # first check for environment variables
    ConfigOSEnv(),
    # then look in the .env file
    ConfigEnvFileEnv('.env'),
])


SECRET_KEY = str(uuid4())
GITHUB_SECRET = config('GITHUB_SECRET', raise_error=False)
SSH_DOKKU_HOST = config('SSH_DOKKU_HOST')
