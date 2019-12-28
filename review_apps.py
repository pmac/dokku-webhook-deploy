from flask import Flask, request


app = Flask(__name__)
app.config.from_object('settings')


@app.route('/')
def home():
    return {'status': 'ok'}


@app.route('/hooks/', methods=['POST'])
def hooks():
    data = request.json
    print(data)
    return '', 204
