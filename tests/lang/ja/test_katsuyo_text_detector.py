import pytest
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    KatsuyoText,
)
from spacy_dialog_reflection.lang.ja.katsuyo import (
    KEIYOUDOUSHI,
    KEIYOUSHI,
)
from spacy_dialog_reflection.lang.ja.katsuyo_text_appender import Hitei, Shieki, Ukemi
from spacy_dialog_reflection.lang.ja.katsuyo_text_builder import SpacyKatsuyoTextBuilder


@pytest.fixture(scope="session")
def spacy_detector():
    return SpacyKatsuyoTextBuilder().root_detector


@pytest.fixture(scope="session")
def spacy_appender_detector():
    return SpacyKatsuyoTextBuilder().appender_detector


@pytest.mark.parametrize(
    "text, root_text, pos, expected",
    [
        (
            "あなたは美しい",
            "美しい",
            "ADJ",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
        ),
        (
            "あなたは傲慢だ",
            "傲慢",
            "ADJ",
            KatsuyoText(
                gokan="傲慢",
                katsuyo=KEIYOUDOUSHI,
            ),
        ),
        (
            "それは明日かな",
            "明日",
            "NOUN",
            KatsuyoText(
                gokan="明日",
                katsuyo=KEIYOUDOUSHI,
            ),
        ),
        (
            "それはステファンだ",
            "ステファン",
            "PROPN",
            KatsuyoText(
                gokan="ステファン",
                katsuyo=KEIYOUDOUSHI,
            ),
        ),
    ],
)
def test_spacy_katsuyo_text_detector(
    nlp_ja, spacy_detector, text, root_text, pos, expected
):
    sent = next(nlp_ja(text).sents)
    root_token = sent.root
    assert root_token.text == root_text, "root token is not correct"
    assert root_token.pos_ == pos, "root token is not correct"
    result = spacy_detector.detect(sent)
    assert str(result) == str(expected)


@pytest.mark.parametrize(
    "text, norm, pos, expected",
    [
        (
            "あなたに愛される",
            "れる",
            "AUX",
            [Ukemi],
        ),
        (
            "称号が与えられる",
            "られる",
            "AUX",
            [Ukemi],
        ),
        (
            "あなたを愛させる",
            "せる",
            "AUX",
            [Shieki],
        ),
        (
            "子供を寝させる",
            "させる",
            "AUX",
            [Shieki],
        ),
        (
            "子供を愛さない",
            "ない",
            "AUX",
            [Hitei],
        ),
        (
            "子供が寝ない",
            "ない",
            "AUX",
            [Hitei],
        ),
        (
            "それは仕方ない",
            "仕方無い",
            "ADJ",
            [],
        ),
        # 現状、Hiteiとして取れてしまう。言語の返答には
        # 直接的には関係ないので、現状はこのままとする。
        # TODO 「仕方が無い」のような、Hiteiとして取れるものを取れなくする
        # (
        #     "それは仕方がない",
        #     "無い",
        #     "ADJ",
        #     [],
        # ),
    ],
)
def test_spacy_katsuyo_text_appender_detector(
    nlp_ja, spacy_appender_detector, text, norm, pos, expected
):
    sent = next(nlp_ja(text).sents)
    last_token = sent[-1]
    assert last_token.norm_ == norm, "last token is not correct"
    assert last_token.pos_ == pos, "last token is not correct"
    appenders, has_error = spacy_appender_detector.detect(sent)
    assert not has_error, "has error in detection"
    appender_types = [type(appender) for appender in appenders]
    assert appender_types == expected
