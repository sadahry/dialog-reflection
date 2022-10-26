import pytest
from spacy_dialog_reflection.lang.ja.katsuyo import (
    GODAN_BA_GYO,
    GODAN_KA_GYO,
    GODAN_SA_GYO,
    KAMI_ICHIDAN,
    SHIMO_ICHIDAN,
)
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    KURU_KANJI,
    SURU,
    KatsuyoText,
)


@pytest.mark.parametrize(
    "msg, katsuyo_text1, katsuyo_text2, expected",
    [
        # NOTE: このテストではあくまで文法的なパターンを記載しているのみであり、
        #       すべてのパターンで自然な結果を返すことを保証していない。
        #
        #       たとえば「来る」＋「みる」=「来てみる」が自然だといえそうだが
        #       この加算式では「来みる」になる。
        #
        #       自然な結果の出力はIKatsuyoTextHeplerの実装方式に依存する。
        (
            "五段活用",
            KatsuyoText(
                gokan="遊",
                katsuyo=GODAN_BA_GYO,
            ),
            KatsuyoText(
                gokan="歩",
                katsuyo=GODAN_KA_GYO,
            ),
            "遊び歩く",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            KatsuyoText(
                gokan="歩",
                katsuyo=GODAN_KA_GYO,
            ),
            "見歩く",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="蹴",
                katsuyo=SHIMO_ICHIDAN,
            ),
            KatsuyoText(
                gokan="飛ば",
                katsuyo=GODAN_SA_GYO,
            ),
            "蹴飛ばす",
        ),
        (
            "カ変活用",
            KURU_KANJI,
            KatsuyoText(
                gokan="すぎ",
                katsuyo=KAMI_ICHIDAN,
            ),
            "来すぎる",
        ),
        (
            "サ変活用",
            SURU,
            KatsuyoText(
                gokan="直",
                katsuyo=GODAN_SA_GYO,
            ),
            "し直す",
        ),
    ],
)
def test_add(msg, katsuyo_text1, katsuyo_text2, expected):
    assert str(katsuyo_text1 + katsuyo_text2) == expected, msg


def test_error():
    with pytest.raises(BaseException):
        KURU_KANJI + 1


# TODO KatsuyoText x INonKatsuyoText のテストを追加する

# TODO ZyodoushiKatsuyoTextなど活用系のテストを追加する
