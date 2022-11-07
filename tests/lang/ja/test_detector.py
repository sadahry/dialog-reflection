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


class DialectNotSupported(CancelledReason):
    def __init__(self, token: Union[spacy.tokens.Token, str]):
        self.token = token


class CancelledByToken(CancelledReason):
    def __init__(self, sent: spacy.tokens.Span, token: Union[spacy.tokens.Token, str]):
        self.sent = sent
        self.token = token


class ReflectionCancelled(Exception):
    def __init__(
        self, *args: object, reason: CancelledReason = UnexpectedError()
    ) -> None:
        self.reason = reason
        super().__init__(*args)


INVALID_JODOUSHI_REGEXP = re.compile(r"^助動詞-(ダ|デス|マス)")
CANCEL_JODOUSHI_REGEXP = re.compile(r"^(助動詞-(ヌ|マイ)|文語助動詞-(ム|ベシ))")
DIALECT_JODOUSHI_REGEXP = re.compile(r"^助動詞-(ジャ|ドス|ナンダ|ヘン|ヤ|ヤス)")
INVALID_SETSUZOKUJOSHI_NORMS = {"が", "し", "て", "で", "に", "から", "けど", "けれど"}
DIALECT_SETSUZOKUJOSHI_NORMS = {"きに", "けん", "すけ", "さかい", "ばってん"}
INVALID_SHUJOSHI_NORMS = {
    "い",
    "え",
    "さ",
    "ぜ",
    "ぞ",
    "や",
    "な",
    "ね",
    "よ",
    "わ",
    "もの",
    "よん",
    "じゃん",
}
INVALID_FUKUJOSHI_NORMS = {
    "って",
}
CANCEL_SHUJOSHI_NORMS = {"か", "の", "かしら"}
DIALECT_SHUJOSHI_NORMS = {
    "で",
    "ど",
    "ラ",
    "かし",
    "ぞい",
    "たい",
    "ちょ",
    "てん",
    "ねん",
    "のう",
    "のん",
    "ばい",
    "ばや",
    "べい",
}


def cut_suffix_until_valid(sent: spacy.tokens.Span) -> Optional[spacy.tokens.Span]:
    if len(sent) == 0:
        return None

    for i in reversed(range(0, len(sent))):
        token = sent[i]
        tag = token.tag_
        conjugation_type, _ = get_conjugation(token)

        # break -> VALID
        # continue -> INVALID
        # raise -> CANCEL

        match tag:
            case ("感動詞-一般" | "感動詞-フィラー" | "連体詞"):
                continue
            case ("補助記号-読点" | "補助記号-句点"):
                if token.norm_ == "?":
                    raise ReflectionCancelled(reason=CancelledByToken(sent, token))
                continue
            case "助動詞":
                if INVALID_JODOUSHI_REGEXP.match(conjugation_type):
                    continue
                if CANCEL_JODOUSHI_REGEXP.match(conjugation_type):
                    raise ReflectionCancelled(reason=CancelledByToken(sent, token))
                if DIALECT_JODOUSHI_REGEXP.match(conjugation_type):
                    raise ReflectionCancelled(reason=DialectNotSupported(token))
            case "助詞-準体助詞":
                continue
            case "助詞-接続助詞":
                if token.norm_ in INVALID_SETSUZOKUJOSHI_NORMS:
                    continue
                if token.norm_ in DIALECT_SETSUZOKUJOSHI_NORMS:
                    raise ReflectionCancelled(reason=DialectNotSupported(token))
                break
            case "助詞-終助詞":
                if token.norm_ in INVALID_SHUJOSHI_NORMS:
                    continue
                if token.norm_ in CANCEL_SHUJOSHI_NORMS:
                    raise ReflectionCancelled(reason=CancelledByToken(sent, token))
                if token.norm_ in DIALECT_SHUJOSHI_NORMS:
                    raise ReflectionCancelled(reason=DialectNotSupported(token))
            case "助詞-副助詞":
                if token.norm_ in INVALID_FUKUJOSHI_NORMS:
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


# NOTE: 形態素解析のように正しく文書を分離することが目的ではないため
#       正しく文章が切断されていることまでを確認する


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
        # 形容動詞
        (
            "形容動詞",
            "あなたは傲慢だ",
            "あなたは傲慢",
        ),
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
        # 稀なケースであるため、機械的に文法から生成
        # 連体詞
        (
            "連体詞",
            "全然あるその",
            "全然ある",
        ),
        (
            "接頭辞",
            "いや超",
            "いや超",
        ),
        (
            "感動詞",
            "そういうことほら",
            "そういうこと",
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
        (
            "未然形",
            "あなたと歩かない",
        ),
        (
            "連用形",
            "あなたと歩き始める",
        ),
        (
            "終止形",
            "あなたと歩く。",
        ),
        (
            "連体形",
            "あなたと歩くため",
        ),
        (
            "仮定形",
            "あなたと歩けば",
        ),
        (
            "命令形",
            "あなたが歩けよな",
        ),
        (
            "意志推量形",
            "あなたと歩こうか",
        ),
    ],
)
def test_spacy_katsuyo_text_detector_with_no_error_as_conjugation_form(
    nlp_ja, msg, text
):
    sent = next(nlp_ja(text).sents)
    # 活用形を取り出しやすくするために付与した単語を除く
    tokens = sent[:-1]
    tokens = cut_suffix_until_valid(tokens)
    assert tokens is not None, msg


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
        # 例外的なケース
        (
            "副助詞「って」",
            "それって",
            "それ",
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
        # ref, https://ja.wikipedia.org/wiki/助詞#接続助詞
        # ref. http://sudachi.s3-website-ap-northeast-1.amazonaws.com/sudachidict-raw/20221021/small_lex.zip
        # ・仮定の順接「ば」「ても」「ところで」「たって」 ・仮定の逆説「と」「ど」「とて」「とも」
        # ・確定の順接「ので」「から」「て」「で」 ・並列「し」「なり」「たり」
        # ・確定の逆接「けれど」「けど※2」「が」「のに※3」「ものの」「いえども」
        # ・するとすぐに「や※3」 ・「まま※3」 ・動作の並行「ながら」「つつ」
        (
            "接続助詞「が」",
            "頑張ったが、",
            "頑張った",
        ),
        (
            "接続助詞「し」",
            "頑張ったし、",
            "頑張った",
        ),
        (
            "接続助詞「て」",
            "頑張って、",
            "頑張っ",
        ),
        (
            "接続助詞「で」",
            "遊んで、",
            "遊ん",
        ),
        (
            "接続助詞「ので」",
            "頑張るので、",
            "頑張る",
        ),
        (
            "接続助詞「と」",
            "頑張ると、",
            "頑張ると",
        ),
        (
            "接続助詞「ど」",
            "頑張れど、",
            "頑張れど",
        ),
        (
            "接続助詞「ば」",
            "頑張ってれば",
            "頑張ってれば",
        ),
        (
            "接続助詞「から」",
            "頑張るから、",
            "頑張る",
        ),
        (
            "接続助詞「けど」",
            "頑張るけど、",
            "頑張る",
        ),
        (
            "接続助詞「つつ」",
            "頑張りつつ",
            "頑張りつつ",
        ),
        (
            "接続助詞「ては」",
            "頑張っては、",
            "頑張っては",  # 「ては」では接続助詞となりづらかったため追加
        ),
        (
            "接続助詞「ては」",
            "頑張っちゃあ、",
            "頑張っちゃあ",  # 「ては」では接続助詞となりづらかったため追加
        ),
        (
            "接続助詞「とて」",
            "頑張ったとて、",
            "頑張ったとて",
        ),
        (
            "接続助詞「とも」",
            "何をしようとも、",
            "何をしようとも",  # 終助詞になる
        ),
        (
            "接続助詞「なり」",
            "頑張るなり、",
            "頑張るなり",
        ),
        (
            "接続助詞「けれど」",
            "頑張ったけれど、",
            "頑張った",
        ),
        (
            "接続助詞「たって」",
            "頑張ったって、",
            "頑張ったって",
        ),
        (
            "接続助詞「ながら」",
            "頑張りながら、",
            "頑張りながら",
        ),
    ],
)
def test_spacy_katsuyo_text_detector_joshi(nlp_ja, msg, text, expected):
    sent = next(nlp_ja(text).sents)
    result = cut_suffix_until_valid(sent)
    assert result.text == expected, msg


@pytest.mark.parametrize(
    "msg, text, expected",
    [
        (
            "補助記号-読点",
            "遊ぶ、",
            "遊ぶ",
        ),
        (
            "補助記号-句点",
            "遊ぶ。",
            "遊ぶ",
        ),
        (
            "補助記号-句点",
            "遊ぶ！",
            "遊ぶ",
        ),
    ],
)
def test_spacy_katsuyo_text_detector_kigo(nlp_ja, msg, text, expected):
    sent = next(nlp_ja(text).sents)
    result = cut_suffix_until_valid(sent)
    assert result.text == expected, msg


@pytest.mark.parametrize(
    "msg, text, will_cancel",
    [
        (
            "補助記号-句点",
            "遊ぶ？",
            True,
        ),
        (
            "補助記号-句点",
            "遊ぶ？",
            True,
        ),
        (
            "補助記号-句点",
            "遊ぶ？って尋ねた",
            False,
        ),
    ],
)
def test_spacy_katsuyo_text_detector_kigo_cancel(nlp_ja, msg, text, will_cancel):
    sent = next(nlp_ja(text).sents)
    if will_cancel:
        with pytest.raises(ReflectionCancelled):
            cut_suffix_until_valid(sent)
            assert False, msg
    else:
        cut_suffix_until_valid(sent)


@pytest.mark.parametrize(
    "msg, text, expected",
    [
        # ref. https://ja.wikipedia.org/wiki/助詞#終助詞
        (
            "終助詞「い」",
            "遊ぶだろうがい",
            "遊ぶ",
        ),
        # 『日本語日常コーパス』に用例がないためスキップ
        # (
        #     "終助詞「え」",
        # ),
        (
            "終助詞「さ」",
            "知ってるさ",
            "知ってる",
        ),
        (
            "終助詞「ぜ」",
            "知ってるぜ",
            "知ってる",
        ),
        (
            "終助詞「ぞ」",
            "知ってるぞ",
            "知ってる",
        ),
        (
            "終助詞「な」",
            "知ってるな",
            "知ってる",
        ),
        (
            "終助詞「ね」",
            "知ってるね",
            "知ってる",
        ),
        (
            "終助詞「や」",
            "どうしようもないや",
            "どうしようもない",
        ),
        (
            "終助詞「よ」",
            "わかったよ",
            "わかった",
        ),
        (
            "終助詞「わ」",
            "わかったわ",
            "わかった",
        ),
        # 終助詞としての用例が存在しない。ただ副助詞的に「かも」が取れる
        # 文章としてはVALIDなので現状は取り除かない
        (
            "助詞「かも」",
            "知ってるかも",
            "知ってるかも",
        ),
        (
            "終助詞「もの」",
            "わかってるもん",
            "わかってる",
        ),
        (
            "終助詞「よん」",
            "わかってるよん",
            "わかってる",
        ),
        (
            "終助詞「じゃん」",
            "わかってるじゃん",
            "わかってる",
        ),
        (
            "終助詞「のに」",
            "頑張ってるのに",
            "頑張ってるのに",
        ),
    ],
)
def test_spacy_katsuyo_text_detector_shujoshi(nlp_ja, msg, text, expected):
    sent = next(nlp_ja(text).sents)
    result = cut_suffix_until_valid(sent)
    assert result.text == expected, msg


@pytest.mark.parametrize(
    "msg, text, will_cancel",
    [
        (
            "終助詞「か」",
            "知ってるか",
            True,
        ),
        (
            "終助詞「の」",
            "知ってたの",
            True,
        ),
        (
            "終助詞「かしら」",
            "知ってたかしら",
            True,
        ),
    ],
)
def test_spacy_katsuyo_text_detector_shujoshi_cancel(nlp_ja, msg, text, will_cancel):
    sent = next(nlp_ja(text).sents)
    if will_cancel:
        with pytest.raises(ReflectionCancelled):
            cut_suffix_until_valid(sent)
            assert False, msg
    else:
        cut_suffix_until_valid(sent)


@pytest.mark.parametrize(
    "msg, text, will_cancel",
    [
        # NOTE: 厳格なチェックはしない
        #       （e.g., 方言のあとにVALIDな品詞を追加する）
        (
            "方言助詞「きに」",
            "知ってるきに",
            True,
        ),
        (
            "方言助詞「けん」",
            "知ってるけん",
            True,
        ),
        (
            "方言助詞「すけ」",
            "知ってるすけ",
            True,
        ),
        (
            "方言助詞「さかい」",
            "知ってるさかい",
            True,
        ),
        (
            "方言助詞「ばってん」",
            "知ってるばってん",
            True,
        ),
        (
            "方言助詞「で」",
            "知ってるやで",
            True,
        ),
        # 用例は存在するが形態素解析で終助詞とならないためスキップ
        # (
        #     "方言助詞「ど」",
        #     "知ってるど",
        #     True,
        # ),
        (
            "方言助詞「ラ」",
            "すごいら",
            True,
        ),
        # 用例が存在しないためスキップ
        # (
        #     "方言助詞「哉」",
        #     "知ってる哉",
        #     True,
        # ),
        # https://chunagon.ninjal.ac.jp/cejc/permalink?unit=short&position=T007_005a,12160
        (
            "方言助詞「かし」",
            "帰っちゃうかし",
            True,
        ),
        # 用例が存在しないためスキップ
        # (
        #     "方言助詞「くさ」",
        #     "知ってるくさ",
        #     True,
        # ),
        (
            "方言助詞「ぞい」",
            "知ってるぞい",
            True,
        ),
        # 用例が存在しないためスキップ
        # (
        #     "方言助詞「ちょ」",
        #     "頑張るちょ",
        #     True,
        # ),
        (
            "方言助詞「てん」",
            "びっくりしててん",
            True,
        ),
        (
            "方言助詞「ねん」",
            "びっくりしてんねん",
            True,
        ),
        (
            "方言助詞「のう」",
            "びっくりしてんのう",
            True,
        ),
        (
            "方言助詞「のん」",
            "びっくりしてんのん",
            True,
        ),
        (
            "方言助詞「ばい」",
            "びっくりするばい",
            True,
        ),
        (
            "方言助詞「ばや」",
            "いかんばや",
            True,
        ),
        (
            "方言助詞「べい」",
            "いかんべ",
            True,
        ),
        # 用例が存在しないためスキップ
        # (
        #     "方言助詞「もが」",
        #     "頑張るもが",
        #     True,
        # ),
    ],
)
def test_spacy_katsuyo_text_detector_joshi_dialect_cancel(
    nlp_ja, msg, text, will_cancel
):
    sent = next(nlp_ja(text).sents)
    if will_cancel:
        with pytest.raises(ReflectionCancelled) as e:
            cut_suffix_until_valid(sent)
            assert False, msg
        type(e.value.reason) is DialectNotSupported, msg
    else:
        cut_suffix_until_valid(sent)


@pytest.mark.parametrize(
    "msg, text, expected",
    [
        # ref. https://ja.wikipedia.org/wiki/助動詞_(国文法)
        (
            "助動詞「れる」",
            "報われる",
            "報われる",
        ),
        (
            "助動詞「られる」",
            "見られる",
            "見られる",
        ),
        (
            "助動詞「せる」",
            "報わせる",
            "報わせる",
        ),
        (
            "助動詞「させる」",
            "見させる",
            "見させる",
        ),
        (
            "助動詞「ない」",
            "見ない",
            "見ない",
        ),
        (
            "助動詞「たい」",
            "見たい",
            "見たい",
        ),
        (
            "助動詞「たがる」",
            "話したがる",
            "話したがる",
        ),
        (
            "助動詞「た」",
            "見た",
            "見た",
        ),
        (
            "助動詞「だ」",
            "読んだ",
            "読んだ",
        ),
        (
            "助動詞「そうだ」",
            "見そうだ",
            "見そう",  # 「だ」が抜ける
        ),
        (
            "助動詞「らしい」",
            "見るらしい",
            "見るらしい",
        ),
        (
            "助動詞「ようだ」",
            "見るようだ",
            "見るよう",  # 「だ」が抜ける
        ),
        # INVALID
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
            "助動詞「です」",
            "楽しいんです",
            "楽しい",
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
            "助動詞「べし」",
            "あるべし",
            True,
        ),
        (
            "助動詞「ん」",
            "あるべきだ",
            True,
        ),
        (
            "助動詞「ん」",
            "あるべきでない",
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
    ],
)
def test_spacy_katsuyo_text_detector_jodoushi_cancel(nlp_ja, msg, text, will_cancel):
    sent = next(nlp_ja(text).sents)
    if will_cancel:
        with pytest.raises(ReflectionCancelled) as e:
            cut_suffix_until_valid(sent)
            assert False, msg
        type(e.value.reason) is DialectNotSupported, msg
    else:
        cut_suffix_until_valid(sent)


@pytest.mark.parametrize(
    "msg, text, will_cancel",
    [
        # NOTE: 厳格なチェックはしない
        #       （e.g., 方言のあとにVALIDな品詞を追加する）
        (
            "方言助動詞「じゃ」",
            "そうじゃ",
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
def test_spacy_katsuyo_text_detector_jodoushi_dialect_cancel(
    nlp_ja, msg, text, will_cancel
):
    sent = next(nlp_ja(text).sents)
    if will_cancel:
        with pytest.raises(ReflectionCancelled):
            cut_suffix_until_valid(sent)
            assert False, msg
    else:
        cut_suffix_until_valid(sent)
