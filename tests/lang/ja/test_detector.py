# NOTE: あくまでテスト用
# TODO JaSpacyReflectionTextBuilder に移植
from typing import Optional
import pytest
import re

JODOUSHI_REGEXP = re.compile(r"^助動詞-(ダ|デス|マス)")


def cut_suffix_until_valid(sent) -> Optional[str]:
    if len(sent) == 0:
        return None

    for i in reversed(range(0, len(sent))):
        token = sent[i]
        tag = token.tag_
        match tag:
            case "助動詞":
                # sudachiの形態素解析結果(part_of_speech)5つ目以降(活用タイプ、活用形)が格納される
                # 品詞によっては活用タイプ、活用形が存在しないため、ここでは配列の取得のみ行う
                # e.g. 動詞
                # > m.part_of_speech() # => ['動詞', '一般', '*', '*', '下一段-バ行', '連用形-一般']
                # ref. https://github.com/explosion/spaCy/blob/v3.4.1/spacy/lang/ja/__init__.py#L102
                # ref. https://github.com/WorksApplications/SudachiPy/blob/v0.5.4/README.md
                # > Returns the part of speech as a six-element tuple. Tuple elements are four POS levels, conjugation type and conjugation form.
                # ref. https://worksapplications.github.io/sudachi.rs/python/api/sudachipy.html#sudachipy.Morpheme.part_of_speech
                inflection = token.morph.get("Inflection")[0].split(";")
                conjugation_type = inflection[0]
                if JODOUSHI_REGEXP.match(conjugation_type):
                    continue
            case "助詞-準体助詞":
                continue
        break

    return sent[: i + 1]


@pytest.mark.parametrize(
    "msg, text, expected",
    [
        # ref, https://ja.wikipedia.org/wiki/五段活用
        (
            "五段活用",
            "あなたと歩く",
            "あなたと歩く",
        ),
        (
            "五段活用",
            "あなたと稼ぐ",
            "あなたと稼ぐ",
        ),
        (
            "五段活用",
            "あなたと話す",
            "あなたと話す",
        ),
        (
            "五段活用",
            "あなたと待つ",
            "あなたと待つ",
        ),
        (
            "五段活用",
            "あなたと死ぬ",
            "あなたと死ぬ",
        ),
        (
            "五段活用",
            "あなたと遊ぶ",
            "あなたと遊ぶ",
        ),
        (
            "五段活用",
            "本を読む",
            "本を読む",
        ),
        (
            "五段活用",
            "あなたと帰る",
            "あなたと帰る",
        ),
        (
            "五段活用",
            "あなたと買う",
            "あなたと買う",
        ),
        # ref, https://ja.wikipedia.org/wiki/上一段活用
        (
            "上一段活用",
            "あなたと老いる",
            "あなたと老いる",
        ),
        (
            "上一段活用",
            "あなたと居る",
            "あなたと居る",
        ),
        (
            "上一段活用",
            "あなたといる",
            "あなたといる",
        ),
        (
            "上一段活用",
            "あなたと起きる",
            "あなたと起きる",
        ),
        (
            "上一段活用",
            "あなたと着る",
            "あなたと着る",
        ),
        (
            "上一段活用",
            "過ぎる",
            "過ぎる",
        ),
        (
            "上一段活用",
            "あなたと閉じる",
            "あなたと閉じる",
        ),
        (
            "上一段活用",
            "あなたと落ちる",
            "あなたと落ちる",
        ),
        (
            "上一段活用",
            "野菜を煮る",
            "野菜を煮る",
        ),
        (
            "上一段活用",
            "日差しを浴びる",
            "日差しを浴びる",
        ),
        (
            "上一段活用",
            "目に染みる",
            "目に染みる",
        ),
        (
            "上一段活用",
            "目を見る",
            "目を見る",
        ),
        (
            "上一段活用",
            "下に降りる",
            "下に降りる",
        ),
        # ref, https://ja.wikipedia.org/wiki/下一段活用
        (
            "下一段活用",
            "下に見える",
            "下に見える",
        ),
        (
            "下一段活用",
            "報酬を得る",
            "報酬を得る",
        ),
        (
            "下一段活用",
            "罰を受ける",
            "罰を受ける",
        ),
        (
            "下一段活用",
            "宣告を告げる",
            "宣告を告げる",
        ),
        (
            "下一段活用",
            "映像を見せる",
            "映像を見せる",
        ),
        (
            "下一段活用",
            "小麦粉を混ぜる",
            "小麦粉を混ぜる",
        ),
        (
            "下一段活用",
            "小麦粉を捨てる",
            "小麦粉を捨てる",
        ),
        (
            "下一段活用",
            "うどんを茹でる",
            "うどんを茹でる",
        ),
        (
            "下一段活用",
            "出汁が出る",
            "出汁が出る",
        ),
        (
            "下一段活用",
            "親戚を尋ねる",
            "親戚を尋ねる",
        ),
        (
            "下一段活用",
            "すぐに寝る",
            "すぐに寝る",
        ),
        (
            "下一段活用",
            "時を経る",
            "時を経る",
        ),
        (
            "下一段活用",
            "ご飯を食べる",
            "ご飯を食べる",
        ),
        (
            "下一段活用",
            "ご飯を求める",
            "ご飯を求める",
        ),
        (
            "下一段活用",
            "麺を入れる",
            "麺を入れる",
        ),
        # 「いく」のみ特殊
        (
            "五段活用",
            "あなたといく",
            "あなたといく",
        ),
        # ref. https://ja.wikipedia.org/wiki/カ行変格活用
        (
            "カ行変格活用",
            "家にくる",
            "家にくる",
        ),
        (
            "カ行変格活用",
            "家に来る",
            "家に来る",
        ),
        # ref. https://ja.wikipedia.org/wiki/サ行変格活用
        (
            "サ行変格活用",
            "軽くウォーキングする",
            "軽くウォーキングする",
        ),
        (
            "サ行変格活用",
            "フライパンを熱する",
            "フライパンを熱する",
        ),
        (
            "サ行変格活用",
            "影響が生ずる",
            "影響が生ずる",
        ),
        # 形容詞
        (
            "形容詞",
            "あなたは美しい",
            "あなたは美しい",
        ),
        # TODO 省略を実装したら直す
        # # 形容動詞
        # (
        #     "形容動詞",
        #     "あなたは傲慢だ",
        #     "傲慢",
        # ),
        # 名詞
        (
            "名詞",
            "それは明日",
            "それは明日",
        ),
        # 固有名詞
        (
            "固有名詞",
            "それはステファン",
            "それはステファン",
        ),
        # 代名詞
        (
            "代名詞",
            "それはそれ",
            "それはそれ",
        ),
    ],
)
def test_spacy_katsuyo_text_detector(nlp_ja, msg, text, expected):
    sent = next(nlp_ja(text).sents)
    result = cut_suffix_until_valid(sent)
    assert result.text == expected, msg


@pytest.mark.parametrize(
    "msg, text, expected",
    [
        # ref. https://ja.wikipedia.org/wiki/助詞#格助詞
        (
            "格助詞「が」",
            "それが",
            "それが",
        ),
        (
            "格助詞「の」",
            "それの",
            "それの",
        ),
        (
            "格助詞「を」",
            "それを",
            "それを",
        ),
        (
            "格助詞「に」",
            "それに",
            "それに",
        ),
        (
            "格助詞「へ」",
            "それへ",
            "それへ",
        ),
        (
            "格助詞「と」",
            "それと",
            "それと",
        ),
        (
            "格助詞「から」",
            "それから",
            "それから",
        ),
        (
            "格助詞「より」",
            "それより",
            "それより",
        ),
        (
            "格助詞「で」",
            "それで",
            "それで",
        ),
        # ref. https://ja.wikipedia.org/wiki/助詞#並列助詞
        (
            "並列助詞「の」",
            "それの",
            "それの",
        ),
        (
            "並列助詞「に」",
            "それに",
            "それに",
        ),
        (
            "並列助詞「と」",
            "それと",
            "それと",
        ),
        (
            "並列助詞「や」",
            "それや",
            "それや",
        ),
        (
            "並列助詞「し」",
            "それし",
            "それし",
        ),
        (
            "並列助詞「やら」",
            "それやら",
            "それやら",
        ),
        (
            "並列助詞「か」",
            "それか",
            "それか",
        ),
        (
            "並列助詞「なり」",
            "それなり",
            "それなり",
        ),
        (
            "並列助詞「だの」",
            "それだの",
            "それだの",
        ),
        # ref. https://ja.wikipedia.org/wiki/助詞#副助詞
        (
            "副助詞「ばかり」",
            "そればかり",
            "そればかり",
        ),
        (
            "副助詞「まで」",
            "それまで",
            "それまで",
        ),
        (
            "副助詞「ほど」",
            "それほど",
            "それほど",
        ),
        (
            "副助詞「くらい」",
            "それくらい",
            "それくらい",
        ),
        (
            "副助詞「ぐらい」",
            "それぐらい",
            "それぐらい",
        ),
        (
            "副助詞「の」",
            "それの",
            "それの",
        ),
        (
            "副助詞「など」",
            "それなど",
            "それなど",
        ),
        (
            "副助詞「なり」",
            "それなり",
            "それなり",
        ),
        (
            "副助詞「やら」",
            "それやら",
            "それやら",
        ),
        (
            "副助詞「か」",
            "それか",
            "それか",
        ),
        (
            "副助詞「がてら」",
            "それがてら",
            "それがてら",
        ),
        (
            "副助詞「かり」",
            "そればっかり",
            "そればっかり",
        ),
        (
            "副助詞「ずつ」",
            "それずつ",
            "それずつ",
        ),
        (
            "副助詞「のみ」",
            "それのみ",
            "それのみ",
        ),
        (
            "副助詞「きり」",
            "それきり",
            "それきり",
        ),
        (
            "副助詞「や」",
            "あれやそれや",
            "あれやそれや",
        ),
        # ref. https://ja.wikipedia.org/wiki/助詞#係助詞
        (
            "係助詞「は」",
            "そういうことでは",
            "そういうことでは",
        ),
        (
            "係助詞「も」",
            "そういうことも",
            "そういうことも",
        ),
        (
            "係助詞「こそ」",
            "そういうことこそ",
            "そういうことこそ",
        ),
        (
            "係助詞「でも」",
            "そういうことでも",
            "そういうことでも",
        ),
        (
            "係助詞「しか」",
            "そういうことしか",
            "そういうことしか",
        ),
        (
            "係助詞「さえ」",
            "そういうことさえ",
            "そういうことさえ",
        ),
        # ref. https://ja.wikipedia.org/wiki/助詞#準体助詞
        (
            "準体助詞「ん」",
            "頑張ってるん",
            "頑張ってる",
        ),
        (
            "準体助詞「の」",
            "頑張ってるの",
            "頑張ってる",
        ),
        # NOTE: 「から」は格助詞として識別されることと、本ライブラリもそれに準ずる
        # (
        #     "準体助詞「から」",
        #     "着いてから",
        #     "着いてから",
        # ),
    ],
)
def test_spacy_katsuyo_text_detector_joshi(nlp_ja, msg, text, expected):
    sent = next(nlp_ja(text).sents)
    result = cut_suffix_until_valid(sent)
    assert result.text == expected, msg


@pytest.mark.parametrize(
    "msg, text, expected",
    [
        # ref. https://ja.wikipedia.org/wiki/助動詞_(国文法)
        (
            "助動詞「だ」",
            "それだ",
            "それ",
        ),
        (
            "助動詞「です」",
            "それです",
            "それ",
        ),
        (
            "助動詞「ます」",
            "楽しみます",
            "楽しみ",
        ),
    ],
)
def test_spacy_katsuyo_text_detector_jodoushi(nlp_ja, msg, text, expected):
    sent = next(nlp_ja(text).sents)
    result = cut_suffix_until_valid(sent)
    assert result.text == expected, msg
