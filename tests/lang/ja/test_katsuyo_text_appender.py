import pytest
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    KURU,
    KatsuyoText,
)
from spacy_dialog_reflection.lang.ja.katsuyo import (
    GODAN_BA_GYO,
    KA_GYO_HENKAKU_KURU,
    KAMI_ICHIDAN,
    KEIYOUSHI,
    RARERU,
    RERU,
    SA_GYO_HENKAKU_SURU,
    SA_GYO_HENKAKU_ZURU,
    SASERU,
    SERU,
    SHIMO_ICHIDAN,
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
        (
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            KatsuyoText(
                gokan="見",
                katsuyo=RARERU,
            ),
        ),
        (
            KatsuyoText(
                gokan="蹴",
                katsuyo=SHIMO_ICHIDAN,
            ),
            KatsuyoText(
                gokan="蹴",
                katsuyo=RARERU,
            ),
        ),
        (
            KURU,
            KatsuyoText(
                gokan="こ",
                katsuyo=RARERU,
            ),
        ),
        (
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            KatsuyoText(
                gokan="ウォーキングさ",
                katsuyo=RERU,
            ),
        ),
        (
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            KatsuyoText(
                gokan="尊重さ",
                katsuyo=RERU,
            ),
        ),
        (
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            KatsuyoText(
                gokan="重んぜ",
                katsuyo=RARERU,
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
        (
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            KatsuyoText(
                gokan="見",
                katsuyo=SASERU,
            ),
        ),
        (
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            KatsuyoText(
                gokan="求め",
                katsuyo=SASERU,
            ),
        ),
        (
            KURU,
            KatsuyoText(
                gokan="こ",
                katsuyo=SASERU,
            ),
        ),
        (
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            KatsuyoText(
                gokan="ウォーキングさ",
                katsuyo=SERU,
            ),
        ),
        (
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            KatsuyoText(
                gokan="尊重さ",
                katsuyo=SERU,
            ),
        ),
        (
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            KatsuyoText(
                gokan="重んじ",
                katsuyo=SASERU,
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
        # TODO 「らしい」など未然形が存在しないケースを追加
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
        (
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            KatsuyoText(
                gokan="見な",
                katsuyo=KEIYOUSHI,
            ),
        ),
        (
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            KatsuyoText(
                gokan="求めな",
                katsuyo=KEIYOUSHI,
            ),
        ),
        (
            KURU,
            KatsuyoText(
                gokan="こな",
                katsuyo=KEIYOUSHI,
            ),
        ),
        (
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            KatsuyoText(
                gokan="ウォーキングしな",
                katsuyo=KEIYOUSHI,
            ),
        ),
        (
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            KatsuyoText(
                gokan="尊重しな",
                katsuyo=KEIYOUSHI,
            ),
        ),
        (
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            KatsuyoText(
                gokan="重んじな",
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
