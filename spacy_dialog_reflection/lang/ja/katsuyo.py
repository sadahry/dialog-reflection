import attrs

DAN = {
    "あ": ["あ", "か", "さ", "た", "な", "は", "ま", "や", "ら", "わ", "が", "ざ", "だ", "ば", "ぱ"],
    "い": ["い", "き", "し", "ち", "に", "ひ", "み", "り", "ぎ", "じ", "ぢ", "び", "ぴ"],
    "う": ["う", "く", "す", "つ", "ぬ", "ふ", "む", "ゆ", "る", "ぐ", "ず", "づ", "ぶ", "ぷ"],
    "え": ["え", "け", "せ", "て", "ね", "へ", "め", "れ", "げ", "ぜ", "で", "べ", "ぺ"],
    "お": ["お", "こ", "そ", "と", "の", "ほ", "も", "よ", "ろ", "を", "ご", "ぞ", "ど", "ぼ", "ぽ"],
}

GYO = {
    "あ": ["あ", "い", "う", "え", "お"],
    "か": ["か", "き", "く", "け", "こ"],
    "さ": ["さ", "し", "す", "せ", "そ"],
    "た": ["た", "ち", "つ", "て", "と"],
    "な": ["な", "に", "ぬ", "ね", "の"],
    "は": ["は", "ひ", "ふ", "へ", "ほ"],
    "ま": ["ま", "み", "む", "め", "も"],
    "や": ["や", "ゆ", "よ"],
    "ら": ["ら", "り", "る", "れ", "ろ"],
    "わ": ["わ", "を"],
    "が": ["が", "ぎ", "ぐ", "げ", "ご"],
    "ざ": ["ざ", "じ", "ず", "ぜ", "ぞ"],
    "だ": ["だ", "ぢ", "づ", "で", "ど"],
    "ば": ["ば", "び", "ぶ", "べ", "ぼ"],
    "ぱ": ["ぱ", "ぴ", "ぷ", "ぺ", "ぽ"],
}


# ==============================================================================
# 活用系ベース
# ==============================================================================


class IKatsuyo:
    pass


@attrs.define(frozen=True, slots=False)
class MizenMixin:
    """未然形"""

    mizen: str


@attrs.define(frozen=True, slots=False)
class RenyoMixin:
    """連用形"""

    renyo: str


@attrs.define(frozen=True, slots=False)
class ShushiMixin:
    """終止形"""

    shushi: str

    def __str__(self) -> str:
        return self.shushi


@attrs.define(frozen=True, slots=False)
class RentaiMixin:
    """連体形"""

    rentai: str


@attrs.define(frozen=True, slots=False)
class KateiMixin:
    """
    仮定形
    已然形(izen)は仮定形に含める
    """

    katei: str


@attrs.define(frozen=True, slots=False)
class MeireiMixin:
    """命令形"""

    meirei: str


# 特殊な活用系


@attrs.define(frozen=True, slots=False)
class MizenUMixin:
    """
    未然形が意思・推量の語尾（あるいは助動詞）の
    「う」に続くとき、活用語尾が変化する活用形が存在する。
    """

    mizen_u: str


@attrs.define(frozen=True, slots=False)
class MizenReruMixin:
    """
    未然形が受身の「れる」使役の「せる」に続くとき、
    活用語尾が変化する活用形が存在する。
    """

    mizen_reru: str


@attrs.define(frozen=True, slots=False)
class MizenRareeruMixin:
    """
    未然形が受身の「られる」や否定の「ぬ」に続くとき、
    活用語尾が変化する活用形が存在する。
    """

    mizen_rareru: str


@attrs.define(frozen=True, slots=False)
class RenyoTaMixin:
    """
    連用形に「た・て」などが続くとき、
    活用語尾が変化する活用形が存在する。
    """

    renyo_ta: str


@attrs.define(frozen=True, slots=False)
class RenyoNaiMixin:
    """
    連用形に「ない」などが続くとき、
    活用語尾が変化する活用形が存在する。
    """

    renyo_nai: str


# ==============================================================================
# 動詞ベース
# ==============================================================================


@attrs.define(frozen=True, slots=False)
class IDoushiKatsuyo(
    IKatsuyo,
    MizenMixin,
    RenyoMixin,
    ShushiMixin,
    RentaiMixin,
    KateiMixin,
    MeireiMixin,
):
    pass


# ==============================================================================
# 動詞::五段活用
# see: https://ja.wikipedia.org/wiki/五段活用
# ==============================================================================


@attrs.define(frozen=True, slots=True)
class GodanKatsuyo(
    IDoushiKatsuyo,
    # 「う」の場合、オ段となる
    MizenUMixin,
    RenyoTaMixin,
):
    pass


# カ行
GODAN_KA_GYO = GodanKatsuyo(
    mizen="か",
    mizen_u="こ",
    renyo="き",
    renyo_ta="い",
    shushi="く",
    rentai="く",
    katei="け",
    meirei="け",
)

# ガ行
GODAN_GA_GYO = GodanKatsuyo(
    mizen="が",
    mizen_u="ご",
    renyo="ぎ",
    renyo_ta="い",
    shushi="ぐ",
    rentai="ぐ",
    katei="げ",
    meirei="げ",
)

# サ行
GODAN_SA_GYO = GodanKatsuyo(
    mizen="さ",
    mizen_u="そ",
    renyo="し",
    renyo_ta="し",
    shushi="す",
    rentai="す",
    katei="せ",
    meirei="せ",
)

# タ行
GODAN_TA_GYO = GodanKatsuyo(
    mizen="た",
    mizen_u="と",
    renyo="ち",
    renyo_ta="っ",
    shushi="つ",
    rentai="つ",
    katei="て",
    meirei="て",
)

# ナ行
GODAN_NA_GYO = GodanKatsuyo(
    mizen="な",
    mizen_u="の",
    renyo="に",
    renyo_ta="ん",
    shushi="ぬ",
    rentai="ぬ",
    katei="ね",
    meirei="ね",
)

# バ行
GODAN_BA_GYO = GodanKatsuyo(
    mizen="ば",
    mizen_u="ぼ",
    renyo="び",
    renyo_ta="ん",
    shushi="ぶ",
    rentai="ぶ",
    katei="べ",
    meirei="べ",
)

# マ行
GODAN_MA_GYO = GodanKatsuyo(
    mizen="ま",
    mizen_u="も",
    renyo="み",
    renyo_ta="ん",
    shushi="む",
    rentai="む",
    katei="め",
    meirei="め",
)

# ラ行
GODAN_RA_GYO = GodanKatsuyo(
    mizen="ら",
    mizen_u="ろ",
    renyo="り",
    renyo_ta="っ",
    shushi="る",
    rentai="る",
    katei="れ",
    meirei="れ",
)

# ワア行
GODAN_WAA_GYO = GodanKatsuyo(
    mizen="わ",
    mizen_u="お",
    renyo="い",
    renyo_ta="っ",
    shushi="う",
    rentai="う",
    katei="え",
    meirei="え",
)

# 「行く」は特殊な活用形を持つ。
GODAN_IKU = GodanKatsuyo(
    mizen="か",
    mizen_u="こ",
    renyo="き",
    renyo_ta="っ",
    shushi="く",
    rentai="く",
    katei="け",
    meirei="け",
)

# ==============================================================================
# 動詞::上一段活用
# see: https://ja.wikipedia.org/wiki/上一段活用
# ==============================================================================


@attrs.define(frozen=True, slots=True)
class KamiIchidanKatsuyo(
    # 命令形「-○よ」は登録しない
    # 「-○ろ」のほうが口語的だと判断
    IDoushiKatsuyo,
):
    pass


KAMI_ICHIDAN = KamiIchidanKatsuyo(
    mizen="",
    renyo="",
    shushi="る",
    rentai="る",
    katei="れ",
    meirei="ろ",
)

# ==============================================================================
# 動詞::下一段活用
# see: https://ja.wikipedia.org/wiki/下一段活用
# ==============================================================================


@attrs.define(frozen=True, slots=True)
class ShimoIchidanKatsuyo(
    # 命令形「-○よ」は登録しない
    # 「-○ろ」のほうが口語的だと判断
    IDoushiKatsuyo,
):
    pass


SHIMO_ICHIDAN = ShimoIchidanKatsuyo(
    mizen="",
    renyo="",
    shushi="る",
    rentai="る",
    katei="れ",
    meirei="ろ",
)

# ==============================================================================
# 動詞::カ行変格活用
# see: https://ja.wikipedia.org/wiki/カ行変格活用
# ==============================================================================


@attrs.define(frozen=True, slots=True)
class KaGyoHenkakuKatsuyo(
    IDoushiKatsuyo,
):
    pass


# 「くる」のみ特殊な活用形を持つ。
KA_GYO_HENKAKU_KURU = KaGyoHenkakuKatsuyo(
    mizen="こ",
    renyo="き",
    shushi="くる",
    rentai="くる",
    katei="くれ",
    meirei="こい",
)

# 「来る」と「くる」を区別
# TODO ReadingをKatsuyoに含める際には語幹から「来」を除く
KA_GYO_HENKAKU_KURU_KANJI = KaGyoHenkakuKatsuyo(
    mizen="",
    renyo="",
    shushi="る",
    rentai="る",
    katei="れ",
    meirei="い",
)

# ==============================================================================
# 動詞::サ行変格活用
# see: https://ja.wikipedia.org/wiki/サ行変格活用
# ==============================================================================


@attrs.define(frozen=True, slots=True)
class SaGyoHenkakuKatsuyo(
    # 命令形「せよ」は登録しない
    # 「しろ」のほうが口語的だと判断
    IDoushiKatsuyo,
    MizenReruMixin,
    MizenRareeruMixin,
):
    pass


# 「〜する」の特殊な活用形
# e.g. 愛（あい）する
SA_GYO_HENKAKU_SURU = SaGyoHenkakuKatsuyo(
    mizen="し",
    mizen_reru="さ",
    mizen_rareru="せ",
    renyo="し",
    shushi="する",
    rentai="する",
    katei="すれ",
    meirei="しろ",
)

# 「〜ずる」の特殊な活用形
# e.g. 生（しょう）ずる
SA_GYO_HENKAKU_ZURU = SaGyoHenkakuKatsuyo(
    mizen="じ",
    mizen_reru="ざ",
    mizen_rareru="ぜ",
    renyo="じ",
    shushi="ずる",
    rentai="ずる",
    katei="ずれ",
    meirei="じろ",
)


# ==============================================================================
# 形容詞
# see: https://www.kokugobunpou.com/用言/形容詞-2-活用/#gsc.tab=0
# ==============================================================================


@attrs.define(frozen=True, slots=True)
class KeiyoushiKatsuyo(
    IKatsuyo,
    MizenMixin,
    RenyoMixin,
    RenyoTaMixin,
    ShushiMixin,
    RentaiMixin,
    KateiMixin,
    # NO: MeireiMixin,
):
    pass


KEIYOUSHI = KeiyoushiKatsuyo(
    mizen="かろ",
    renyo="く",
    renyo_ta="かっ",
    shushi="い",
    rentai="い",
    katei="けれ",
)

# ==============================================================================
# 形容動詞
# see: https://www.kokugobunpou.com/用言/形容動詞-2-活用/#gsc.tab=0
# ==============================================================================


@attrs.define(frozen=True, slots=True)
class KeiyoudoushiKatsuyo(
    IKatsuyo,
    MizenMixin,
    RenyoMixin,
    RenyoTaMixin,
    RenyoNaiMixin,
    ShushiMixin,
    RentaiMixin,
    KateiMixin,
    # NO: MeireiMixin,
):
    pass


KEIYOUDOUSHI = KeiyoudoushiKatsuyo(
    mizen="だろ",
    renyo="に",
    renyo_ta="だっ",
    renyo_nai="で",
    shushi="だ",
    rentai="な",
    katei="なら",
)

# ==============================================================================
# 助動詞ベース
# see: https://ja.wikipedia.org/wiki/助動詞_(国文法)
# ==============================================================================


@attrs.define(frozen=True, slots=False)
class IZyodoushiKatsuyo(IKatsuyo):
    """
    このクラスは助動詞の活用形を表すクラスではなく、
    特殊な活用であることを表すクラスである。
    """

    pass


# ==============================================================================
# 助動詞「た」「だ」
# ==============================================================================


@attrs.define(frozen=True, slots=True)
class TaKatsuyo(
    IZyodoushiKatsuyo,
    MizenMixin,
    # NO: RenyoMixin,
    ShushiMixin,
    RentaiMixin,
    KateiMixin,
    # NO: MeireiMixin,
):
    pass


ZYODOUSHI_TA = TaKatsuyo(
    mizen="たろ",
    shushi="た",
    rentai="た",
    katei="たら",
)

ZYODOUSHI_DA = TaKatsuyo(
    mizen="だ",
    shushi="だ",
    rentai="だ",
    katei="だら",
)
