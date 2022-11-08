from typing import Callable, Set
from dialog_reflection.lang.ja.cancelled_reason import (
    WhTokenNotSupported,
    DialectNotSupported,
)
import attr
import re
import spacy

ExceptionToText = Callable[[BaseException], str]
WhTokenNotSupportedToText = Callable[[WhTokenNotSupported], str]
DialectNotSupportedToText = Callable[[DialectNotSupported], str]
TokensToText = Callable[[spacy.tokens.Span], str]
TokenToText = Callable[[spacy.tokens.Token], str]


@attr.define(frozen=True)
class JaSpacyPlainTextBuilderOption:
    # ========================================================================
    # For Extracting Tokens
    # ========================================================================
    # restrict root pos tags to facilitate handling of suffixes in Japanese
    # root: -VERB (29585; 52% instances), -NOUN (19528; 34% instances), -ADJ (3807; 7% instances), -PROPN (1508; 3% instances), -NUM (953; 2% instances), ...
    # https://universaldependencies.org/treebanks/ja_bccwj/ja_bccwj-dep-root.html
    allowed_root_pos_tags: Set[str] = {
        "VERB",
        "NOUN",
        "PROPN",
        "ADJ",
        "NUM",
    }
    forbidden_wh_norms: Set[str] = {
        "何",
        "何故",
        "誰",
        "いつ",
        "どこ",
        "どちら",
        "どう",
        "どの",
        "どれ",
        "どんな",
        "どっち",
        "幾ら",
        "幾つ",
        "?",
    }
    # ========================================================================
    # For Building Text (cut_suffix)
    # ========================================================================
    invalid_jodoushi_types: Set[str] = {
        "助動詞-ダ",
        "助動詞-デス",
        "助動詞-マス",
    }
    valid_jodoushi_types: Set[str] = {
        "助動詞-タ",
        "助動詞-タイ",
        "助動詞-ナイ",
        "助動詞-レル",
        "助動詞-ラシイ",
    }
    # 網羅はしない。あくまでWARNINGとして出すため
    dialect_jodoushi_types: Set[str] = {
        "助動詞-ジャ",
        "助動詞-ドス",
        "助動詞-ナンダ",
        "助動詞-ヘン",
        "助動詞-ヤ",
        "助動詞-ヤス",
    }
    invalid_setsuzokujoshi_norms: Set[str] = {
        "が",
        "し",
        "て",
        "で",
        "に",
        "から",
        "けど",
        "けれど",
    }
    valid_setsuzokujoshi_norms: Set[str] = {
        "と",
        "ど",
        "ば",
        "つつ",
        "ては",
        "とも",
        "とて",
        "なり",
        "たって",
        "ながら",
        "し",  # 終助詞的に扱われる用例が多いためVALIDに
        "というか",  # TODO ユーザー辞書での対応(spaCyモデルの再学習を含め)を実現する
    }
    dialect_setsuzokujoshi_norms = {
        "きに",
        "けん",
        "すけ",
        "さかい",
        "ばってん",
    }
    invalid_shujoshi_norms = {
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
    valid_shujoshi_norms: Set[str] = {
        "とも",  # 接続助詞「とも」の代用
    }
    dialect_shujoshi_norms: Set[str] = {
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
    invalid_fukujoshi_norms: Set[str] = {
        "って",  # 終助詞的に扱われる用例が多いためVALIDに
    }
    valid_fukujoshi_norms: Set[str] = set()
    invalid_keijoshi_norms: Set[str] = set()
    valid_keijoshi_norms: Set[str] = set()
    invalid_kakuoshi_norms: Set[str] = set()
    valid_kakuoshi_norms: Set[str] = set()
    # ========================================================================
    # For Building Text (finalize)
    # ========================================================================
    fn_suffix_taigen: TokenToText = lambda _: "なんですね。"
    fn_suffix_yougen: TokenToText = lambda _: "んですね。"
    taigen_suffix_pattern: re.Pattern = re.compile(r".*(名|代名|形状|助)詞")
    # ========================================================================
    # For Error Handling
    # ========================================================================
    fn_message_when_error: ExceptionToText = lambda _: "そうなんですね。"
    fn_suffix_ambiguous: TokensToText = (
        lambda tokens: tokens[-1].sent.root.text + "、ですか。"
    )
    fn_message_cancelled_by_token: TokenToText = (
        # 少しでもバリエーションを増やすため、用例の多いケースに例外的に対応
        lambda token: token.doc[token.sent.root.i :].text + "、と。"
        if token.tag_ == "助詞-終助詞" and token.norm_ in {"か", "の", "かしら"}
        else "そうなんですね。"
    )
    fn_message_when_wh_token: WhTokenNotSupportedToText = lambda _: "んー。"
    fn_message_dialect_not_supported: DialectNotSupportedToText = (
        lambda _: "すみません、方言はわからない言葉が多いです。出来れば標準語でお願いします。"
    )
