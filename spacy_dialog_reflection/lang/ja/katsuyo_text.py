from typing import Union
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

    def __add__(
        self, post: Union["NoKatsuyoText", "NoKatsuyoText"]
    ) -> Union["NoKatsuyoText", "NoKatsuyoText"]:
        if issubclass(type(post), NoKatsuyoText):
            return self.append(post)

        # if "KatsuyoText"
        # 言語の特性上、活用形の前に接続される品詞の影響を受ける。
        return post.merge(self)

    def append(self, post: "NoKatsuyoText") -> "NoKatsuyoText":
        """
        基本的には連体形で受けるが、下位クラスで上書きすることで
        任意の活用形に変換して返すことがある。
        """
        prefix = self.gokan + self.katsuyo.rentai
        return NoKatsuyoText(text=prefix + post.text)

    def merge(self, pre: "KatsuyoText") -> "KatsuyoText":
        """
        基本的には連用形で受けるが、下位クラスで上書きすることで
        任意の活用形に変換して返すことがある。
        """
        prefix = pre.gokan + pre.katsuyo.renyo
        return KatsuyoText(
            gokan=prefix + self.gokan,
            katsuyo=self.katsuyo,
        )

    def __str__(self):
        return f"{self.gokan}{self.katsuyo}"


@dataclass(frozen=True)
class NoKatsuyoText:
    """
    活用形を含まない文字列を表すクラス
    名詞,助詞,接続詞,感動詞,記号,連体詞,接頭辞,接尾辞,補助記号,フィラー,
    その他,そのままKatsuyoTextにaddする文字列を想定
    """

    text: str

    def __add__(
        self, post: Union["KatsuyoText", "NoKatsuyoText"]
    ) -> Union["KatsuyoText", "NoKatsuyoText"]:
        if issubclass(type(post), NoKatsuyoText):
            return NoKatsuyoText(text=self.text + post.text)

        # if "KatsuyoText"
        return KatsuyoText(
            gokan=self.text + post.gokan,
            katsuyo=post.katsuyo,
        )

    def __str__(self):
        return self.text


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


class ZyodoushiKatsuyoText(KatsuyoText):
    def __init__(self, zyodoushi: KatsuyoText):
        self.zyodoushi = zyodoushi
        super().__init__(
            zyodoushi.gokan,
            zyodoushi.katsuyo,
        )


# ==============================================================================
# 助動詞::受身
# ==============================================================================


class Reru(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            KatsuyoText(
                gokan="れ",
                katsuyo=k.SHIMO_ICHIDAN,
            )
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if issubclass(type(pre.katsuyo), k.SaGyoHenkakuKatsuyo):
            prefix = pre.gokan + pre.katsuyo.mizen_reru
            return NoKatsuyoText(prefix) + self.zyodoushi

        prefix = pre.gokan + pre.katsuyo.mizen
        return NoKatsuyoText(prefix) + self.zyodoushi


class Rareru(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            KatsuyoText(
                gokan="られ",
                katsuyo=k.SHIMO_ICHIDAN,
            )
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if issubclass(type(pre.katsuyo), k.SaGyoHenkakuKatsuyo):
            prefix = pre.gokan + pre.katsuyo.mizen_rareru
            return NoKatsuyoText(prefix) + self.zyodoushi

        prefix = pre.gokan + pre.katsuyo.mizen
        return NoKatsuyoText(prefix) + self.zyodoushi


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
