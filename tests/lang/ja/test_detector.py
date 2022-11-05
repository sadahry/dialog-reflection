# NOTE: あくまでテスト用
# TODO JaSpacyReflectionTextBuilder に移植
from typing import Optional, Union
import pytest
import re
import spacy


class CancelledReason:
    pass


class UnexpectedError(CancelledReason):
    pass


class CancelledByToken(CancelledReason):
    def __init__(self, token: Union[spacy.tokens.Token, str]):
        self.token = token


class ReflectionCancelled(Exception):
    def __init__(
        self, *args: object, reason: CancelledReason = UnexpectedError()
    ) -> None:
        self.reason = reason
        super().__init__(*args)


INVALID_JODOUSHI_REGEXP = re.compile(r"^助動詞-(ダ|デス|マス)")
CANCEL_JODOUSHI_REGEXP = re.compile(r"^(助動詞-(ヌ|マイ|ジャ|タイ|ドス|ナンダ|ヘン|ヤ|ヤス)|文語助動詞-ム)")
CANCEL_KATSUYO_REGEXP = re.compile(r"意志推量形$")


def cut_suffix_until_valid(sent) -> Optional[str]:
    if len(sent) == 0:
        return None

    for i in reversed(range(0, len(sent))):
        token = sent[i]
        tag = token.tag_
        conjugation_type, conjugation_form = get_conjugation(token)

        if conjugation_form and CANCEL_KATSUYO_REGEXP.match(conjugation_form):
            raise ReflectionCancelled(reason=CancelledByToken(token))

        match tag:
            case "助動詞":
                if INVALID_JODOUSHI_REGEXP.match(conjugation_type):
                    continue
                if CANCEL_JODOUSHI_REGEXP.match(conjugation_type):
                    raise ReflectionCancelled(reason=CancelledByToken(token))
            case "助詞-準体助詞":
                continue
        break

    return sent[: i + 1]


def get_conjugation(token):
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
        # 接尾辞
        (
            "接尾辞-名詞的",
            "田中さん",
            "田中さん",
        ),
        (
            "接尾辞-動詞的",
            "田中ぶる",
            "田中ぶる",
        ),
        (
            "接尾辞-形容詞的",
            "田中っぽい",
            "田中っぽい",
        ),
        (
            "接尾辞-形状詞的",
            "田中だらけ",
            "田中だらけ",
        ),
    ],
)
def test_spacy_katsuyo_text_detector(nlp_ja, msg, text, expected):
    sent = next(nlp_ja(text).sents)
    result = cut_suffix_until_valid(sent)
    assert result.text == expected, msg


@pytest.mark.parametrize(
    "msg, text",
    [
        # ref, https://ja.wikipedia.org/wiki/五段活用
        (
            "五段活用",
            "あなたと歩こう",
        ),
        (
            "五段活用",
            "あなたと稼ごう",
        ),
        (
            "五段活用",
            "あなたと話そう",
        ),
        (
            "五段活用",
            "あなたと話そ",  # う抜き
        ),
        (
            "五段活用",
            "あなたと待とう",
        ),
        (
            "五段活用",
            "あなたと死のう",
        ),
        (
            "五段活用",
            "あなたと遊ぼう",
        ),
        (
            "五段活用",
            "あなたと遊ぼ",  # う抜き
        ),
        (
            "五段活用",
            "本を読もう",
        ),
        (
            "五段活用",
            "あなたと帰ろう",
        ),
        (
            "五段活用",
            "あなたと買おう",
        ),
        # ref, https://ja.wikipedia.org/wiki/上一段活用
        (
            "上一段活用",
            "あなたと老いよう",
        ),
        (
            "上一段活用",
            "あなたと居よう",
        ),
        (
            "上一段活用",
            "あなたといよう",
        ),
        (
            "上一段活用",
            "あなたと起きよう",
        ),
        (
            "上一段活用",
            "あなたと着よう",
        ),
        (
            "上一段活用",
            "過ぎよう",
        ),
        (
            "上一段活用",
            "あなたと閉じよう",
        ),
        (
            "上一段活用",
            "あなたと落ちよう",
        ),
        (
            "上一段活用",
            "野菜を煮よう",
        ),
        (
            "上一段活用",
            "日差しを浴びよう",
        ),
        (
            "上一段活用",
            "日差しを浴びよっ",  # う抜き
            # "日差しを浴びよ",  # 命令形となるためスキップ
        ),
        (
            "上一段活用",
            "目に染みよう",
        ),
        (
            "上一段活用",
            "目を見よう",
        ),
        (
            "上一段活用",
            "下に降りよう",
        ),
        # ref, https://ja.wikipedia.org/wiki/下一段活用
        (
            "下一段活用",
            "下に見えよう",
        ),
        (
            "下一段活用",
            "報酬を得よう",
        ),
        (
            "下一段活用",
            "罰を受けよう",
        ),
        (
            "下一段活用",
            "宣告を告げよう",
        ),
        (
            "下一段活用",
            "映像を見せよう",
        ),
        (
            "下一段活用",
            "小麦粉を混ぜよう",
        ),
        (
            "下一段活用",
            "小麦粉を混ぜよっ",  # う抜き
            # "小麦粉を混ぜよ",  # 命令形となるためスキップ
        ),
        (
            "下一段活用",
            "小麦粉を捨てよう",
        ),
        (
            "下一段活用",
            "うどんを茹でよう",
        ),
        (
            "下一段活用",
            "出汁が出よう",
        ),
        (
            "下一段活用",
            "親戚を尋ねよう",
        ),
        (
            "下一段活用",
            "すぐに寝よう",
        ),
        (
            "下一段活用",
            "時を経よう",
        ),
        (
            "下一段活用",
            "ご飯を食べよう",
        ),
        (
            "下一段活用",
            "ご飯を求めよう",
        ),
        (
            "下一段活用",
            "麺を入れよう",
        ),
        # 「いく」のみ特殊
        (
            "五段活用",
            "あなたと行こ",
        ),
        (
            "五段活用",
            "あなたと行こう",
            # "あなたといこう", # 五段活用「憩う」となるためスキップ
        ),
        # ref. https://ja.wikipedia.org/wiki/カ行変格活用
        (
            "カ行変格活用",
            "家にこよう",
        ),
        (
            "カ行変格活用",
            "家に来よ",  # う抜き
        ),
        # ref. https://ja.wikipedia.org/wiki/サ行変格活用
        (
            "サ行変格活用",
            "軽くウォーキングしよ",
        ),
        (
            "サ行変格活用",
            "フライパンを熱しよう",
        ),
        (
            "サ行変格活用",
            "フライパンを熱そう",
        ),
        (
            "サ行変格活用",
            "影響が生じよう",
        ),
        # 形容詞
        (
            "形容詞",
            "あなたは美しかろう",
        ),
    ],
)
def test_spacy_katsuyo_text_detector_cancel_u(nlp_ja, msg, text):
    sent = next(nlp_ja(text).sents)
    with pytest.raises(ReflectionCancelled):
        cut_suffix_until_valid(sent)
        assert False, msg


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
        (
            "助動詞「ます」",
            "楽しんでます",
            # 楽しんでる
            "楽しんで",
        ),
        (
            "助動詞「ます」",
            "楽しいんです",
            "楽しい",
        ),
    ],
)
def test_spacy_katsuyo_text_detector_jodoushi(nlp_ja, msg, text, expected):
    sent = next(nlp_ja(text).sents)
    result = cut_suffix_until_valid(sent)
    assert result.text == expected, msg


@pytest.mark.parametrize(
    "msg, text, will_cancel",
    [
        # ref. https://ja.wikipedia.org/wiki/助動詞_(国文法)
        (
            "助動詞「ず」",
            "あらず",
            True,
        ),
        (
            "助動詞「ず」",
            "あらずだ",
            True,
        ),
        (
            "助動詞「ず」",
            "あらずでない",
            False,
        ),
        (
            "助動詞「ぬ」",
            "あらぬ",
            True,
        ),
        (
            "助動詞「ぬ」",
            "あらぬだ",
            True,
        ),
        (
            "助動詞「ぬ」",
            "あらぬでない",
            False,
        ),
        (
            "助動詞「ん」",
            "あらん",
            True,
        ),
        (
            "助動詞「ん」",
            "あらんのだ",
            True,
        ),
        (
            "助動詞「ん」",
            "あらんでない",
            False,
        ),
        (
            "助動詞「まい」",
            "あるまい",
            True,
        ),
        (
            "助動詞「まい」",
            "あるまいのだ",
            True,
        ),
        (
            "助動詞「まい」",
            "あるまいとのこと",
            False,
        ),
        # 方言
        (
            "方言助動詞「じゃ」",
            "そうじゃ",
            True,
        ),
        (
            "方言助動詞「たい」",
            "そうたい",
            True,
        ),
        (
            "方言助動詞「どす」",
            "そうなんどす",
            True,
        ),
        (
            "方言助動詞「なんだ」",
            "知らなんだ",
            True,
        ),
        (
            "方言助動詞「へん」",
            "知らへん",
            True,
        ),
        (
            "方言助動詞「や」",
            "知らんのや",
            True,
        ),
        (
            "方言助動詞「やす」",
            "おいでやす",
            True,
        ),
    ],
)
def test_spacy_katsuyo_text_detector_jodoushi_cancel(nlp_ja, msg, text, will_cancel):
    sent = next(nlp_ja(text).sents)
    if will_cancel:
        with pytest.raises(ReflectionCancelled):
            cut_suffix_until_valid(sent)
            assert False, msg
    else:
        cut_suffix_until_valid(sent)


@pytest.mark.parametrize(
    "msg, text",
    [
        (
            "助動詞「れる」",
            "報われよう",
        ),
        (
            "助動詞「られる」",
            "見られよう",
        ),
        (
            "助動詞「せる」",
            "報わせよう",
        ),
        (
            "助動詞「させる」",
            "見させよう",
        ),
        (
            "助動詞「ない」",
            "見なかろう",
        ),
        # 意志推量形が思いつかないためスキップ
        # (
        #     "助動詞「ぬ」",
        # ),
        # (
        #     "助動詞「ん」",
        # ),
        # (
        #     "助動詞「まい」",
        # ),
        (
            "助動詞「たい」",
            "見たかろう",
        ),
        (
            "助動詞「たがる」",
            "話したがろう",  # 機械的に文法から生成
            # 見たがろうだと不適席な係り受けとなる。稀だと判断し対応はしない
            # # text = 見
            # 1       見      見る    VERB    動詞-非自立可能 _       0       root    _       SpaceAfter=No|BunsetuBILabel=B|BunsetuPositionType=ROOT|Inf=上一段-マ行,連用形-一般|Reading=ミ
            # # text = たがろう
            # 1       たがろう        たがる  PROPN   助動詞  _       0       root    _       SpaceAfter=No|BunsetuBILabel=B|BunsetuPositionType=ROOT|NP_I|Inf=五段-ラ行,意志推量形|Reading=タガロウ
        ),
        # 意志推量形が思いつかないためスキップ
        # (
        #     "助動詞「た」",
        # ),
        # (
        #     "助動詞「だ」",
        # ),
        (
            "助動詞「ます」",
            "見ましょう",
        ),
        (
            "助動詞「ます」",
            "見ましょ",  # 「う」抜き
        ),
        (
            "助動詞「そうだ」",
            "見そうだろう",
        ),
        (
            "助動詞「そうだ」",
            "見そうだろ",  # 「う」抜き
        ),
        (
            "助動詞「らしい」",
            "見るらしかろう",  # 機械的に文法から生成
        ),
        (
            "助動詞「べきだ」",
            "見るべきだろう",
        ),
        (
            "助動詞「ようだ」",
            "見るようだろう",
        ),
        (
            "助動詞「だ」",
            "見るだろう",
        ),
        (
            "助動詞「です」",
            "見るでしょう",
        ),
        (
            "助動詞「です」",
            "見るでしょ",  # 「う」抜き
        ),
    ],
)
def test_spacy_katsuyo_text_detector_jodoushi_cancel_u(nlp_ja, msg, text):
    sent = next(nlp_ja(text).sents)
    with pytest.raises(ReflectionCancelled):
        cut_suffix_until_valid(sent)
        assert False, msg
