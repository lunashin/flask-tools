#!/bin/bash

SCRIPT_DIR=$(cd $(dirname $0); pwd)


which virtualenv > /dev/null
if [ $? -ne 0 ]; then
    echo "virtualenv をインストールしてください。"
    echo "$ pip3 install virtualenv"
    exit 1
fi


# スクリプトのディレクトリへ移動
echo "- Move to Script dir"
cd $SCRIPT_DIR
if [ $? -ne 0 ]; then
    echo "faled."
    exit 1
fi

# virtualenv
echo "- Make virtualenv..."
virtualenv ./

# enable virtualenv
echo "- Activate Virtualenv..."
source ./bin/activate
if [ $? -ne 0 ]; then
    echo "faled."
    exit 1
fi

# flask インストール
echo "- Install flask..."
pip3 install flask
if [ $? -ne 0 ]; then
    echo "faled."
    exit 1
fi
