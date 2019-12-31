import hmac

from flask import Flask, request
from io import StringIO
from sh import ssh

from review_apps import settings


app = Flask('review_apps')
app.config.from_object(settings)
dokku_ssh = ssh.bake(settings.SSH_DOKKU_HOST)


def dokku(cmd):
    return StringIO(str(dokku_ssh(cmd)))


def dokku_apps_list():
    return [app.strip() for app in dokku('apps:list') if not app.startswith('===')]


@app.route('/')
def home():
    return {'status': 'ok'}


@app.route('/apps/')
def apps_list():
    return {'apps': dokku_apps_list()}


@app.route('/hooks/', methods=['POST'])
def hooks():
    if settings.GITHUB_SECRET:
        signature = request.headers.get('X-Hub-Signature')
        if signature:
            their_sig = signature[5:]
            key = settings.GITHUB_SECRET.encode()
            our_sig = hmac.new(key, request.data, 'sha1').hexdigest()
            if their_sig != our_sig:
                app.logger.warning(f'HMAC error: {their_sig=}, {our_sig=}')
                return 'HMAC Signature error', 401
        else:
            app.logger.warning('No HMAC signature received')
            return 'HMAC Signature missing', 401


    data = request.json
    print(data)
    return '', 204
