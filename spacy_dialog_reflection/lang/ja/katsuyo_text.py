from dataclasses import dataclass
import spacy_dialog_reflection.lang.ja.katsuyo as k


@dataclass(frozen=True)
class KatsuyoText:
    """
    活用形を含む動詞,形容詞,形容動詞,副詞の表現を表すクラス
    """

    gokan: str
    """
    文字列のうち活用されない部分。
    接続される品詞の情報を含むことがある。
    e.g. こられるそうだ -> gokan=こられる
    """
    katsuyo: k.Katsuyo

    def __add__(self, post: "KatsuyoText") -> "KatsuyoText":
        # 言語の特性上、活用形の前に接続される品詞の影響を受ける。
        return post.merge(self)

    def merge(self, pre: "KatsuyoText") -> "KatsuyoText":
        renyo_text = pre.gokan + pre.katsuyo.renyo
        return KatsuyoText(
            gokan=renyo_text + self.gokan,
            katsuyo=self.katsuyo,
        )

    def __str__(self):
        return f"{self.gokan}{self.katsuyo}"


# ==============================================================================
# 動詞
# ==============================================================================

KURU = KatsuyoText(
    gokan="",
    katsuyo=k.KA_GYO_HENKAKU_KURU,
)

KURU_KANJI = KatsuyoText(
    gokan="来",
    katsuyo=k.KA_GYO_HENKAKU_KURU_KANJI,
)

SURU = KatsuyoText(
    gokan="",
    katsuyo=k.SA_GYO_HENKAKU_SURU,
)

ZURU = KatsuyoText(
    gokan="",
    katsuyo=k.SA_GYO_HENKAKU_ZURU,
)

# ==============================================================================
# 助動詞
# see: https://ja.wikipedia.org/wiki/助動詞_(国文法)
# ==============================================================================

# ==============================================================================
# 助動詞::受身
# ==============================================================================

RERU = KatsuyoText(
    gokan="れ",
    katsuyo=k.SHIMO_ICHIDAN,
)

RARERU = KatsuyoText(
    gokan="られ",
    katsuyo=k.SHIMO_ICHIDAN,
)

# ==============================================================================
# 助動詞::使役
# ==============================================================================

SERU = KatsuyoText(
    gokan="せ",
    katsuyo=k.SHIMO_ICHIDAN,
)

SASERU = KatsuyoText(
    gokan="させ",
    katsuyo=k.SHIMO_ICHIDAN,
)

# ==============================================================================
# 助動詞::否定
# ==============================================================================

NAI = KatsuyoText(
    gokan="な",
    katsuyo=k.KEIYOUSHI,
)

# ==============================================================================
# 助動詞::希望
# ==============================================================================

TAI = KatsuyoText(
    gokan="た",
    katsuyo=k.KEIYOUSHI,
)

TAGARU = KatsuyoText(
    gokan="たが",
    katsuyo=k.GODAN_RA_GYO,
)
