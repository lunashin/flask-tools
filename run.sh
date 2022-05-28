#!/bin/bash

# バックグラウンドで実行

SCRIPT_DIR=$(cd $(dirname $0); pwd)



# Connection source limitation
# host="0.0.0.0"
host="127.0.0.1"

# port
port=5000
# port=5555


echo "Virtualenv Activate"
source ./bin/activate


echo "Set Env"
# export FLASK_APP=$SCRIPT_DIR/main.py
export FLASK_APP=./main.py
export FLASK_ENV=development

echo "run flask ( $host:$port )"
flask run --host $host --port $port
