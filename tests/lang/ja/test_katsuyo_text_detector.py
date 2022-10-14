import pytest
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    KatsuyoText,
)
from spacy_dialog_reflection.lang.ja.katsuyo import (
    KEIYOUDOUSHI,
    KEIYOUSHI,
)
from spacy_dialog_reflection.lang.ja.katsuyo_text_detector import (
    SpacyKatsuyoTextDetector,
)


@pytest.fixture(scope="session")
def spacy_detector():
    return SpacyKatsuyoTextDetector()


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
