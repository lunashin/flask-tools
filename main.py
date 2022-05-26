#!python

from flask import Flask, render_template, make_response, jsonify, request, redirect
from werkzeug.utils import secure_filename
import functools
import json
import csv
import io
import base64
import binascii
import schedule_manager
import datetime
import os
from aws import ec2


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
    # decode = base64decode(request.json['data']).decode()
    decode = base64decode(request.json['data'])
    if decode == '':
        decode = 'Error.'

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





# Base64デコード
def base64decode(str):
    decode_str = ""
    try:
        decode_str = base64.b64decode(str)
    except Exception:
        try:
            decode_str = base64.b64decode(str + "=")
        except Exception:
            try:
                decode_str = base64.b64decode(str + "==")
            except Exception as e:
                print("base64 decodee error.")
                print(e)
                return ""
    return decode_str.decode('utf8')










#################################################### 
# CSV スケジュール作成
#################################################### 

app.config['CSV_FILE'] = ''
app.config['CSV_DELIMITER'] = '\t'



# CSVテキストからスケジュールを作成(ファイル版)
def make_schedule_from_file(csv_file, index_name, index_days, index_role, start_date_str):
    ret = ""
    with open(csv_file) as f:
        ret = make_schedule_from_stream(f, index_name, index_days, index_role, start_date_str)
    return ret


# CSVテキストからスケジュールを作成(テキスト版)
def make_schedule_from_string(csv_text, index_name, index_days, index_role, start_date_str):
    # 文字列をストリームへ書き込み
    f = io.StringIO()
    f.write(csv_text)
    f.seek(0)
    ret = make_schedule_from_stream(f, index_name, index_days, index_role, start_date_str)
    f.close()
    return ret


# CSVテキストからスケジュールを作成(ストリーム版)
def make_schedule_from_stream(f, index_name, index_days, index_role, start_date_str):
    mng = schedule_manager.schedule_manager()

    # インデックス位置設定
    mng.setIndexName(index_name)
    mng.setIndexDays(index_days)
    mng.setIndexRole(index_role)

    # CSVから読み取り
    mng.read_csv_from_stream(f, app.config['CSV_DELIMITER'])
    f.close()

    # スケジュールを計算
    start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d')
    mng.detect_start_end(start_date)

    result = mng.get_csv_text(app.config['CSV_DELIMITER'])
    print("resut--------------")
    print(result)

    return result


# CSVファイルから先頭行のフィールドをリストで取得
def get_field_list(csvfile):
    # 1行目を取得
    field_list = list()
    with open(csvfile) as f:
        reader = csv.reader(f, delimiter=app.config['CSV_DELIMITER'])
        index = 0
        for row in reader:
            for field in row:
                field_list.append(field)
            break
    
    return field_list


# 
def get_field_index(csvfile, keyword, default_index):
    index_ret = -1

    # 1行目を取得
    field_list = list()
    with open(csvfile) as f:
        reader = csv.reader(f, delimiter=app.config['CSV_DELIMITER'])
        index = 0
        for row in reader:
            for field in row:
                if keyword in field:
                    index_ret = index
                index += 1
            break
    
    # 該当なしの場合はデフォルト値
    if index_ret == -1:
        index_ret = default_index
    
    return index_ret




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
    result = make_schedule_from_string(csv_text, index_name, index_days, index_role, start_date)

    # make result
    result_data = result

    # make response
    j = json.loads('{"result":""}')
    j["result"] = result_data

    # response
    return j








#################################################### 
# CSV スケジュール作成 (CSVファイルアップロード版)
#################################################### 

# Upload CSV
#
@app.route("/upload_csv", methods=["POST"])
def ep_csv_upload():
    form_key = "files"

    # ファイル名等チェック・保存
    file_dest = check_and_store_file(request, form_key)
    if file_dest == '':
        print("redirect")
        return redirect("/static/csv-upload.html")

    app.config['CSV_FILE'] = file_dest

    # デリミタ決定
    with open(file_dest) as f:
        s_line = f.readline()
        if '\t' in s_line:
            app.config['CSV_DELIMITER'] = '\t'
        else:
            app.config['CSV_DELIMITER'] = ','

    # CSVフィールド一覧取得
    field_list = get_field_list(file_dest)
    print(field_list)

    # インデックス取得
    index_name = get_field_index(file_dest, 'タスク', 0)
    index_days = get_field_index(file_dest, '工数', 1)
    index_role = get_field_index(file_dest, '担当', -1)
    if index_role == -1:
        index_role_str = ""
    else:
        index_role_str = str(index_role)
    
    dt_now_str = datetime.datetime.now().strftime('%Y%m%d')
    return render_template('csv_set_param.html', csv_field_list=field_list, index_name=str(index_name), index_days=str(index_days), index_role=index_role_str, start_date=dt_now_str)



# Set param CSV
#
@app.route("/set_param_csv", methods=["GET"])
def ep_csv_set_param():
    index_name_str = request.args.get('index_name')
    index_days_str = request.args.get('index_days')
    index_role_str = request.args.get('index_role')
    start_date_str = request.args.get('start_date')
    print(index_name_str,index_days_str,index_role_str,start_date_str)

    # クエリチェック
    if index_name_str is None or index_name_str == '':
        field_list = get_field_list(app.config['CSV_FILE'])
        return render_template('csv_set_param.html', csv_field_list=field_list, index_name=index_name_str, index_days=index_days_str, index_role=index_role_str, start_date=start_date_str)
    if index_days_str is None or index_days_str == '':
        field_list = get_field_list(app.config['CSV_FILE'])
        return render_template('csv_set_param.html', csv_field_list=field_list, index_name=index_name_str, index_days=index_days_str, index_role=index_role_str, start_date=start_date_str)
    if start_date_str is None or start_date_str == '':
        field_list = get_field_list(app.config['CSV_FILE'])
        return render_template('csv_set_param.html', csv_field_list=field_list, index_name=index_name_str, index_days=index_days_str, index_role=index_role_str, start_date=start_date_str)

    if index_role_str is None or index_role_str == '':
        index_role_str = "-1"

    index_name = int(index_name_str)
    index_days = int(index_days_str)
    index_role = int(index_role_str)

    # スケジュールCSV作成
    ret_csv = make_schedule_from_file(app.config['CSV_FILE'], index_name, index_days, index_role, start_date_str)

    return render_template('csv_result.html', csv_text=ret_csv)












# 画像のアップロード先のディレクトリ
UPLOAD_FOLDER = './uploads'
# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif', 'csv'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

redirect_url = "/static/upload.html"



# ファイル名チェック
# return: True / False
def allwed_file(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ファイル名等チェック・保存
# 
def check_and_store_file(request, form_key):
    # ファイルがなかった場合の処理
    if form_key not in request.files:
        print('ファイルがありません')
        return ''

    # データの取り出し
    file = request.files[form_key]
    print("filename: ", file)

    # ファイル名がなかった時の処理
    if file.filename == '':
        print('ファイルがありません2')
        return ''

    # ファイルのチェック
    if file and allwed_file(file.filename):
        # 危険な文字を削除（サニタイズ処理）
        filename = secure_filename(file.filename)
        # ファイルの保存
        dest = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(dest)
        print("保存先: ", dest)
        return dest
    else:
        print('許可されていないファイル')

    return ''



# Upload files TEST
#
@app.route("/upload", methods=["POST"])
def ep_upload():
    form_key = "files"

    if request.method == 'POST':
        # ファイル名等チェック・保存
        file_dest = check_and_store_file(request, form_key)
        if file_dest != '':
            print(file_dest)
            print("success")

    redirect(redirect_url)
    return ''





##################################################
# AWS
##################################################

# AWS
#
@app.route("/aws", methods=["GET"])
def ep_aws():
    ec2_obj = ec2.ec2()
    res_running = ec2_obj.get_running()
    res_not_running = ec2_obj.get_not_running()
    return render_template('ec2_list.html', running_list=res_running, not_running_list=res_not_running)


# AWS Create (いつもの)
#
@app.route("/aws/create_template", methods=["GET"])
def ep_aws_create_template():
    ec2_obj = ec2.ec2()
    
    dt_now = datetime.datetime.now()
    dt_str = dt_now.strftime('%Y-%m-%d_%H%M%S')
    name = dt_str
    instance_type = 't2.micro'
    image_id = 'ami-00bc9b7f0e98dc134'
    security_group_id = 'sg-0633e97c90e23f751'

    ec2_obj.create_instance(name, instance_type, image_id, security_group_id)
    return "ok"

# AWS START
#
@app.route("/aws/start", methods=["GET"])
def ep_aws_start():
    if request.args.get('instance_id') is not None:
        ec2_obj = ec2.ec2_low()
        ec2_obj.start(request.args.get('instance_id'))
    return "ok"

# AWS STOP
#
@app.route("/aws/stop", methods=["GET"])
def ep_aws_stop():
    if request.args.get('instance_id') is not None:
        ec2_obj = ec2.ec2_low()
        ec2_obj.stop(request.args.get('instance_id'))
    return "ok"

# AWS Terminate
#
@app.route("/aws/terminate", methods=["GET"])
def ep_aws_terminate():
    if request.args.get('instance_id') is not None:
        ec2_obj = ec2.ec2_low()
        ec2_obj.terminate(request.args.get('instance_id'))
    return "ok"









## magic
if __name__ == "__main__":
    # app.run(debug=True, host='127.0.0.1', port=5555)
    app.run(debug=True)