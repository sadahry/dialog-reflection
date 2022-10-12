from spacy_dialog_reflection.lang.ja.katsuyo import (
    KatsuyoHinshi,
    GODAN_IKU,
    KAMI_ICHIDAN_A_GYO,
    SHIMO_ICHIDAN_A_GYO,
    KA_GYO_HENKAKU_KURU,
    SA_GYO_HENKAKU_SURU,
    GodanKatsuyo,
    KamiIchidanKatsuyo,
    ShimoIchidanKatsuyo,
    SaGyoHenkakuKatsuyo,
    KaGyoHenkakuKatsuyo,
    ZyodoushiKatsuyo,
)
from spacy_dialog_reflection.lang.ja.katsuyo_zyodoushi import (
    RERU,
)
import pytest


@pytest.mark.parametrize(
    "katsuyo, expected_type, expected_hinshi",
    [
        (
            GODAN_IKU,
            GodanKatsuyo,
            KatsuyoHinshi.DOUSHI,
        ),
        (
            KAMI_ICHIDAN_A_GYO,
            KamiIchidanKatsuyo,
            KatsuyoHinshi.DOUSHI,
        ),
        (
            SHIMO_ICHIDAN_A_GYO,
            ShimoIchidanKatsuyo,
            KatsuyoHinshi.DOUSHI,
        ),
        (
            KA_GYO_HENKAKU_KURU,
            KaGyoHenkakuKatsuyo,
            KatsuyoHinshi.DOUSHI,
        ),
        (
            SA_GYO_HENKAKU_SURU,
            SaGyoHenkakuKatsuyo,
            KatsuyoHinshi.DOUSHI,
        ),
        (
            RERU,
            ZyodoushiKatsuyo,
            KatsuyoHinshi.ZYODOUSHI,
        ),
    ],
)
def test_katsuyo_hinshi(katsuyo, expected_type, expected_hinshi):
    assert type(katsuyo) is expected_type
    assert katsuyo.hinshi == expected_hinshi
