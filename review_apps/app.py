import hmac

from flask import Flask, request

from review_apps import dokku, settings


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

    data = request.json
    print(data)
    return '', 204


def check_github_sig():
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

    return None
