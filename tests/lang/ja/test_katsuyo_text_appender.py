import pytest
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    KatsuyoText,
)
from spacy_dialog_reflection.lang.ja.katsuyo import (
    GODAN_BA_GYO,
    KA_GYO_HENKAKU_KURU,
    KEIYOUSHI,
    RARERU,
    RERU,
    SASERU,
    SERU,
)
from spacy_dialog_reflection.lang.ja.katsuyo_text_appender import (
    Nai,
    IKatsuyoTextAppender,
    Shieki,
    Ukemi,
)
from spacy_dialog_reflection.lang.ja.katsuyo_text_builder import (
    SpacyKatsuyoTextBuilder,
)


@pytest.fixture(scope="session")
def append_multiple():
    return SpacyKatsuyoTextBuilder().append_multiple


@pytest.mark.parametrize(
    "katsuyo_text, expected",
    [
        # TODO もっとテストケースを増やす
        (
            KatsuyoText(
                gokan="",
                katsuyo=KA_GYO_HENKAKU_KURU,
            ),
            KatsuyoText(
                gokan="こ",
                katsuyo=RARERU,
            ),
        ),
        (
            KatsuyoText(
                gokan="遊",
                katsuyo=GODAN_BA_GYO,
            ),
            KatsuyoText(
                gokan="遊ば",
                katsuyo=RERU,
            ),
        ),
    ],
)
def test_zohdoushi_appender_ukemi(katsuyo_text, expected):
    zohdoushi_appender = Ukemi()
    result = zohdoushi_appender.append(katsuyo_text)
    assert str(result) == str(expected)


@pytest.mark.parametrize(
    "katsuyo_text, expected",
    [
        # TODO もっとテストケースを増やす
        (
            KatsuyoText(
                gokan="",
                katsuyo=KA_GYO_HENKAKU_KURU,
            ),
            KatsuyoText(
                gokan="こ",
                katsuyo=SASERU,
            ),
        ),
        (
            KatsuyoText(
                gokan="遊",
                katsuyo=GODAN_BA_GYO,
            ),
            KatsuyoText(
                gokan="遊ば",
                katsuyo=SERU,
            ),
        ),
    ],
)
def test_zohdoushi_appender_shieki(katsuyo_text, expected):
    zohdoushi_appender = Shieki()
    result = zohdoushi_appender.append(katsuyo_text)
    assert str(result) == str(expected)


@pytest.mark.filterwarnings("ignore:ValueError")
@pytest.mark.filterwarnings("ignore:Invalid appender")
def test_katsuyo_text_warning_value_error(append_multiple):
    class AppenderRaiseValueError(IKatsuyoTextAppender):
        def append(self, _):
            raise ValueError("HOGE")

    katsuyo_text = KatsuyoText(
        gokan="",
        katsuyo=KA_GYO_HENKAKU_KURU,
    )
    katsuyo_text_appenders = [
        AppenderRaiseValueError(),
    ]
    result, has_error = append_multiple(
        katsuyo_text,
        katsuyo_text_appenders,
    )
    assert result == katsuyo_text, "No changes"
    assert has_error, "has_error is True"


@pytest.mark.parametrize(
    "katsuyo_text, expected",
    [
        # TODO もっとテストケースを増やす
        # TODO 「らしい」など未然形が存在しないケースを追加
        (
            KatsuyoText(
                gokan="",
                katsuyo=KA_GYO_HENKAKU_KURU,
            ),
            KatsuyoText(
                gokan="こな",
                katsuyo=KEIYOUSHI,
            ),
        ),
        (
            KatsuyoText(
                gokan="遊",
                katsuyo=GODAN_BA_GYO,
            ),
            KatsuyoText(
                gokan="遊ばな",
                katsuyo=KEIYOUSHI,
            ),
        ),
    ],
)
def test_zohdoushi_appender_Nai(katsuyo_text, expected):
    zohdoushi_appender = Nai()
    result = zohdoushi_appender.append(katsuyo_text)
    assert str(result) == str(expected)


@pytest.mark.filterwarnings("ignore:None value TypeError Detected")
@pytest.mark.filterwarnings("ignore:Invalid appender")
def test_katsuyo_text_warning_none_type_error(append_multiple):
    class AppenderRaiseTypeError(IKatsuyoTextAppender):
        def append(self, _):
            return KatsuyoText(
                # raise TypeError
                gokan="あ" + None,
                katsuyo=KA_GYO_HENKAKU_KURU,
            )

    katsuyo_text = KatsuyoText(
        gokan="",
        katsuyo=KA_GYO_HENKAKU_KURU,
    )
    katsuyo_text_appenders = [
        AppenderRaiseTypeError(),
    ]
    result, has_error = append_multiple(
        katsuyo_text,
        katsuyo_text_appenders,
    )
    assert result == katsuyo_text, "No changes"
    assert has_error, "has_error is True"
