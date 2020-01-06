# Dokku Webhook Deploy

Use [Dokku][] to auto-deploy branches pushed to Github.

By default it will create and deploy apps based on branches pushed and named `demo/<name>`, where `<name>`
is anything you want. This will create a Dokku app named `<repo-name>-demo-<name>`, deploy to it, and optionally
setup a Let's Encrypt cert for it. You can also tell it other specific branches to deploy (e.g. `master` or `prod`).
This should be able to fully replace Heroku's GitHub integration including it's Review Apps.

If you are using the [dokku-require](https://github.com/crisward/dokku-require) plugin the required volumes
will be created for you via the `app.json` file; otherwise you can set them up manually following the install instructions.

## Setup

This app is meant to be deployed to your [Dokku][] server, but could really run anywhere. All that is required
is for Github to be able to post webhooks to it, and for it to have SSH access to your Dokku server. All of the shell
commands below should be run on your Dokku server as the `dokku` user.

### 1. Fork this repo

You may want to make changes to the code, but you may not need to. This is an optional step, but it's a good idea
so that you'll have a place to put your changes should you make them.

### 2. Clone your fork

Or clone the original.

```shell
$ git clone https://github.com/pmac/dokku-webhook-deploy
```

### 3. Create and configure your app

```shell
$ export APP_NAME=deployer # or whatever you want your app name to be
$ dokku apps:create $APP_NAME
$ dokku config:set $APP_NAME \
    GITHUB_SECRET=<sekrit> \ # the secret you use to configure webhooks at github
    SSH_DOKKU_HOST=dokku.me \ # your dokku server domain
    APPS_LETSENCRYPT=True \ # if you want the Let's Encrypt plugin to run
```

You can see more about all of the configuration options in the [config docs](config.md), but this should
be a good start.

### 4. Setup the volumes

The app will store some things on the Dokku host: ssh keys, deployment logs, and the bare git repos.

```shell
$ mkdir -p /var/lib/dokku/data/storage/$APP_NAME/{ssh,deploy-logs,repos}
$ dokku storage:mount $APP_NAME /var/lib/dokku/data/storage/$APP_NAME/ssh:/home/dokku/.ssh
$ dokku storage:mount $APP_NAME /var/lib/dokku/data/storage/$APP_NAME/deploy-logs:/app/deploy-logs
$ dokku storage:mount $APP_NAME /var/lib/dokku/data/storage/$APP_NAME/repos:/app/repos
```

### 5. Setup the build arguments

Because the app interacts with the filesystem via the above volumes, it's best if it does so as the `dokku`
user so that permission issues don't arise. To combat that the Dockerfile will accept build args for the user
and group IDs for the local user and will add said user in the image and run as that user rather than root.

```shell
$ dokku docker-options:add $APP_NAME build "--build-arg GROUP_ID=$(id -g)"
$ dokku docker-options:add $APP_NAME build "--build-arg USER_ID=$(id -u)"
```

### 6. Create an SSH key

The app communicates with Dokku via SSH. You should create a new key pair for this specifically.
Make sure you create it with an empty passphrase.

```shell
$ pushd /var/lib/dokku/data/storage/$APP_NAME/ssh
$ ssh-keygen -t rsa -b 4096 -C "webhook-deploy-app" -f ./id_rsa
```

Then you can add it to your Dokku users:

```shell
$ sudo dokku ssh-keys:add webhook-deploy-app ./id_rsa.pub
```

> Note: You may have to do this one as root. Run it via `sudo` from an account with permission to do that.

### 7. Deploy the webhook-deploy app

From your machine push this app you cloned in step 2 to the new app you created in Dokku. Once the initial deployment
is finished and working it is strongly recommended to use the [Let's Encrypt plugin][] to enable TLS on this app so that
communication between GitHub and your server is encrypted:

```shell
$ dokku letsencrypt $APP_NAME
```

### 8. Setup the webhook in Github

Navigate to your repo's webhook settings (URL below) and enter the following for the web:

* URL: `https://github.com/<your-user-or-org>/<your-repo>/settings/hooks/new`
* Payload URL: `https://deployer.<your-dokku-server-domain>/hooks/`
* Content Type: `application/json`
* Secret: The secret you set in your app config from step 3
* Which events would you like to trigger this webhook?: `Just the push event`
* Active: checked

### 9. Profit

You should be done! Now you can push a branch like `demo/test` to your repo and hopefully see a new app! If you configure Slack
integration it will give you the link to the new app and the deployment log. If not you can find the deployment log at a URL like:

`https://deployer.<your-dokku-server-domain>/deploy-logs/repo-name-demo-test.txt`

Where `repo-name-demo-test.txt` is the new app name with a `.txt` suffix. Look in the folder you setup above for deploy-logs
if you can't guess the name.

[Dokku]: http://dokku.viewdocs.io/dokku/
[Let's Encrypt plugin]: https://github.com/dokku/dokku-letsencrypt
