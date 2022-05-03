#!python

from flask import Flask, render_template, make_response, jsonify, request
import functools
import json
import csv
import io
import base64
import binascii
import schedule_manager
import datetime

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






# CSVテキストからスケジュールを作成
def make_schedule(csv_text, index_name, index_days, index_role, start_date):
    # 文字列をストリームへ書き込み
    f = io.StringIO()
    f.write(csv_text)
    f.seek(0)

    mng = schedule_manager.schedule_manager()

    # インデックス位置設定
    mng.setIndexName(index_name)
    mng.setIndexDays(index_days)
    mng.setIndexRole(index_role)

    # CSVから読み取り
    mng.read_csv_from_stream(f, ',')
    f.close()

    # スケジュールを計算
    mng.detect_start_end(start_date)

    result = mng.get_csv_text(',')
    print("resut--------------")
    print(result)

    return result



# Make Schedule CSV
#
# content-type : application/json
# body { "data":"[CSV text], "index_name": x, "index_days": x, "index_role": x, "start_date": "yyyymmdd" }
@app.route("/csv", methods=["POST"])
@content_type('application/json')
def ep_csv():
    # print(request.json['data'])
    csv_text = request.json['data']
    index_name = request.json['index_name']
    index_days = request.json['index_days']
    index_role = request.json['index_role']
    start_date_str = request.json["start_date"]
    start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d')

    # スケジュール作成
    result = make_schedule(csv_text, index_name, index_days, index_role, start_date)

    # make result
    result_data = result

    # make response
    j = json.loads('{"result":""}')
    j["result"] = result_data

    # response
    return j








## magic
if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5555)