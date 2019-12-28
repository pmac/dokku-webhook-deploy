import hmac

from flask import Flask, request

import settings


app = Flask(__name__)
app.config.from_object(settings)


@app.route('/')
def home():
    return {'status': 'ok'}


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
