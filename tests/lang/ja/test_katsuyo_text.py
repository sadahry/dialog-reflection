import pytest
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    KatsuyoText,
)
from spacy_dialog_reflection.lang.ja.katsuyo import (
    KA_GYO_HENKAKU_KURU,
)
from spacy_dialog_reflection.lang.ja.katsuyo_zyodoushi import (
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


def test_zohdoushi_builder():
    katsuyo_text = KatsuyoText(
        gokan="",
        katsuyo=KA_GYO_HENKAKU_KURU,
    )
    zohdoushi_builder = Ukemi()
    katsuyo_w_zyodoushi = zohdoushi_builder.build(katsuyo_text)
    assert katsuyo_w_zyodoushi.gokan == "こ"
    assert katsuyo_w_zyodoushi.katsuyo.shushi == "られる"


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
    result = build_zyodoushi(
        katsuyo_text,
        zyodoushi_builders,
    )
    assert result == katsuyo_text, "No changes"
