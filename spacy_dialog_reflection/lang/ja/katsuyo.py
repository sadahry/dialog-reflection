from dataclasses import dataclass
from enum import Enum, auto, unique
from typing import Optional
import abc

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


@unique
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
    meirei: Optional[str]

    @property
    @abc.abstractmethod
    def hinshi(self) -> KatsuyoHinshi:
        raise NotImplementedError()

    def __str__(self) -> str:
        return self.shushi


# ==============================================================================
# 動詞
# ==============================================================================


class DoushiKatsuyo(Katsuyo):
    @property
    def hinshi(self) -> KatsuyoHinshi:
        return KatsuyoHinshi.DOUSHI


# ==============================================================================
# 動詞::五段活用
# see: https://ja.wikipedia.org/wiki/五段活用
# ==============================================================================


@dataclass(frozen=True)
class GodanKatsuyo(DoushiKatsuyo):
    # 未然形（ア段）が意思・推量の語尾（あるいは助動詞）の「う」に接続する際にオ段となる。
    mizen_u: str
    # 五段活用の連用形に「た・て」などが続くとき、活用語尾が変化する。
    renyo_ta: str


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
# 動詞::上一段活用
# see: https://ja.wikipedia.org/wiki/上一段活用
# ==============================================================================


@dataclass(frozen=True)
class KamiIchidanKatsuyo(DoushiKatsuyo):
    # 命令形「-○よ」は登録しない
    # 「-○ろ」のほうが口語的だと判断
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


@dataclass(frozen=True)
class ShimoIchidanKatsuyo(DoushiKatsuyo):
    # 命令形「-○よ」は登録しない
    # 「-○ろ」のほうが口語的だと判断
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


@dataclass(frozen=True)
class KaGyoHenkakuKatsuyo(DoushiKatsuyo):
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

# ==============================================================================
# 動詞::サ行変格活用
# see: https://ja.wikipedia.org/wiki/サ行変格活用
# ==============================================================================


@dataclass(frozen=True)
class SaGyoHenkakuKatsuyo(DoushiKatsuyo):
    # せる/れる
    mizen_reru: str
    # ぬ/られる
    mizen_rareru: str
    # 命令形「せよ」は登録しない
    # 「しろ」のほうが口語的だと判断


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


@dataclass(frozen=True)
class KeiyoushiKatsuyo(Katsuyo):
    # 連用形に「た」が続くとき、活用語尾が変化する。
    renyo_ta: str

    @property
    def hinshi(self) -> KatsuyoHinshi:
        return KatsuyoHinshi.KEIYOUSHI


KEIYOUSHI = KeiyoushiKatsuyo(
    mizen="かろ",
    renyo="く",
    renyo_ta="かっ",
    shushi="い",
    rentai="い",
    katei="けれ",
    meirei=None,
)

# ==============================================================================
# 形容動詞
# see: https://www.kokugobunpou.com/用言/形容動詞-2-活用/#gsc.tab=0
# ==============================================================================


@dataclass(frozen=True)
class KeiyoudoushiKatsuyo(Katsuyo):
    # 連用形に「た」が続くとき、活用語尾が変化する。
    renyo_ta: str
    # 連用形に「なる」「する」などが続くとき、活用語尾が変化する。
    renyo_naru: str

    @property
    def hinshi(self) -> KatsuyoHinshi:
        return KatsuyoHinshi.KEIYOUDOUSHI


KEIYOUDOUSHI = KeiyoudoushiKatsuyo(
    mizen="だろ",
    renyo="で",
    renyo_ta="だっ",
    renyo_naru="に",
    shushi="だ",
    rentai="な",
    katei="なら",
    meirei=None,
)

# ==============================================================================
# 助動詞
# see: https://ja.wikipedia.org/wiki/助動詞_(国文法)
# ==============================================================================


@dataclass(frozen=True)
class ZyodoushiKatsuyo(Katsuyo):
    @property
    def hinshi(self) -> KatsuyoHinshi:
        return KatsuyoHinshi.ZYODOUSHI


# ==============================================================================
# 助動詞::受身
# ==============================================================================

RERU = ZyodoushiKatsuyo(
    mizen="れ",
    renyo="れ",
    shushi="れる",
    rentai="れる",
    katei="れれ",
    # 命令形「れよ」は省略
    meirei="れろ",
)

RARERU = ZyodoushiKatsuyo(
    mizen="られ",
    renyo="られ",
    shushi="られる",
    rentai="られる",
    katei="られれ",
    # 命令形「られよ」は省略
    meirei="られろ",
)

# ==============================================================================
# 助動詞::使役
# ==============================================================================

SERU = ZyodoushiKatsuyo(
    mizen="せ",
    renyo="せ",
    shushi="せる",
    rentai="せる",
    katei="せれ",
    # 命令形「せよ」は省略
    meirei="せろ",
)

SASERU = ZyodoushiKatsuyo(
    mizen="させ",
    renyo="させ",
    shushi="させる",
    rentai="させる",
    katei="させれ",
    # 命令形「させよ」は省略
    meirei="させろ",
)
