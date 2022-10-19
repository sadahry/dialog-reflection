import pytest
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    KURU,
    KatsuyoText,
    NonKatsuyoText,
)
from spacy_dialog_reflection.lang.ja.katsuyo import (
    GODAN_BA_GYO,
    # KA_GYO_HENKAKU_KURU,
    KAMI_ICHIDAN,
    KEIYOUDOUSHI,
    KEIYOUSHI,
    SA_GYO_HENKAKU_SURU,
    SA_GYO_HENKAKU_ZURU,
    SHIMO_ICHIDAN,
)

# TODO 直す
# from spacy_dialog_reflection.lang.ja.katsuyo_text_helper import (
#     Nai,
#     Shieki,
#     Ukemi,
# )
from spacy_dialog_reflection.lang.ja.katsuyo_text_helper import (
    Ukemi,
)
from spacy_dialog_reflection.lang.ja.katsuyo_text_builder import (
    SpacyKatsuyoTextBuilder,
)


@pytest.fixture(scope="session")
def append_multiple():
    return SpacyKatsuyoTextBuilder().append_multiple


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


# @pytest.mark.parametrize(
#     "msg, katsuyo_text, expected",
#     [
#         (
#             "五段活用",
#             KatsuyoText(
#                 gokan="遊",
#                 katsuyo=GODAN_BA_GYO,
#             ),
#             "遊ばせる",
#         ),
#         (
#             "上一段活用",
#             KatsuyoText(
#                 gokan="見",
#                 katsuyo=KAMI_ICHIDAN,
#             ),
#             "見させる",
#         ),
#         (
#             "下一段活用",
#             KatsuyoText(
#                 gokan="求め",
#                 katsuyo=SHIMO_ICHIDAN,
#             ),
#             "求めさせる",
#         ),
#         (
#             "カ変活用",
#             KURU,
#             "こさせる",
#         ),
#         (
#             "サ変活用",
#             KatsuyoText(
#                 gokan="ウォーキング",
#                 katsuyo=SA_GYO_HENKAKU_SURU,
#             ),
#             "ウォーキングさせる",
#         ),
#         (
#             "サ変活用(する)",
#             KatsuyoText(
#                 gokan="尊重",
#                 katsuyo=SA_GYO_HENKAKU_SURU,
#             ),
#             "尊重させる",
#         ),
#         (
#             "サ変活用(ずる)",
#             KatsuyoText(
#                 gokan="重ん",
#                 katsuyo=SA_GYO_HENKAKU_ZURU,
#             ),
#             "重んじさせる",
#         ),
#     ],
# )
# def test_zyodoushi_shieki(msg, katsuyo_text, expected):
#     zyodoushi = Shieki()
#     result = katsuyo_text + zyodoushi
#     assert str(result) == expected, msg


# @pytest.mark.filterwarnings("ignore:ValueError")
# @pytest.mark.filterwarnings("ignore:Invalid appendant")
# def test_katsuyo_text_warning_value_error(append_multiple):
#     class AppenderRaiseValueError(IKatsuyoTextAppendants):
#         def append(self, _):
#             raise ValueError("HOGE")

#     katsuyo_text = KatsuyoText(
#         gokan="",
#         katsuyo=KA_GYO_HENKAKU_KURU,
#     )
#     katsuyo_text_appendants = [
#         AppenderRaiseValueError(),
#     ]
#     result, has_error = append_multiple(
#         katsuyo_text,
#         katsuyo_text_appendants,
#     )
#     assert result == katsuyo_text, "No changes"
#     assert has_error, "has_error is True"


# @pytest.mark.parametrize(
#     "msg, katsuyo_text, expected",
#     [
#         # TODO 「らしい」など未然形が存在しないケースを追加
#         (
#             "五段活用",
#             KatsuyoText(
#                 gokan="遊",
#                 katsuyo=GODAN_BA_GYO,
#             ),
#             "遊ばない",
#         ),
#         (
#             "上一段活用",
#             KatsuyoText(
#                 gokan="見",
#                 katsuyo=KAMI_ICHIDAN,
#             ),
#             "見ない",
#         ),
#         (
#             "下一段活用",
#             KatsuyoText(
#                 gokan="求め",
#                 katsuyo=SHIMO_ICHIDAN,
#             ),
#             "求めない",
#         ),
#         (
#             "カ変活用",
#             KURU,
#             "こない",
#         ),
#         (
#             "サ変活用",
#             KatsuyoText(
#                 gokan="ウォーキング",
#                 katsuyo=SA_GYO_HENKAKU_SURU,
#             ),
#             "ウォーキングしない",
#         ),
#         (
#             "サ変活用(する)",
#             KatsuyoText(
#                 gokan="尊重",
#                 katsuyo=SA_GYO_HENKAKU_SURU,
#             ),
#             "尊重しない",
#         ),
#         (
#             "サ変活用(ずる)",
#             KatsuyoText(
#                 gokan="重ん",
#                 katsuyo=SA_GYO_HENKAKU_ZURU,
#             ),
#             "重んじない",
#         ),
#     ],
# )
# def test_zyodoushi_Nai(msg, katsuyo_text, expected):
#     zyodoushi = Nai()
#     result = katsuyo_text + zyodoushi
#     assert str(result) == expected, msg


# @pytest.mark.filterwarnings("ignore:None value TypeError Detected")
# @pytest.mark.filterwarnings("ignore:Invalid appendant")
# def test_katsuyo_text_warning_none_type_error(append_multiple):
#     class AppenderRaiseTypeError(IKatsuyoTextAppendants):
#         def append(self, _):
#             # raise TypeError
#             gokan = "あ" + None
#             return KatsuyoText(
#                 gokan=gokan,
#                 katsuyo=KA_GYO_HENKAKU_KURU,
#             )

#     katsuyo_text = KatsuyoText(
#         gokan="",
#         katsuyo=KA_GYO_HENKAKU_KURU,
#     )
#     katsuyo_text_appendants = [
#         AppenderRaiseTypeError(),
#     ]
#     result, has_error = append_multiple(
#         katsuyo_text,
#         katsuyo_text_appendants,
#     )
#     assert result == katsuyo_text, "No changes"
#     assert has_error, "has_error is True"


# @pytest.mark.filterwarnings("ignore:None value TypeError Detected")
# @pytest.mark.filterwarnings("ignore:Invalid appendant")
# def test_katsuyo_text_warning_none_type_error2(append_multiple):
#     class AppenderRaiseTypeError(IKatsuyoTextAppendants):
#         def append(self, _):
#             gokan = None
#             return KatsuyoText(
#                 # raise TypeError
#                 gokan=gokan[:-1],
#                 katsuyo=KA_GYO_HENKAKU_KURU,
#             )

#     katsuyo_text = KatsuyoText(
#         gokan="",
#         katsuyo=KA_GYO_HENKAKU_KURU,
#     )
#     katsuyo_text_appendants = [
#         AppenderRaiseTypeError(),
#     ]
#     result, has_error = append_multiple(
#         katsuyo_text,
#         katsuyo_text_appendants,
#     )
#     assert result == katsuyo_text, "No changes"
#     assert has_error, "has_error is True"
