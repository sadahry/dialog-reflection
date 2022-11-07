# NOTE: 設定をリバートしたい場合はdict_dirを空フォルダを指定

#!/bin/bash
set -eu
cd $(dirname $0)

# confirm jq

echo confirming you have jq...
which jq

dict_dir=`pwd`/dicts
cache_dir=`pwd`/.sudachi_dict_cache
sudachi_json=`pwd`/.venv/lib/python3.10/site-packages/sudachipy/resources/sudachi.json
system_dict=`pwd`/.venv/lib/python3.10/site-packages/sudachidict_core/resources/system.dic 

# clear cache

rm -rf $cache_dir
mkdir -p $cache_dir

# create user dictionary
# ファイルの読み込みが後になるほど（降順に）ユーザー辞書の優先順位が高い

user_dicts=""
for file in `ls dicts`
do
    dict_file=$cache_dir/$file.dic
    poetry run sudachipy ubuild $dict_dir/$file -o $dict_file -s $system_dict
    user_dicts+="\"$dict_file\","
done
user_dicts=${user_dicts%?} # remove last comma

user_dicts_json="["
user_dicts_json+=$user_dicts
user_dicts_json+="]"

# apply user dictionary

cat $sudachi_json | jq ".userDict = $user_dicts_json" > $sudachi_json.tmp
mv $sudachi_json $sudachi_json.bk
mv $sudachi_json.tmp $sudachi_json
