# All Configuration Options

Configuration should be set in environment variables, but can also be set in a `.env` file in the project root (mostly for development use).

## LOG_LEVEL

Can be the usual things (e.g. 'DEBUG', 'INFO', etc.). Default is 'INFO'.

## GITHUB_SECRET

When you create your webhook in your GitHub repo settings, you have the option of setting a secret. It's highly recommended that you set this. If you do, github will use that secret to calculate an HMAC signature of the POST data using SHA1 and [send it with the POST in a header](https://developer.github.com/webhooks/#delivery-headers). Set the same secret in this variable to have the app calculate the same HMAC signature and verify that they match. In this way we can verify that this POST request did indeed come from a service that has this secret, which hopefully means only Github.

## SSH_DOKKU_{HOST,PORT,USER}

The connection information for your Dokku server via SSH. The only required one is `SSH_DOKKU_HOST` which has no default
and nothing else really works without it. The others have useful defaults:

```dotenv
SSH_DOKKU_USER=dokku
SSH_DOKKU_PORT=22
```

## APPS_DOKKU_DOMAIN

This defaults to `SSH_DOKKU_HOST` but if you have another domain you use for public access to the apps then you can define it here.

## APPS_LETSENCRYPT

This is a boolean and tells the system whether or not to setup a Let's Encrypt cert for the newly created apps using the Let's Encrypt Dokku plugin.

## DEMO_BRANCH_PREFIX 

This determines which branches will be deployed as demos (or review apps). The default is `demo/`, but you can set it to be anything else with this setting.

## DEFAULT_DEPLOY_BRANCHES

If you'd like for the system to deploy any other branches that don't match the demo prefix above, you can set them here. This should be a comma separated list of branch names:

```dotenv
DEFAULT_DEPLOY_BRANCHES=master,stage,prod
```

You can alternatively override this setting on a per-repo basis if you have more than one repo setup to use your instance for deployments. The repo-specific version uses the owner and repo names in the environment variable. For example:

```dotenv
# repo name: pmac/dokku-webhook-deploy
PMAC_DOKKU_WEBHOOK_DEPLOY_BRANCHES=master,prod
```

If a matching config name is found it will be used, otherwise it will fall back to the default list above. The default for both is an empty list which means no non-demo deployments will happen.

## APP_NAME_TEMPLATE

You can customize the names of the created apps if you wish. The default is:

```dotenv
APP_NAME_TEMPLATE={repo_name}-{branch_name}
```

The format should be that of the [Python str.format()](https://docs.python.org/3/library/string.html#formatstrings) function, and
the available variables are:

* `repo_name`: Name of the repository without the owner prefix (e.g. `dokku-webhook-deploy`)
* `repo_full_name`: Name of the repository with the owner prefix (e.g. `pmac/dokku-webhook-deploy`)
* `branch_name`: Full name of the branch (e.g. `master` or `demo/feature`)

All of those strings will be [slugified](https://github.com/un33k/python-slugify#how-to-use) for use in the name, which mostly means all non-alpha-numerics become dashes.

## SLACK_*

If you set these variables updates about your deployments will be sent to the slack team and channel of your choice.

```dotenv
SLACK_API_TOKEN=<the token from slack>
SLACK_CHANNEL=#my-deployments
```

See the [following page](https://api.slack.com/custom-integrations/legacy-tokens) for how to get your token.

> Note: Yes, this is an old way of doing Slack and the plan is to upgrade. For now this works.
