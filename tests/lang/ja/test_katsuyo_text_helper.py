import re
import pytest
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    KURU,
    IKatsuyoTextHelper,
    KatsuyoText,
    NonKatsuyoText,
    KatsuyoTextError,
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
    IKatsuyo,
    KA_GYO_HENKAKU_KURU,
    KAMI_ICHIDAN,
    KEIYOUDOUSHI,
    KEIYOUSHI,
    SA_GYO_HENKAKU_SURU,
    SA_GYO_HENKAKU_ZURU,
    SHIMO_ICHIDAN,
)

from spacy_dialog_reflection.lang.ja.katsuyo_text_helper import (
    Denbun,
    Hitei,
    KibouOthers,
    Shieki,
    Suitei,
    Touzen,
    Ukemi,
    KibouSelf,
    KakoKanryo,
    Youtai,
)
from spacy_dialog_reflection.lang.ja.katsuyo_text_builder import (
    SpacyKatsuyoTextBuilder,
)


@pytest.fixture(scope="session")
def append_multiple():
    return SpacyKatsuyoTextBuilder().append_multiple


@pytest.fixture(scope="session")
def unsupported_katsuyo_text():
    class UnsupportedKatsuyo(IKatsuyo):
        pass

    return KatsuyoText(
        gokan="{{gokan}}",
        katsuyo=UnsupportedKatsuyo(),
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
    with pytest.raises(KatsuyoTextError):
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
    with pytest.raises(KatsuyoTextError):
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
    with pytest.raises(KatsuyoTextError):
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
    with pytest.raises(KatsuyoTextError, match=re.compile(r"Unsupported.*")):
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
    with pytest.raises(KatsuyoTextError, match=re.compile(r"Unsupported.*")):
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


@pytest.mark.parametrize(
    "msg, katsuyo_text, expected",
    [
        (
            "五段活用",
            KatsuyoText(
                gokan="遊",
                katsuyo=GODAN_BA_GYO,
            ),
            "遊びそうだ",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見そうだ",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めそうだ",
        ),
        (
            "カ変活用",
            KURU,
            "きそうだ",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングしそうだ",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重しそうだ",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んじそうだ",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しそうだ",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗そうだ",
        ),
        # TODO 助詞のハンドリング
        (
            "NonKatsuyoText",
            NonKatsuyoText("状態"),
            "状態そうだ",
        ),
    ],
)
def test_zyodoushi_youtaii(msg, katsuyo_text, expected):
    zyodoushi = Youtai()
    result = katsuyo_text + zyodoushi
    assert str(result) == expected, msg


def test_zyodoushi_youtai_value_error(unsupported_katsuyo_text):
    zyodoushi = Youtai()
    with pytest.raises(KatsuyoTextError):
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
            "遊ぶそうだ",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るそうだ",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるそうだ",
        ),
        (
            "カ変活用",
            KURU,
            "くるそうだ",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするそうだ",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するそうだ",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるそうだ",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいそうだ",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗だそうだ",
        ),
        # TODO 助詞のハンドリング
        (
            "NonKatsuyoText",
            NonKatsuyoText("状態"),
            "状態だそうだ",
        ),
    ],
)
def test_zyodoushi_denbun(msg, katsuyo_text, expected):
    zyodoushi = Denbun()
    result = katsuyo_text + zyodoushi
    assert str(result) == expected, msg


def test_zyodoushi_denbun_value_error(unsupported_katsuyo_text):
    zyodoushi = Denbun()
    with pytest.raises(KatsuyoTextError):
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
            "遊ぶらしい",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るらしい",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるらしい",
        ),
        (
            "カ変活用",
            KURU,
            "くるらしい",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするらしい",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するらしい",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるらしい",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいらしい",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗らしい",
        ),
        # TODO 助詞のハンドリング
        (
            "NonKatsuyoText",
            NonKatsuyoText("状態"),
            "状態らしい",
        ),
    ],
)
def test_zyodoushi_suitei(msg, katsuyo_text, expected):
    zyodoushi = Suitei()
    result = katsuyo_text + zyodoushi
    assert str(result) == expected, msg


def test_zyodoushi_suitei_value_error(unsupported_katsuyo_text):
    zyodoushi = Suitei()
    with pytest.raises(KatsuyoTextError):
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
            "遊ぶべきだ",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るべきだ",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるべきだ",
        ),
        (
            "カ変活用",
            KURU,
            "くるべきだ",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするべきだ",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するべきだ",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるべきだ",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しくあるべきだ",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗であるべきだ",
        ),
        # TODO 助詞のハンドリング
        (
            "NonKatsuyoText",
            NonKatsuyoText("状態"),
            "状態であるべきだ",
        ),
    ],
)
def test_zyodoushi_touzen(msg, katsuyo_text, expected):
    zyodoushi = Touzen()
    result = katsuyo_text + zyodoushi
    assert str(result) == expected, msg


def test_zyodoushi_touzen_value_error(unsupported_katsuyo_text):
    zyodoushi = Touzen()
    with pytest.raises(KatsuyoTextError):
        unsupported_katsuyo_text + zyodoushi


@pytest.mark.filterwarnings(r"ignore:Error in append_multiple.*KatsuyoTextError")
@pytest.mark.filterwarnings("ignore:Skip invalid appendant")
def test_katsuyo_text_warning_KatsuyoTextError(append_multiple):
    class HelperRaiseKatsuyoTextError(IKatsuyoTextHelper):
        def __init__(self):
            super().__init__(bridge=lambda x: x)

        def try_merge(self, _):
            raise KatsuyoTextError("HOGE")

    katsuyo_text = KURU
    katsuyo_text_appendants = [
        HelperRaiseKatsuyoTextError(),
    ]
    result, has_error = append_multiple(
        katsuyo_text,
        katsuyo_text_appendants,
    )
    assert result == katsuyo_text, "No changes"
    assert has_error, "has_error is True"


@pytest.mark.filterwarnings(r"ignore:Error in append_multiple.*AttributeError")
@pytest.mark.filterwarnings("ignore:Skip invalid appendant")
def test_katsuyo_text_warning_AttributeError(append_multiple):
    class HelperRaiseNoneAttributeError(IKatsuyoTextHelper):
        def __init__(self):
            super().__init__(bridge=lambda x: x)

        def try_merge(self, _):
            return KatsuyoText(
                gokan="",
                # raise AttributeError
                katsuyo=KA_GYO_HENKAKU_KURU.hoge,
            )

    katsuyo_text = KURU
    katsuyo_text_appendants = [
        HelperRaiseNoneAttributeError(),
    ]
    result, has_error = append_multiple(
        katsuyo_text,
        katsuyo_text_appendants,
    )
    assert result == katsuyo_text, "No changes"
    assert has_error, "has_error is True"


@pytest.mark.filterwarnings(r"ignore:Error in append_multiple.*KatsuyoTextError")
@pytest.mark.filterwarnings("ignore:Skip invalid appendant")
def test_katsuyo_text_warning_KatsuyoTextError_on_bridge(append_multiple):
    class HelperRaiseKatsuyoTextError(IKatsuyoTextHelper):
        def __init__(self):
            def bridge(_):
                raise KatsuyoTextError("HOGE")

            super().__init__(bridge=bridge)

        def try_merge(self, _):
            return None

    katsuyo_text = KURU
    katsuyo_text_appendants = [
        HelperRaiseKatsuyoTextError(),
    ]
    result, has_error = append_multiple(
        katsuyo_text,
        katsuyo_text_appendants,
    )
    assert result == katsuyo_text, "No changes"
    assert has_error, "has_error is True"


@pytest.mark.filterwarnings(r"ignore:Error in append_multiple.*AttributeError")
@pytest.mark.filterwarnings("ignore:Skip invalid appendant")
def test_katsuyo_text_warning_AttributeErrorr_on_bridge(append_multiple):
    class HelperRaiseNoneAttributeError(IKatsuyoTextHelper):
        def __init__(self):
            def bridge(_):
                return KatsuyoText(
                    gokan="",
                    # raise AttributeError
                    katsuyo=KA_GYO_HENKAKU_KURU.hoge,
                )

            super().__init__(bridge=bridge)

        def try_merge(self, _):
            return None

    katsuyo_text = KURU
    katsuyo_text_appendants = [
        HelperRaiseNoneAttributeError(),
    ]
    result, has_error = append_multiple(
        katsuyo_text,
        katsuyo_text_appendants,
    )
    assert result == katsuyo_text, "No changes"
    assert has_error, "has_error is True"
