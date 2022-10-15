from tkinter import E
import pytest
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    KatsuyoText,
)
from spacy_dialog_reflection.lang.ja.katsuyo import (
    KEIYOUDOUSHI,
    KEIYOUSHI,
)
from spacy_dialog_reflection.lang.ja.katsuyo_text_appender import Ukemi
from spacy_dialog_reflection.lang.ja.katsuyo_text_detector import (
    SpacyKatsuyoTextAppenderDetector,
    SpacyKatsuyoTextDetector,
)


@pytest.fixture(scope="session")
def spacy_detector():
    return SpacyKatsuyoTextDetector()


@pytest.fixture(scope="session")
def spacy_appender_detector():
    appender_dict = {
        Ukemi: Ukemi(),
    }
    return SpacyKatsuyoTextAppenderDetector(appender_dict)


@pytest.mark.parametrize(
    "text, root, pos, expected",
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
def test_spacy_katsuyo_text_detector(nlp_ja, spacy_detector, text, root, pos, expected):
    root_token = next(nlp_ja(text).sents).root
    assert root_token.text == root, "root token is not correct"
    assert root_token.pos_ == pos, "root token is not correct"
    result = spacy_detector.detect(root_token)
    assert str(result) == str(expected)


@pytest.mark.parametrize(
    "text, norm, pos, expected",
    [
        (
            "あなたに愛される",
            "れる",
            "AUX",
            [
                Ukemi,
            ],
        ),
    ],
)
def test_spacy_katsuyo_text_appender_detector(
    nlp_ja, spacy_appender_detector, text, norm, pos, expected
):
    sent = next(nlp_ja(text).sents)
    last_token = sent[-1]
    assert last_token.norm_ == norm, "last token is not correct"
    assert last_token.pos_ == pos, "last token is not correct"
    result, has_error = spacy_appender_detector.detect(sent)
    assert not has_error, "has error in detection"
    types = [type(appender) for appender in result]
    assert types == expected
