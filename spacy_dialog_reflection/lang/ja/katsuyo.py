from dataclasses import dataclass
from enum import Enum, auto
import abc


class KatsuyoHinshi(Enum):
    # ref. https://docs.python.org/ja/3/library/enum.html#using-automatic-values
    def _generate_next_value_(name, start, count, last_values):
        return name

    DOUSHI = auto()
    ZYODOUSHI = auto()
    KEIYOUSHI = auto()
    KEIYOUDOUSHI = auto()


@dataclass(frozen=True)
class Katsuyo:
    mizen: str
    renyo: str
    shushi: str
    rentai: str
    # 已然形もkateiに含める
    katei: str
    meirei: str

    @property
    @abc.abstractmethod
    def hinshi(self) -> KatsuyoHinshi:
        raise NotImplementedError()

    def __str__(self) -> str:
        return self.shushi


class DoushiKatsuyo(Katsuyo):
    @property
    def hinshi(self) -> KatsuyoHinshi:
        return KatsuyoHinshi.DOUSHI


class ZyodoushiKatsuyo(Katsuyo):
    @property
    def hinshi(self) -> KatsuyoHinshi:
        return KatsuyoHinshi.ZYODOUSHI


@dataclass(frozen=True)
class GodanKatsuyo(DoushiKatsuyo):
    # 未然形（ア段）が意思・推量の語尾（あるいは助動詞）の「う」に接続する際にオ段となる。
    mizen_u: str
    # 五段活用の連用形に「た・て」などが続くとき、活用語尾が変化する。
    renyo_ta: str


@dataclass(frozen=True)
class KamiIchidanKatsuyo(DoushiKatsuyo):
    # 命令形「-○よ」は登録しない
    # 「-○ろ」のほうが口語的だと判断
    pass


@dataclass(frozen=True)
class ShimoIchidanKatsuyo(DoushiKatsuyo):
    # 命令形「-○よ」は登録しない
    # 「-○ろ」のほうが口語的だと判断
    pass


@dataclass(frozen=True)
class KaGyoHenkakuKatsuyo(DoushiKatsuyo):
    pass


@dataclass(frozen=True)
class SaGyoHenkakuKatsuyo(DoushiKatsuyo):
    # せる/れる
    mizen_reru: str
    # ぬ/られる
    mizen_rareru: str
    # 命令形「せよ」は登録しない
    # 「しろ」のほうが口語的だと判断
    pass


# ==============================================================================
# 五段活用
# see: https://ja.wikipedia.org/wiki/五段活用
# ==============================================================================

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
    renyo_ta="う",
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
# 上一段活用
# see: https://ja.wikipedia.org/wiki/上一段活用
# ==============================================================================

# ア行
KAMI_ICHIDAN_A_GYO = KamiIchidanKatsuyo(
    mizen="い",
    renyo="い",
    shushi="いる",
    rentai="いる",
    katei="いれ",
    meirei="いろ",
)

# カ行
KAMI_ICHIDAN_KA_GYO = KamiIchidanKatsuyo(
    mizen="き",
    renyo="き",
    shushi="きる",
    rentai="きる",
    katei="きれ",
    meirei="きろ",
)

# ザ行
KAMI_ICHIDAN_ZA_GYO = KamiIchidanKatsuyo(
    mizen="じ",
    renyo="じ",
    shushi="じる",
    rentai="じる",
    katei="じれ",
    meirei="じろ",
)

# タ行
KAMI_ICHIDAN_TA_GYO = KamiIchidanKatsuyo(
    mizen="ち",
    renyo="ち",
    shushi="ちる",
    rentai="ちる",
    katei="ちれ",
    meirei="ちろ",
)

# バ行
KAMI_ICHIDAN_BA_GYO = KamiIchidanKatsuyo(
    mizen="び",
    renyo="び",
    shushi="びる",
    rentai="びる",
    katei="びれ",
    meirei="びろ",
)

# マ行
KAMI_ICHIDAN_MA_GYO = KamiIchidanKatsuyo(
    mizen="み",
    renyo="み",
    shushi="みる",
    rentai="みる",
    katei="みれ",
    meirei="みろ",
)

# ラ行
KAMI_ICHIDAN_RA_GYO = KamiIchidanKatsuyo(
    mizen="り",
    renyo="り",
    shushi="りる",
    rentai="りる",
    katei="りれ",
    meirei="りろ",
)

# 語幹なし
# e.g. 居（い）る, 着（き）る, 煮（に）る, 見（み）る
KAMI_ICHIDAN_NO_GOKAN = KamiIchidanKatsuyo(
    mizen="",
    renyo="",
    shushi="る",
    rentai="る",
    katei="れ",
    meirei="ろ",
)

# ==============================================================================
# 下一段活用
# see: https://ja.wikipedia.org/wiki/下一段活用
# ==============================================================================

# ア行
SHIMO_ICHIDAN_A_GYO = ShimoIchidanKatsuyo(
    mizen="え",
    renyo="え",
    shushi="える",
    rentai="える",
    katei="えれ",
    meirei="えろ",
)

# カ行
SHIMO_ICHIDAN_KA_GYO = ShimoIchidanKatsuyo(
    mizen="け",
    renyo="け",
    shushi="ける",
    rentai="ける",
    katei="けれ",
    meirei="けろ",
)

# サ行
SHIMO_ICHIDAN_SA_GYO = ShimoIchidanKatsuyo(
    mizen="せ",
    renyo="せ",
    shushi="せる",
    rentai="せる",
    katei="せれ",
    meirei="せろ",
)

# ザ行
SHIMO_ICHIDAN_ZA_GYO = ShimoIchidanKatsuyo(
    mizen="ぜ",
    renyo="ぜ",
    shushi="ぜる",
    rentai="ぜる",
    katei="ぜれ",
    meirei="ぜろ",
)

# タ行
SHIMO_ICHIDAN_TA_GYO = ShimoIchidanKatsuyo(
    mizen="て",
    renyo="て",
    shushi="てる",
    rentai="てる",
    katei="てれ",
    meirei="てろ",
)

# ダ行
SHIMO_ICHIDAN_DA_GYO = ShimoIchidanKatsuyo(
    mizen="で",
    renyo="で",
    shushi="でる",
    rentai="でる",
    katei="でれ",
    meirei="でろ",
)

# ナ行
SHIMO_ICHIDAN_NA_GYO = ShimoIchidanKatsuyo(
    mizen="ね",
    renyo="ね",
    shushi="ねる",
    rentai="ねる",
    katei="ねれ",
    meirei="ねろ",
)

# ハ行
SHIMO_ICHIDAN_HA_GYO = ShimoIchidanKatsuyo(
    mizen="へ",
    renyo="へ",
    shushi="へる",
    rentai="へる",
    katei="へれ",
    meirei="へろ",
)

# バ行
SHIMO_ICHIDAN_BA_GYO = ShimoIchidanKatsuyo(
    mizen="べ",
    renyo="べ",
    shushi="べる",
    rentai="べる",
    katei="べれ",
    meirei="べろ",
)

# マ行
SHIMO_ICHIDAN_MA_GYO = ShimoIchidanKatsuyo(
    mizen="め",
    renyo="め",
    shushi="める",
    rentai="める",
    katei="めれ",
    meirei="めろ",
)

# ラ行
SHIMO_ICHIDAN_RA_GYO = ShimoIchidanKatsuyo(
    mizen="れ",
    renyo="れ",
    shushi="れる",
    rentai="れる",
    katei="れれ",
    meirei="れろ",
)

# ==============================================================================
# カ行変格活用
# see: https://ja.wikipedia.org/wiki/カ行変格活用
# ==============================================================================

# 「くる」のみ特殊な活用形を持つ。
KA_GYO_HENKAKU_KURU = KaGyoHenkakuKatsuyo(
    mizen="こ",
    renyo="き",
    shushi="くる",
    rentai="くる",
    katei="くれ",
    meirei="こい",
)

# ==============================================================================
# サ行変格活用
# see: https://ja.wikipedia.org/wiki/サ行変格活用
# ==============================================================================

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
