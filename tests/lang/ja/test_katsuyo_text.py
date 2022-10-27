import pytest
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    FUKUZYOSHI_BAKARI,
    FUKUZYOSHI_DAKE,
    FUKUZYOSHI_HODO,
    FUKUZYOSHI_KA,
    FUKUZYOSHI_KIRI,
    FUKUZYOSHI_KURAI,
    FUKUZYOSHI_MADE,
    FUKUZYOSHI_NADO,
    FUKUZYOSHI_NARI,
    FUKUZYOSHI_NOMI,
    FUKUZYOSHI_YARA,
    FUKUZYOSHI_ZUTSU,
    JODOUSHI_DA,
    JODOUSHI_TA,
    KURU,
    KURU_KANJI,
    SHUJOSHI_KA,
    SHUJOSHI_KASHIRA,
    SHUJOSHI_NA,
    SHUJOSHI_NO,
    SHUJOSHI_NONI,
    SURU,
    KatsuyoText,
    KatsuyoTextError,
    TaigenText,
)
from spacy_dialog_reflection.lang.ja.katsuyo import (
    GODAN_BA_GYO,
    GODAN_KA_GYO,
    GODAN_SA_GYO,
    KAMI_ICHIDAN,
    KEIYOUDOUSHI,
    KEIYOUSHI,
    SA_GYO_HENKAKU_SURU,
    SA_GYO_HENKAKU_ZURU,
    SHIMO_ICHIDAN,
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


@pytest.mark.parametrize(
    "msg, katsuyo_text, expected",
    [
        (
            "五段活用",
            KatsuyoText(
                gokan="遊",
                katsuyo=GODAN_BA_GYO,
            ),
            "遊ぶばかり",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るばかり",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるばかり",
        ),
        (
            "カ変活用",
            KURU,
            "くるばかり",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするばかり",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するばかり",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるばかり",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいばかり",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗なばかり",
        ),
        (
            "TaigenText",
            TaigenText("状態"),
            "状態ばかり",
        ),
    ],
)
def test_FUKUZYOSHI_BAKARI(msg, katsuyo_text, expected):
    fukujoshi = FUKUZYOSHI_BAKARI
    result = katsuyo_text + fukujoshi
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
            "遊ぶまで",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るまで",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるまで",
        ),
        (
            "カ変活用",
            KURU,
            "くるまで",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするまで",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するまで",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるまで",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいまで",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗なまで",
        ),
        (
            "TaigenText",
            TaigenText("状態"),
            "状態まで",
        ),
    ],
)
def test_FUKUZYOSHI_MADE(msg, katsuyo_text, expected):
    fukujoshi = FUKUZYOSHI_MADE
    result = katsuyo_text + fukujoshi
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
            "遊ぶだけ",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るだけ",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるだけ",
        ),
        (
            "カ変活用",
            KURU,
            "くるだけ",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするだけ",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するだけ",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるだけ",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいだけ",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗なだけ",
        ),
        (
            "TaigenText",
            TaigenText("状態"),
            "状態だけ",
        ),
    ],
)
def test_FUKUZYOSHI_DAKE(msg, katsuyo_text, expected):
    fukujoshi = FUKUZYOSHI_DAKE
    result = katsuyo_text + fukujoshi
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
            "遊ぶほど",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るほど",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるほど",
        ),
        (
            "カ変活用",
            KURU,
            "くるほど",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするほど",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するほど",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるほど",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいほど",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗なほど",
        ),
        (
            "TaigenText",
            TaigenText("状態"),
            "状態ほど",
        ),
    ],
)
def test_FUKUZYOSHI_HODO(msg, katsuyo_text, expected):
    fukujoshi = FUKUZYOSHI_HODO
    result = katsuyo_text + fukujoshi
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
            "遊ぶくらい",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るくらい",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるくらい",
        ),
        (
            "カ変活用",
            KURU,
            "くるくらい",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするくらい",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するくらい",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるくらい",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいくらい",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗なくらい",
        ),
        (
            "TaigenText",
            TaigenText("状態"),
            "状態くらい",
        ),
    ],
)
def test_FUKUZYOSHI_KURAI(msg, katsuyo_text, expected):
    fukujoshi = FUKUZYOSHI_KURAI
    result = katsuyo_text + fukujoshi
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
            "遊ぶなど",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るなど",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるなど",
        ),
        (
            "カ変活用",
            KURU,
            "くるなど",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするなど",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するなど",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるなど",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいなど",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗など",
        ),
        (
            "TaigenText",
            TaigenText("状態"),
            "状態など",
        ),
    ],
)
def test_FUKUZYOSHI_NADO(msg, katsuyo_text, expected):
    fukujoshi = FUKUZYOSHI_NADO
    result = katsuyo_text + fukujoshi
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
            "遊ぶなり",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るなり",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるなり",
        ),
        (
            "カ変活用",
            KURU,
            "くるなり",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするなり",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するなり",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるなり",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいなり",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗なり",
        ),
        (
            "TaigenText",
            TaigenText("状態"),
            "状態なり",
        ),
    ],
)
def test_FUKUZYOSHI_NARI(msg, katsuyo_text, expected):
    fukujoshi = FUKUZYOSHI_NARI
    result = katsuyo_text + fukujoshi
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
            "遊ぶやら",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るやら",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるやら",
        ),
        (
            "カ変活用",
            KURU,
            "くるやら",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするやら",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するやら",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるやら",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいやら",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗やら",
        ),
        (
            "TaigenText",
            TaigenText("状態"),
            "状態やら",
        ),
    ],
)
def test_FUKUZYOSHI_YARA(msg, katsuyo_text, expected):
    fukujoshi = FUKUZYOSHI_YARA
    result = katsuyo_text + fukujoshi
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
            "遊ぶか",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るか",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるか",
        ),
        (
            "カ変活用",
            KURU,
            "くるか",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするか",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するか",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるか",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいか",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗か",
        ),
        (
            "TaigenText",
            TaigenText("状態"),
            "状態か",
        ),
    ],
)
def test_FUKUZYOSHI_KA(msg, katsuyo_text, expected):
    fukujoshi = FUKUZYOSHI_KA
    result = katsuyo_text + fukujoshi
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
            "遊ぶのみ",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るのみ",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるのみ",
        ),
        (
            "カ変活用",
            KURU,
            "くるのみ",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするのみ",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するのみ",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるのみ",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいのみ",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗のみ",
        ),
        (
            "TaigenText",
            TaigenText("状態"),
            "状態のみ",
        ),
    ],
)
def test_FUKUZYOSHI_NOMI(msg, katsuyo_text, expected):
    fukujoshi = FUKUZYOSHI_NOMI
    result = katsuyo_text + fukujoshi
    assert str(result) == expected, msg


@pytest.mark.parametrize(
    "msg, katsuyo_text, expected",
    [
        (
            "五段活用",
            KatsuyoText(
                gokan="付",
                katsuyo=GODAN_KA_GYO,
            ),
            "付きっきり",
        ),
        # 上一段活用では特殊なケースを除き、事例が存在しなかった
        # 特殊なケースであり、文語(BCCWJ)のみに見られたため対応しない
        # (
        #     "上一段活用",
        #     KatsuyoText(
        #         gokan="い",
        #         katsuyo=KAMI_ICHIDAN,
        #     ),
        #     "いるっきり",
        # ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="閉め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "閉めっきり",
        ),
        # カ変活用では事例が存在しなかった
        # (
        #     "カ変活用",
        #     KURU,
        #     "くるか",
        # ),
        # サ変活用では事例が存在しなかった
        # (
        #     "サ変活用",
        #     KatsuyoText(
        #         gokan="ウォーキング",
        #         katsuyo=SA_GYO_HENKAKU_SURU,
        #     ),
        #     "ウォーキングするか",
        # ),
        # (
        #     "サ変活用(する)",
        #     KatsuyoText(
        #         gokan="尊重",
        #         katsuyo=SA_GYO_HENKAKU_SURU,
        #     ),
        #     "尊重するか",
        # ),
        # (
        #     "サ変活用(ずる)",
        #     KatsuyoText(
        #         gokan="重ん",
        #         katsuyo=SA_GYO_HENKAKU_ZURU,
        #     ),
        #     "重んずるか",
        # ),
        (
            "TaigenText",
            TaigenText("ひとり"),
            "ひとりきり",
        ),
        (
            "JodoushiText",
            JODOUSHI_TA,
            "たきり",  # e.g. 寝たきり
        ),
        (
            "JodoushiText",
            JODOUSHI_DA,
            "だきり",  # e.g. 遊んだきり
        ),
    ],
)
def test_FUKUZYOSHI_KIRI(msg, katsuyo_text, expected):
    fukujoshi = FUKUZYOSHI_KIRI
    result = katsuyo_text + fukujoshi
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
    ],
)
def test_FUKUZYOSHI_KIRI_error(msg, katsuyo_text):
    fukujoshi = FUKUZYOSHI_KIRI
    with pytest.raises(KatsuyoTextError):
        katsuyo_text + fukujoshi
        assert False, msg


@pytest.mark.parametrize(
    "msg, katsuyo_text, expected",
    [
        (
            "TaigenText",
            TaigenText("２個"),
            "２個ずつ",
        ),
    ],
)
def test_FUKUZYOSHI_ZUTSU(msg, katsuyo_text, expected):
    fukujoshi = FUKUZYOSHI_ZUTSU
    result = katsuyo_text + fukujoshi
    assert str(result) == expected, msg


@pytest.mark.parametrize(
    "msg, katsuyo_text",
    [
        (
            "五段活用",
            KatsuyoText(
                gokan="遊",
                katsuyo=GODAN_BA_GYO,
            ),
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
        ),
        (
            "カ変活用",
            KURU,
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
        ),
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
    ],
)
def test_FUKUZYOSHI_ZUTSU_error(msg, katsuyo_text):
    fukujoshi = FUKUZYOSHI_ZUTSU
    with pytest.raises(KatsuyoTextError):
        katsuyo_text + fukujoshi
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
            "遊ぶの",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るの",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるの",
        ),
        (
            "カ変活用",
            KURU,
            "くるの",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするの",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するの",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるの",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいの",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗なの",
        ),
        (
            "TaigenText",
            TaigenText("状態"),
            "状態の",
        ),
    ],
)
def test_SHUJOSHI_NO(msg, katsuyo_text, expected):
    shujoshi = SHUJOSHI_NO
    result = katsuyo_text + shujoshi
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
            "遊ぶのに",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るのに",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるのに",
        ),
        (
            "カ変活用",
            KURU,
            "くるのに",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするのに",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するのに",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるのに",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいのに",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗なのに",
        ),
        (
            "TaigenText",
            TaigenText("状態"),
            "状態のに",
        ),
    ],
)
def test_SHUJOSHI_NONI(msg, katsuyo_text, expected):
    shujoshi = SHUJOSHI_NONI
    result = katsuyo_text + shujoshi
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
            "遊ぶな",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るな",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるな",
        ),
        (
            "カ変活用",
            KURU,
            "くるな",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするな",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するな",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるな",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいな",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗だな",
        ),
    ],
)
def test_SHUJOSHI_NA(msg, katsuyo_text, expected):
    shujoshi = SHUJOSHI_NA
    result = katsuyo_text + shujoshi
    assert str(result) == expected, msg


@pytest.mark.parametrize(
    "msg, katsuyo_text",
    [
        (
            "TaigenText",
            TaigenText("状態"),
        ),
    ],
)
def test_SHUJOSHI_NA_error(msg, katsuyo_text):
    shujoshi = SHUJOSHI_NA
    with pytest.raises(KatsuyoTextError):
        katsuyo_text + shujoshi
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
            "遊ぶか",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るか",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるか",
        ),
        (
            "カ変活用",
            KURU,
            "くるか",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするか",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するか",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるか",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいか",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗か",
        ),
        (
            "TaigenText",
            TaigenText("状態"),
            "状態か",
        ),
    ],
)
def test_SHUJOSHI_KA(msg, katsuyo_text, expected):
    shujoshi = SHUJOSHI_KA
    result = katsuyo_text + shujoshi
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
            "遊ぶかしら",
        ),
        (
            "上一段活用",
            KatsuyoText(
                gokan="見",
                katsuyo=KAMI_ICHIDAN,
            ),
            "見るかしら",
        ),
        (
            "下一段活用",
            KatsuyoText(
                gokan="求め",
                katsuyo=SHIMO_ICHIDAN,
            ),
            "求めるかしら",
        ),
        (
            "カ変活用",
            KURU,
            "くるかしら",
        ),
        (
            "サ変活用",
            KatsuyoText(
                gokan="ウォーキング",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "ウォーキングするかしら",
        ),
        (
            "サ変活用(する)",
            KatsuyoText(
                gokan="尊重",
                katsuyo=SA_GYO_HENKAKU_SURU,
            ),
            "尊重するかしら",
        ),
        (
            "サ変活用(ずる)",
            KatsuyoText(
                gokan="重ん",
                katsuyo=SA_GYO_HENKAKU_ZURU,
            ),
            "重んずるかしら",
        ),
        (
            "形容詞",
            KatsuyoText(
                gokan="美し",
                katsuyo=KEIYOUSHI,
            ),
            "美しいかしら",
        ),
        (
            "形容動詞",
            KatsuyoText(
                gokan="綺麗",
                katsuyo=KEIYOUDOUSHI,
            ),
            "綺麗かしら",
        ),
        (
            "TaigenText",
            TaigenText("状態"),
            "状態かしら",
        ),
    ],
)
def test_SHUJOSHI_KASHIRA(msg, katsuyo_text, expected):
    shujoshi = SHUJOSHI_KASHIRA
    result = katsuyo_text + shujoshi
    assert str(result) == expected, msg
