#!python

from flask import Flask, render_template, make_response, jsonify, request
import functools
import json
import base64
import binascii

app = Flask(__name__)



# check content-type decorator
def content_type(value):
    def _content_type(func):
        @functools.wraps(func)
        def wrapper(*args,**kwargs):
            if not request.headers.get("Content-Type") == value:
                error_message = {
                    'error': 'not supported Content-Type'
                }
                return make_response(jsonify(error_message), 400)

            return func(*args,**kwargs)
        return wrapper
    return _content_type




@app.route('/')
def hello():
    return render_template('index.html')


# base64 encode
@app.route("/b64encode", methods=["POST"])
@content_type('application/json')
def ep_base64encode():
    print(request.json['data'])

    # decode base64
    decode_bin = base64.b64encode(request.json['data'].encode())
    print(decode_bin)

    # make response
    j = json.loads('{"result":""}')
    j["result"] = decode_bin.decode()

    # response
    return j


# base64 decode
@app.route("/b64decode", methods=["POST"])
@content_type('application/json')
def ep_base64decode():
    print(request.json['data'])

    # decode base64
    decode = "Error."
    try:
        decode = base64.b64decode(request.json['data']).decode()
    except UnicodeDecodeError as e:
        print("Error. base64.b64decode()")
        print(e)
    except binascii.Error as e:
        print("Error. base64.b64decode()")
        print(e)

    # make response
    j = json.loads('{"result":""}')
    j["result"] = decode

    # response
    return j


# base64 tool page
@app.route("/b64", methods=["GET"])
def ep_base64_tool():
    return render_template('b64.html')








## magic
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5555)