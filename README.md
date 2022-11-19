# Dialog Reflection

A library for dialog systems that attempt to respond to messages as Reflective Listening.

## Demo

Need `git` and `poetry` to run this demo.

```console
$ git clone git@github.com:sadahry/dialog-reflection.git
$ cd dialog-reflection
$ poetry install
$ poetry run python examples/interactive_ja.py
```

## Install

Need `python` >= `3.10`

```console
$ pip install dialog-reflection
```

## How to Use (Japanese)

SpaCyの日本語モデルのインストールが必要  
* `ja_ginza==5.1.2` でテスト済
* 他モデルの利用は可能だが推奨しない
  * 係り受けや形態素解析によって不整合があるため利用前にテストを推奨

```console
$ pip install ja_ginza==5.1.2
```

実行例

```python
from dialog_reflection.lang.ja.reflector import JaSpacyReflector


refactor = JaSpacyReflector(model="ja_ginza")

message = "今日は旅行へ行った"
reflection_text = refactor.reflect(message)

print(reflection_text)
# => 旅行へ行ったんですね。
```

Builderを使う例

```python
from dialog_reflection.lang.ja.reflection_text_builder import (
    JaSpacyPlainReflectionTextBuilder,
)
import spacy


nlp = spacy.load("ja_ginza")
builder = JaSpacyPlainReflectionTextBuilder()

message = "今日は旅行へ行った"
doc = nlp(message)
# some code...
reflection_text = builder.build(doc)

print(reflection_text)
# => 旅行へ行ったんですね。
```

### 語尾の調整

`op` を変更することで語尾を調整可能

```python
from dialog_reflection.lang.ja.reflector import JaSpacyReflector
from dialog_reflection.lang.ja.reflection_text_builder import (
    JaSpacyPlainReflectionTextBuilder,
)
from dialog_reflection.lang.ja.reflection_text_builder_option import (
    JaSpacyPlainReflectionTextBuilderOption,
)


refactor = JaSpacyReflector(
    model="ja_ginza",
    builder=JaSpacyPlainReflectionTextBuilder(
        op=JaSpacyPlainRelflectionTextBuilderOption(
            fn_last_token_taigen=lambda token: token.text + "なんだね。",
            fn_last_token_yougen=lambda token: token.lemma_ + "んだね。",
        )
    ),
)

message = "今日は旅行へ行った"
reflection_text = refactor.reflect(message)

print(reflection_text)
# => 旅行へ行ったんだね。
```

その他設定項目は [reflection_text_builder_option.py](https://github.com/sadahry/dialog-reflection/blob/main/dialog_reflection/lang/ja/reflection_text_builder_option.py#L24) を確認してください

### ロジックのカスタマイズ

`JaSpacyPlainReflectionTextBuilder` を override することでロジックをカスタマイズ可能

```python
from dialog_reflection.reflection_cancelled import (
    ReflectionCancelled,
)
from dialog_reflection.cancelled_reason import (
    NoValidSentence,
)
from dialog_reflection.lang.ja.reflector import JaSpacyReflector
from dialog_reflection.lang.ja.reflection_text_builder import (
    JaSpacyPlainReflectionTextBuilder,
)
import spacy


class CustomReflectionTextBuilder(JaSpacyPlainReflectionTextBuilder):
    def extract_tokens(self, doc: spacy.tokens.Doc) -> spacy.tokens.Span:
        propn_token = next(filter(lambda token: token.pos_ == "PROPN", doc), None)
        if propn_token is None:
            raise ReflectionCancelled(reason=NoValidSentence(doc=doc))
        if propn_token.dep_ in ["compound", "numpound"]:
            return doc[propn_token.i : propn_token.head.i + 1]
        return doc[propn_token.i : propn_token.i + 1]


refactor = JaSpacyReflector(
    model="ja_ginza",
    builder=CustomReflectionTextBuilder(),
)


message = "今日は田中さんと旅行へ行った"
reflection_text = refactor.reflect(message)

print(reflection_text)
# => 田中さんなんですね。
```
