import pytest
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    KatsuyoText,
)
from spacy_dialog_reflection.lang.ja.katsuyo import (
    GODAN_BA_GYO,
    KA_GYO_HENKAKU_KURU,
)
from spacy_dialog_reflection.lang.ja.katsuyo_zyodoushi import (
    RARERU,
    RERU,
    IZyodoushiBuilder,
    Ukemi,
    build_zyodoushi,
)


def test_katsuyo_text_generate(nlp_ja):
    doc = nlp_ja("明日が来る")
    kuru_token = doc[-1]
    kuru = KatsuyoText.from_token(kuru_token)
    assert kuru.gokan == ""
    assert kuru.katsuyo.shushi == "くる"


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
def test_zohdoushi_builder_ukemi(katsuyo_text, expected):
    zohdoushi_builder = Ukemi()
    result = zohdoushi_builder.build(katsuyo_text)
    assert str(result) == str(expected)


@pytest.mark.filterwarnings("ignore:ValueError")
@pytest.mark.filterwarnings("ignore:Invalid zodoushi_builder")
def test_katsuyo_text_warning_value_error():
    class BuilderRaiseValueError(IZyodoushiBuilder):
        def build(self, _):
            raise ValueError("HOGE")

    katsuyo_text = KatsuyoText(
        gokan="",
        katsuyo=KA_GYO_HENKAKU_KURU,
    )
    zyodoushi_builders = [
        BuilderRaiseValueError(),
    ]
    result, has_error = build_zyodoushi(
        katsuyo_text,
        zyodoushi_builders,
    )
    assert result == katsuyo_text, "No changes"
    assert has_error, "has_error is True"


@pytest.mark.filterwarnings("ignore:None value TypeError Detected")
@pytest.mark.filterwarnings("ignore:Invalid zodoushi_builder")
def test_katsuyo_text_warning_none_type_error():
    class BuilderRaiseTypeError(IZyodoushiBuilder):
        def build(self, _):
            return KatsuyoText(
                # raise TypeError
                gokan="あ" + None,
                katsuyo=KA_GYO_HENKAKU_KURU,
            )

    katsuyo_text = KatsuyoText(
        gokan="",
        katsuyo=KA_GYO_HENKAKU_KURU,
    )
    zyodoushi_builders = [
        BuilderRaiseTypeError(),
    ]
    result, has_error = build_zyodoushi(
        katsuyo_text,
        zyodoushi_builders,
    )
    assert result == katsuyo_text, "No changes"
    assert has_error, "has_error is True"
