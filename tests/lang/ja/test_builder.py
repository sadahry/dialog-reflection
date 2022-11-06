# NOTE: あくまでテスト用
# TODO JaSpacyReflectionTextBuilder に移植
from typing import Tuple, Optional
import pytest
import re
import spacy


TAIGEN_REGEXP = re.compile(r".*(名|代名|形状|助)詞")


def build(sent: spacy.tokens.Span) -> str:
    if len(sent) == 0:
        return ""

    last_token = sent[-1]

    tag = last_token.tag_

    suffix = "なんですね" if TAIGEN_REGEXP.match(tag) else "んですね"

    return sent[:-1].text + last_token.lemma_ + suffix


def get_conjugation(token: spacy.tokens.Token) -> Tuple[Optional[str], Optional[str]]:
    # sudachiの形態素解析結果(part_of_speech)5つ目以降(活用タイプ、活用形)が格納される
    # 品詞によっては活用タイプ、活用形が存在しないため、ここでは配列の取得のみ行う
    # e.g. 動詞
    # > m.part_of_speech() # => ['動詞', '一般', '*', '*', '下一段-バ行', '連用形-一般']
    # ref. https://github.com/explosion/spaCy/blob/v3.4.1/spacy/lang/ja/__init__.py#L102
    # ref. https://github.com/WorksApplications/SudachiPy/blob/v0.5.4/README.md
    # > Returns the part of speech as a six-element tuple. Tuple elements are four POS levels, conjugation type and conjugation form.
    # ref. https://worksapplications.github.io/sudachi.rs/python/api/sudachipy.html#sudachipy.Morpheme.part_of_speech
    inflection = token.morph.get("Inflection")
    if not inflection:
        return None, None
    inflection = inflection[0].split(";")
    conjugation_type = inflection[0]
    conjugation_form = inflection[1]
    return conjugation_type, conjugation_form


# NOTE: 形態素解析のように正しく文書を分離することが目的ではないため
#       正しく文章が切断されていることまでを確認する


@pytest.mark.parametrize(
    "msg, text, expected",
    [
        # ref, https://ja.wikipedia.org/wiki/五段活用
        (
            "五段活用",
            "あなたと歩く",
            "あなたと歩くんですね",
        ),
        # ref, https://ja.wikipedia.org/wiki/上一段活用
        (
            "上一段活用",
            "あなたと老いる",
            "あなたと老いるんですね",
        ),
        # ref, https://ja.wikipedia.org/wiki/下一段活用
        (
            "下一段活用",
            "下に見える",
            "下に見えるんですね",
        ),
        # 「いく」のみ特殊
        (
            "五段活用",
            "あなたといく",
            "あなたといくんですね",
        ),
        # ref. https://ja.wikipedia.org/wiki/カ行変格活用
        (
            "カ行変格活用",
            "家にくる",
            "家にくるんですね",
        ),
        (
            "カ行変格活用",
            "家に来る",
            "家に来るんですね",
        ),
        # ref. https://ja.wikipedia.org/wiki/サ行変格活用
        (
            "サ行変格活用",
            "軽くウォーキングする",
            "軽くウォーキングするんですね",
        ),
        (
            "サ行変格活用",
            "フライパンを熱する",
            "フライパンを熱するんですね",
        ),
        (
            "サ行変格活用",
            "影響が生ずる",
            "影響が生ずるんですね",
        ),
        # 形容詞
        (
            "形容詞",
            "あなたは美しい",
            "あなたは美しいんですね",
        ),
        # 形容動詞
        (
            "形容動詞",
            "あなたは傲慢",
            "あなたは傲慢なんですね",
        ),
        # 名詞
        (
            "名詞",
            "それは明日",
            "それは明日なんですね",
        ),
        # 固有名詞
        (
            "固有名詞",
            "それはステファン",
            "それはステファンなんですね",
        ),
        # 代名詞
        (
            "代名詞",
            "それはそれ",
            "それはそれなんですね",
        ),
        # 接尾辞
        (
            "接尾辞-名詞的",
            "田中さん",
            "田中さんなんですね",
        ),
        (
            "接尾辞-動詞的",
            "田中ぶる",
            "田中ぶるんですね",
        ),
        (
            "接尾辞-形容詞的",
            "田中っぽい",
            "田中っぽいんですね",
        ),
        (
            "接尾辞-形状詞的",
            "田中だらけ",
            "田中だらけなんですね",
        ),
        # 稀なケースであり想定されないためスキップ
        # # 連体詞
        # (
        #     "連体詞",
        #     "全然あるその",
        #     "全然ある",
        # ),
        # (
        #     "接頭辞",
        #     "いや超",
        #     "いや超",
        # ),
        # (
        #     "感動詞",
        #     "そういうことほら",
        #     "そういうこと",
        # ),
    ],
)
def test_spacy_katsuyo_text_detector(nlp_ja, msg, text, expected):
    sent = next(nlp_ja(text).sents)
    result = build(sent)
    assert result == expected, msg


@pytest.mark.parametrize(
    "msg, text, expected",
    [
        # ref. https://ja.wikipedia.org/wiki/助詞#格助詞
        (
            "格助詞「が」",
            "それが",
            "それがなんですね",
        ),
        (
            "格助詞「の」",
            "それの",
            "それのなんですね",
        ),
        (
            "格助詞「を」",
            "それを",
            "それをなんですね",
        ),
        (
            "格助詞「に」",
            "それに",
            "それになんですね",
        ),
        (
            "格助詞「へ」",
            "それへ",
            "それへなんですね",
        ),
        (
            "格助詞「と」",
            "それと",
            "それとなんですね",
        ),
        (
            "格助詞「から」",
            "それから",
            "それからなんですね",
        ),
        (
            "格助詞「より」",
            "それより",
            "それよりなんですね",
        ),
        (
            "格助詞「で」",
            "それで",
            "それでなんですね",
        ),
        # ref. https://ja.wikipedia.org/wiki/助詞#並列助詞
        (
            "並列助詞「の」",
            "それの",
            "それのなんですね",
        ),
        (
            "並列助詞「に」",
            "それに",
            "それになんですね",
        ),
        (
            "並列助詞「と」",
            "それと",
            "それとなんですね",
        ),
        (
            "並列助詞「や」",
            "それや",
            "それやなんですね",
        ),
        (
            "並列助詞「し」",
            "それし",
            "それしなんですね",
        ),
        (
            "並列助詞「やら」",
            "それやら",
            "それやらなんですね",
        ),
        (
            "並列助詞「か」",
            "それか",
            "それかなんですね",
        ),
        (
            "並列助詞「なり」",
            "それなりあれなり",
            "それなりあれなりなんですね",
        ),
        (
            "並列助詞「だの」",
            "それだの",
            "それだのなんですね",
        ),
        # ref. https://ja.wikipedia.org/wiki/助詞#副助詞
        (
            "副助詞「ばかり」",
            "そればかり",
            "そればかりなんですね",
        ),
        (
            "副助詞「まで」",
            "それまで",
            "それまでなんですね",
        ),
        (
            "副助詞「ほど」",
            "それほど",
            "それほどなんですね",
        ),
        (
            "副助詞「くらい」",
            "それくらい",
            "それくらいなんですね",
        ),
        (
            "副助詞「ぐらい」",
            "それぐらい",
            "それぐらいなんですね",
        ),
        (
            "副助詞「など」",
            "それなど",
            "それなどなんですね",
        ),
        (
            "副助詞「なり」",
            "それなり",
            "それなりなんですね",
        ),
        (
            "副助詞「やら」",
            "それやら",
            "それやらなんですね",
        ),
        (
            "副助詞「か」",
            "それか",
            "それかなんですね",
        ),
        (
            "副助詞「がてら」",
            "それがてら",
            "それがてらなんですね",
        ),
        (
            "副助詞「かり」",
            "そればっかり",
            "そればっかりなんですね",
        ),
        (
            "副助詞「ずつ」",
            "それずつ",
            "それずつなんですね",
        ),
        (
            "副助詞「のみ」",
            "それのみ",
            "それのみなんですね",
        ),
        (
            "副助詞「きり」",
            "それきり",
            "それきりなんですね",
        ),
        (
            "副助詞「や」",
            "あれやそれや",
            "あれやそれやなんですね",
        ),
        # INVALIDとして扱われる想定。テストケースには含めない
        # # 例外的なケース
        # (
        #     "副助詞「って」",
        #     "それって",
        # ),
        # ref. https://ja.wikipedia.org/wiki/助詞#係助詞
        (
            "係助詞「は」",
            "そういうことでは",
            "そういうことではなんですね",
        ),
        (
            "係助詞「も」",
            "そういうことも",
            "そういうこともなんですね",
        ),
        (
            "係助詞「こそ」",
            "そういうことこそ",
            "そういうことこそなんですね",
        ),
        (
            "係助詞「でも」",
            "そういうことでも",
            "そういうことでもなんですね",
        ),
        (
            "係助詞「しか」",
            "そういうことしか",
            "そういうことしかなんですね",
        ),
        (
            "係助詞「さえ」",
            "そういうことさえ",
            "そういうことさえなんですね",
        ),
    ],
)
def test_spacy_katsuyo_text_detector_joshi(nlp_ja, msg, text, expected):
    sent = next(nlp_ja(text).sents)
    result = build(sent)
    assert result == expected, msg


@pytest.mark.parametrize(
    "msg, text, expected",
    [
        # ref, https://ja.wikipedia.org/wiki/助詞#接続助詞
        (
            "接続助詞「が」",
            "頑張ったが、",
            "頑張ったがなんですね",
        ),
        (
            "接続助詞「し」",
            "頑張ったし、",
            "頑張ったしなんですね",
        ),
        (
            "接続助詞「て」",
            "頑張って、",
            "頑張ってなんですね",
        ),
        (
            "接続助詞「で」",
            "遊んで、",
            "遊んでなんですね",
        ),
        (
            "接続助詞「と」",
            "頑張ると、",
            "頑張るとなんですね",
        ),
        (
            "接続助詞「ど」",
            "頑張れど、",
            "頑張れどなんですね",
        ),
        (
            "接続助詞「に」",
            "頑張ってるのに、",
            "頑張ってるのになんですね",
        ),
        (
            "接続助詞「ば」",
            "頑張ってれば、",
            "頑張ってればなんですね",
        ),
        (
            "接続助詞「から」",
            "頑張るから、",
            "頑張るからなんですね",
        ),
        (
            "接続助詞「つつ」",
            "頑張りつつ、",
            "頑張りつつなんですね",
        ),
        (
            "接続助詞「ては」",
            "頑張っては、",
            "頑張ってはなんですね",
        ),
        (
            "接続助詞「ては」",
            "頑張っちゃあ、",
            "頑張っちゃあなんですね",  # TODO normを適用できるように
        ),
        (
            "接続助詞「とて」",
            "頑張ったとて、",
            "頑張ったとてなんですね",
        ),
        (
            "接続助詞「とも」",
            "何をしようとも、",
            "何をしようともなんですね",
        ),
        (
            "接続助詞「なり」",
            "頑張るなり、",
            "頑張るなりなんですね",
        ),
        (
            "接続助詞「けれど」",
            "頑張ったけれど、",
            "頑張ったけれどなんですね",
        ),
        (
            "接続助詞「たって」",
            "頑張ったって、",
            "頑張ったってなんですね",
        ),
        (
            "接続助詞「ながら」",
            "頑張りながら、",
            "頑張りながらなんですね",
        ),
    ],
)
def test_spacy_katsuyo_text_detector_setsuzokujoshi(nlp_ja, msg, text, expected):
    sent = next(nlp_ja(text).sents)
    # 形態素解析の簡易化のために付与していた読点「、」を除去
    sent = sent[:-1]
    result = build(sent)
    assert result == expected, msg
