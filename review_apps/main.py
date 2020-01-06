import hmac
from logging.config import dictConfig

from flask import Flask, request, send_from_directory

from slugify import slugify

from review_apps import dokku, settings, slack


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': settings.LOG_LEVEL,
        'handlers': ['wsgi']
    }
})

app = Flask('review_apps')
app.config.from_object(settings)


@app.route('/')
def home():
    return {'status': 'ok'}


@app.route('/apps/')
def apps_list():
    return {'apps': dokku.apps_list()}


@app.route('/hooks/', methods=['POST'])
def hooks():
    sig = check_github_sig()
    if sig is not None:
        return sig

    handle_push(request.json)
    return '', 204


@app.route('/deploy-logs/<path:filename>')
def deploy_logs(filename):
    return send_from_directory(settings.DEPLOY_LOGS_BASE_PATH, filename)


def check_github_sig():
    if settings.GITHUB_SECRET:
        signature = request.headers.get('X-Hub-Signature')
        if signature:
            their_sig = signature[5:]
            key = settings.GITHUB_SECRET.encode()
            our_sig = hmac.new(key, request.data, 'sha1').hexdigest()
            if their_sig != our_sig:
                app.logger.warning(f'HMAC error: {their_sig}, {our_sig}')
                return 'HMAC Signature error', 401
        else:
            app.logger.warning('No HMAC signature received')
            return 'HMAC Signature missing', 401

    return None


def get_branch_name(ref):
    """
    Take a full git ref name and return a more simple branch name.
    e.g. `refs/heads/demo/dude` -> `demo/dude`

    :param ref: the git head ref sent by GitHub
    :return: str the simple branch name
    """
    refs_prefix = 'refs/heads/'
    if ref.startswith(refs_prefix):
        # ref is in the form "refs/heads/master"
        ref = ref[len(refs_prefix):]

    return ref


def get_app_name(data):
    demo = False
    branch_name = get_branch_name(data['ref'])
    if branch_name.startswith(settings.DEMO_BRANCH_PREFIX):
        demo = True

    repo_name = data['repository']['name']
    repo_full_name = data['repository']['full_name']
    deploy_branches = settings.get_deploy_branches(repo_full_name)
    if not (demo or branch_name in deploy_branches):
        return None

    app_name = settings.APP_NAME_TEMPLATE.format(
        branch_name=branch_name,
        repo_full_name=repo_full_name,
        repo_name=repo_name,
    )
    return slugify(app_name)


def handle_push(data):
    app_name = get_app_name(data)
    user = data['pusher']['name']
    if not app_name:
        app.logger.info(f'branch name not supported: {data["ref"]}')
        return

    app.logger.debug(f'got app_name: {app_name}')
    if data['deleted']:
        app.logger.debug(f'deleting app_name: {app_name}')
        dokku.apps_destroy(app_name)
        slack.notify(user, app_name, 'deleted')
    else:
        slack.notify(user, app_name, 'started')
        dokku.apps_create(app_name)
        dokku.update_repo(data)
        app.logger.debug('repo updated')
        dokku.push_repo(data, app_name)
        app.logger.debug('repo pushed')
        slack.notify(user, app_name, 'shipped')
