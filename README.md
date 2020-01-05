# dokku-webhook-deploy

Use Dokku to auto-deploy branches pushed to Github.

By default it will create and deploy apps based on branches pushed and named `demo/<name>`, where `<name>`
is anything you want. This will create a Dokku app named `<repo-name>-<name>`, deploy to it, and optionally
setup a Let's Encrypt cert for it. You can also tell it other specific branches to deploy (e.g. `master` or `prod`).
