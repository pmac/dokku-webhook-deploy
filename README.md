# dokku-webhook-deploy

Use Dokku to auto-deploy branches pushed to Github.

By default it will create and deploy apps based on branches pushed and named `demo/<name>`, where `<name>`
is anything you want. This will create a Dokku app named `<repo-name>-<name>`, deploy to it, and optionally
setup a Let's Encrypt cert for it. You can also tell it other specific branches to deploy (e.g. `master` or `prod`).
This should be able to fully replace Heroku's GitHub integration including it's Review Apps.

If you are using the [dokku-require](https://github.com/crisward/dokku-require) plugin the required volumes
will be created for you via the `app.json` file; otherwise you can set them up manually following the 
[install instructions](https://dokku-webhook-deploy.readthedocs.io/).
