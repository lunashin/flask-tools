#!python

from flask import Flask, render_template, make_response, jsonify, request
import functools
import json
import csv
import io
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

    # JSON Format
    try:
        j_decode = json.loads(decode)
        j_indent = json.dumps(j_decode, indent=2)
    except Exception as e:
        j_indent = ""

    # make response
    j = json.loads('{"result":""}')
    j["result"] = decode
    j["json_formated"] = j_indent

    # response
    return j


# base64 tool page
@app.route("/b64", methods=["GET"])
def ep_base64_tool():
    return render_template('b64.html')






# csv test
#
# content-type : application/json
# body {"data":"[Base64 encoded CSV]"}
@app.route("/csv", methods=["POST"])
@content_type('application/json')
def ep_csv():
    print(request.json['data'])
    csv_b64 = request.json['data']

    # BASE64デコード
    decode_csv = base64.b64decode(csv_b64).decode()
    print(decode_csv)

    # 文字列をストリームへ書き込み
    f = io.StringIO()
    f.write(decode_csv)
    f.seek(0)

    # CSVとしてパース
    csv_reader = csv.reader(f)
    for row in csv_reader:
        # TODO: CSVに対する任意の処理
        print(row)

    f.close()

    # make result
    result_data = ""

    # make response
    j = json.loads('{"result":""}')
    j["result"] = result_data

    # response
    return j








## magic
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5555)