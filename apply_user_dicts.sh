# NOTE: spaCyモデルの再学習が必要

<< EXAMPLE 辞書のみ追加した場合

% ginza -m ja_core_news_sm
そういうことかも
# text = そういうことかも
1       そう    そう    ADV     副詞    _       2       advmod  _       SpaceAfter=No|Reading=ソウ
2       いう    いう    VERB    動詞-一般       _       3       acl     _       SpaceAfter=No|Inf=五段-ワア行,連体形-一般|Reading=イウ
3       こと    こと    NOUN    名詞-普通名詞-一般      _       0       root    _       SpaceAfter=No|Reading=コト
4       かも    かも    ADP     助詞-副助詞     _       3       case    _       SpaceAfter=No|Reading=カモ

難しいのかも
# text = 難しいの
1       難しい  難しい  ADJ     形容詞-一般     _       0       root    _       SpaceAfter=No|Inf=形容詞,連体形-一般|Reading=ムズカシイ
2       の      の      ADP     助詞-準体助詞   _       1       case    _       SpaceAfter=No|Reading=ノ

# text = かも
1       かも    かも    PROPN   助詞-副助詞     _       0       root    _       SpaceAfter=No|Reading=カモ

ちょっと判断つかないかも
# text = ちょっと判断つかないかも
1       ちょっと        ちょっと        ADV     副詞    _       3       advmod  _       SpaceAfter=No|Reading=チョット
2       判断    判断    VERB    名詞-普通名詞-サ変可能  _       3       obl     _       SpaceAfter=No|Reading=ハンダン
3       つか    つく    VERB    動詞-非自立可能 _       0       root    _       SpaceAfter=No|Inf=五段-カ行,未然形-一般|Reading=ツカ
4       ない    ない    AUX     助動詞  _       3       aux     _       SpaceAfter=No|Inf=助動詞-ナイ,終止形-一般|Reading=ナイ
5       かも    かも    PART    助詞-副助詞     _       3       mark    _       SpaceAfter=No|Reading=カモ

EXAMPLE

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
