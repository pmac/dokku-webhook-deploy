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


def get_branch_name(branch_name):
    if branch_name.startswith('refs/heads/'):
        # ref is in the form "refs/heads/master"
        branch_name = branch_name[11:]

    if branch_name.startswith(settings.DEMO_BRANCH_PREFIX):
        return branch_name[len(settings.DEMO_BRANCH_PREFIX):]
    else:
        return None


def get_app_name(data):
    branch_name = get_branch_name(data['ref'])
    if branch_name is None:
        return None

    repo_full_name = data['repository']['full_name']
    repo_name = data['repository']['name']
    app_name = settings.APP_NAME_TEMPLATE.format(
        branch_name=branch_name,
        repo_full_name=repo_full_name,
        repo_name=repo_name,
    )
    return slugify(app_name)


def handle_push(data):
    print(data)
    app_name = get_app_name(data)
    if not app_name:
        app.logger.info(f'branch name not supported: {data["ref"]}')
        return

    app.logger.debug(f'got app_name: {app_name}')
    if data['deleted']:
        app.logger.debug(f'deleting app_name: {app_name}')
        dokku.apps_destroy(app_name)
        slack.notify(app_name, 'deleted')
        return

    slack.notify(app_name, 'starting')
    dokku.update_repo(data)
    app.logger.debug('repo updated')
    dokku.push_repo(data, app_name)
    app.logger.debug('repo pushed')
    slack.notify(app_name, 'shipped')
