import re
import pytest
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    KURU,
    IKatsuyoTextHelper,
    KatsuyoText,
    NonKatsuyoText,
)
from spacy_dialog_reflection.lang.ja.katsuyo import (
    GODAN_BA_GYO,
    GODAN_GA_GYO,
    GODAN_IKU,
    GODAN_KA_GYO,
    GODAN_MA_GYO,
    GODAN_NA_GYO,
    GODAN_RA_GYO,
    GODAN_SA_GYO,
    GODAN_TA_GYO,
    GODAN_WAA_GYO,
    Katsuyo,
    KA_GYO_HENKAKU_KURU,
    KAMI_ICHIDAN,
    KEIYOUDOUSHI,
    KEIYOUSHI,
    SA_GYO_HENKAKU_SURU,
    SA_GYO_HENKAKU_ZURU,
    SHIMO_ICHIDAN,
    ShushiMixin,
)

from spacy_dialog_reflection.lang.ja.katsuyo_text_helper import (
    Hitei,
    KibouOthers,
    Shieki,
    Ukemi,
    KibouSelf,
    KakoKanryo,
)
from spacy_dialog_reflection.lang.ja.katsuyo_text_builder import (
    SpacyKatsuyoTextBuilder,
)


@pytest.fixture(scope="session")
def append_multiple():
    return SpacyKatsuyoTextBuilder().append_multiple


@pytest.fixture(scope="session")
def unsupported_katsuyo_text():
    class UnsupportedKatsuyo(Katsuyo, ShushiMixin):
        pass

    return KatsuyoText(
        gokan="{{gokan}}",
        katsuyo=UnsupportedKatsuyo(
            shushi="{{shushi}}",
        ),
    )


@pytest.mark.parametrize(
    "msg, katsuyo_text, expected",
    [
        (
            "五段活用",
            KatsuyoText(
                gokan="遊",
                katsuyo=GODAN_BA_GYO,
            ),
            "遊ばれる",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見られる",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="蹴",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "蹴られる",
        ),
        (
            "カ変活用",
            KURU,
            "こられる",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングされる",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重される",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んぜられる",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しくなられる",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗になられる",
        ),
        (
            "NonKatsuyoText",
            NonKatsuyoText("状態"),
            "状態になられる",
        ),
    ],
)
def test_zyodoushi_ukemi(msg, katsuyo_text, expected):
    zyodoushi = Ukemi()
    result = katsuyo_text + zyodoushi
    assert str(result) == expected, msg


def test_zyodoushi_ukemi_value_error(unsupported_katsuyo_text):
    zyodoushi = Ukemi()
    with pytest.raises(ValueError):
        unsupported_katsuyo_text + zyodoushi


@pytest.mark.parametrize(
    "msg, katsuyo_text, expected",
    [
        (
            "五段活用",
            KatsuyoText(
                gokan="遊",
                katsuyo=GODAN_BA_GYO,
            ),
            "遊ばせる",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見させる",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めさせる",
        ),
        (
            "カ変活用",
            KURU,
            "こさせる",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングさせる",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重させる",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んじさせる",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しくさせる",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗にさせる",
        ),
        (
            "NonKatsuyoText",
            NonKatsuyoText("状態"),
            "状態にさせる",
        ),
    ],
)
def test_zyodoushi_shieki(msg, katsuyo_text, expected):
    zyodoushi = Shieki()
    result = katsuyo_text + zyodoushi
    assert str(result) == expected, msg


def test_zyodoushi_shieki_value_error(unsupported_katsuyo_text):
    zyodoushi = Shieki()
    with pytest.raises(ValueError):
        unsupported_katsuyo_text + zyodoushi


@pytest.mark.parametrize(
    "msg, katsuyo_text, expected",
    [
        (
            "五段活用",
            KatsuyoText(
                gokan="遊",
                katsuyo=GODAN_BA_GYO,
            ),
            "遊ばない",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見ない",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めない",
        ),
        (
            "カ変活用",
            KURU,
            "こない",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングしない",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重しない",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んじない",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しくない",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗でない",
        ),
        # TODO 助詞のハンドリング
        (
            "NonKatsuyoText",
            NonKatsuyoText("状態"),
            "状態ではない",
        ),
    ],
)
def test_zyodoushi_hiteii(msg, katsuyo_text, expected):
    zyodoushi = Hitei()
    result = katsuyo_text + zyodoushi
    assert str(result) == expected, msg


def test_zyodoushi_hitei_value_error(unsupported_katsuyo_text):
    zyodoushi = Hitei()
    with pytest.raises(ValueError):
        unsupported_katsuyo_text + zyodoushi


@pytest.mark.parametrize(
    "msg, katsuyo_text, expected",
    [
        (
            "五段活用",
            KatsuyoText(
                gokan="遊",
                katsuyo=GODAN_BA_GYO,
            ),
            "遊びたい",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見たい",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めたい",
        ),
        (
            "カ変活用",
            KURU,
            "きたい",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングしたい",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重したい",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んじたい",
        ),
    ],
)
def test_zyodoushi_kibou_self(msg, katsuyo_text, expected):
    zyodoushi = KibouSelf()
    result = katsuyo_text + zyodoushi
    assert str(result) == expected, msg


@pytest.mark.parametrize(
    "msg, katsuyo_text",
    [
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
        ),
        (
            "NonKatsuyoText",
            NonKatsuyoText("状態"),
        ),
    ],
)
def test_zyodoushi_kibou_self_value_error(msg, katsuyo_text):
    zyodoushi = KibouSelf()
    with pytest.raises(ValueError, match=re.compile(r"Unsupported.*")):
        katsuyo_text + zyodoushi
        assert False, msg


@pytest.mark.parametrize(
    "msg, katsuyo_text, expected",
    [
        (
            "五段活用",
            KatsuyoText(
                gokan="遊",
                katsuyo=GODAN_BA_GYO,
            ),
            "遊びたがる",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見たがる",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めたがる",
        ),
        (
            "カ変活用",
            KURU,
            "きたがる",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングしたがる",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重したがる",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んじたがる",
        ),
    ],
)
def test_zyodoushi_kibou_others(msg, katsuyo_text, expected):
    zyodoushi = KibouOthers()
    result = katsuyo_text + zyodoushi
    assert str(result) == expected, msg


@pytest.mark.parametrize(
    "msg, katsuyo_text",
    [
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
        ),
        (
            "NonKatsuyoText",
            NonKatsuyoText("状態"),
        ),
    ],
)
def test_zyodoushi_kibou_others_value_error(msg, katsuyo_text):
    zyodoushi = KibouOthers()
    with pytest.raises(ValueError, match=re.compile(r"Unsupported.*")):
        katsuyo_text + zyodoushi
        assert False, msg


@pytest.mark.parametrize(
    "msg, katsuyo_text, expected",
    [
        # 五段活用を念入りにテスト
        (
            "五段活用",
            KatsuyoText(
                gokan="歩",
                katsuyo=GODAN_KA_GYO,
            ),
            "歩いた",
        ),
        (
            "五段活用",
            KatsuyoText(
                gokan="稼",
                katsuyo=GODAN_GA_GYO,
            ),
            "稼いだ",
        ),
        (
            "五段活用",
            KatsuyoText(
                gokan="話",
                katsuyo=GODAN_SA_GYO,
            ),
            "話した",
        ),
        (
            "五段活用",
            KatsuyoText(
                gokan="待",
                katsuyo=GODAN_TA_GYO,
            ),
            "待った",
        ),
        (
            "五段活用",
            KatsuyoText(
                gokan="死",
                katsuyo=GODAN_NA_GYO,
            ),
            "死んだ",
        ),
        (
            "五段活用",
            KatsuyoText(
                gokan="遊",
                katsuyo=GODAN_BA_GYO,
            ),
            "遊んだ",
        ),
        (
            "五段活用",
            KatsuyoText(
                gokan="読",
                katsuyo=GODAN_MA_GYO,
            ),
            "読んだ",
        ),
        (
            "五段活用",
            KatsuyoText(
                gokan="帰",
                katsuyo=GODAN_RA_GYO,
            ),
            "帰った",
        ),
        (
            "五段活用",
            KatsuyoText(
                gokan="買",
                katsuyo=GODAN_WAA_GYO,
            ),
            "買った",
        ),
        (
            "五段活用",
            KatsuyoText(
                gokan="行",
                katsuyo=GODAN_IKU,
            ),
            "行った",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見た",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めた",
        ),
        (
            "カ変活用",
            KURU,
            "きた",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングした",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重した",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んじた",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しかった",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗だった",
        ),
        (
            "NonKatsuyoText",
            NonKatsuyoText("状態"),
            "状態だった",
        ),
    ],
)
def test_zyodoushi_kako_kanryo(msg, katsuyo_text, expected):
    zyodoushi = KakoKanryo()
    result = katsuyo_text + zyodoushi
    assert str(result) == expected, msg


@pytest.mark.filterwarnings("ignore:ValueError")
@pytest.mark.filterwarnings("ignore:Invalid appendant")
def test_katsuyo_text_warning_value_error(append_multiple):
    class HelperRaiseValueError(IKatsuyoTextHelper):
        def __init__(self):
            super().__init__(bridge=lambda x: x)

        def try_merge(self, _):
            raise ValueError("HOGE")

    katsuyo_text = KURU
    katsuyo_text_appendants = [
        HelperRaiseValueError(),
    ]
    result, has_error = append_multiple(
        katsuyo_text,
        katsuyo_text_appendants,
    )
    assert result == katsuyo_text, "No changes"
    assert has_error, "has_error is True"


@pytest.mark.filterwarnings("ignore:None value TypeError Detected")
@pytest.mark.filterwarnings("ignore:Invalid appendant")
def test_katsuyo_text_warning_none_type_error(append_multiple):
    class HelperrRaiseNoneTypeError(IKatsuyoTextHelper):
        def __init__(self):
            super().__init__(bridge=lambda x: x)

        def try_merge(self, _):
            # raise TypeError
            gokan = "あ" + None
            return KatsuyoText(
                gokan=gokan,
                katsuyo=KA_GYO_HENKAKU_KURU,
            )

    katsuyo_text = KURU
    katsuyo_text_appendants = [
        HelperrRaiseNoneTypeError(),
    ]
    result, has_error = append_multiple(
        katsuyo_text,
        katsuyo_text_appendants,
    )
    assert result == katsuyo_text, "No changes"
    assert has_error, "has_error is True"


@pytest.mark.filterwarnings("ignore:None value TypeError Detected")
@pytest.mark.filterwarnings("ignore:Invalid appendant")
def test_katsuyo_text_warning_none_type_error_on_bridge(append_multiple):
    class HelperrRaiseNoneTypeError(IKatsuyoTextHelper):
        def __init__(self):
            def bridge(_):
                # raise TypeError
                gokan = "あ" + None
                return KatsuyoText(
                    gokan=gokan,
                    katsuyo=KA_GYO_HENKAKU_KURU,
                )

            super().__init__(bridge=bridge)

        def try_merge(self, _):
            return None

    katsuyo_text = KURU
    katsuyo_text_appendants = [
        HelperrRaiseNoneTypeError(),
    ]
    result, has_error = append_multiple(
        katsuyo_text,
        katsuyo_text_appendants,
    )
    assert result == katsuyo_text, "No changes"
    assert has_error, "has_error is True"


@pytest.mark.filterwarnings("ignore:None value TypeError Detected")
@pytest.mark.filterwarnings("ignore:Invalid appendant")
def test_katsuyo_text_warning_none_type_error2(append_multiple):
    class HelperrRaiseNoneTypeError(IKatsuyoTextHelper):
        def __init__(self):
            super().__init__(bridge=lambda x: x)

        def try_merge(self, _):
            gokan = None
            return KatsuyoText(
                # raise TypeError
                gokan=gokan[:-1],
                katsuyo=KA_GYO_HENKAKU_KURU,
            )

    katsuyo_text = KURU
    katsuyo_text_appendants = [
        HelperrRaiseNoneTypeError(),
    ]
    result, has_error = append_multiple(
        katsuyo_text,
        katsuyo_text_appendants,
    )
    assert result == katsuyo_text, "No changes"
    assert has_error, "has_error is True"


def test_katsuyo_text_raise_type_error(append_multiple):
    class HelperRaiseTypeError(IKatsuyoTextHelper):
        def __init__(self):
            super().__init__(bridge=lambda x: x)

        def try_merge(self, _):
            gokan = 1
            return KatsuyoText(
                # raise TypeError
                gokan=gokan[:-1],
                katsuyo=KA_GYO_HENKAKU_KURU,
            )

    katsuyo_text = KURU
    katsuyo_text_appendants = [
        HelperRaiseTypeError(),
    ]
    with pytest.raises(TypeError):
        append_multiple(
            katsuyo_text,
            katsuyo_text_appendants,
        )
