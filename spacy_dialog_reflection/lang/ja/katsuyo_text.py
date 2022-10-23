from collections.abc import Callable
from typing import Union, Optional
import attrs
import abc
import spacy_dialog_reflection.lang.ja.katsuyo as k


class KatsuyoTextError(ValueError):
    pass


@attrs.define(frozen=True, slots=True)
class KatsuyoText:
    """
    活用形を含む動詞,形容詞,形容動詞,副詞の表現を表すクラス。用言を表す。
    """

    gokan: str
    """
    文字列のうち活用されない部分。
    接続される品詞の情報を含むことがある。
    e.g. こられるそうだ -> gokan=こられる
    """
    katsuyo: k.IKatsuyo

    def __add__(
        self, post: Union["KatsuyoText", "NonKatsuyoText", "IKatsuyoTextHelper"]
    ) -> Union["KatsuyoText", "NonKatsuyoText"]:  # IKatsuyoTextHelper は return しない
        # NOTE: postを保持しておいて文字列化する際に再帰呼び出し的にしてもいいかもしれない
        #       ただadd時のエラーがわかりにくくなるので現状は都度gokanに追記するようにしている
        if isinstance(post, NonKatsuyoText):
            return self.append(post)
        elif isinstance(post, KatsuyoText):
            # 言語の特性上、活用形の前に接続される品詞の影響を受ける。
            return post.merge(self)
        elif isinstance(post, IKatsuyoTextHelper):
            # 言語の特性上、活用形の前に接続される品詞の影響を受ける。
            return post.merge(self)

        raise KatsuyoTextError(f"Invalid type in addition: {type(post)}")

    def append(self, post: "NonKatsuyoText") -> "NonKatsuyoText":
        """
        基本的には連体形で受けるが、下位クラスで上書きすることで
        任意の活用形に変換して返すことがある。
        """
        if isinstance(self.katsuyo, k.RentaiMixin):
            return NonKatsuyoText(self.gokan + self.katsuyo.rentai + post.text)

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in append of {type(self)}: {post} "
            f"type: {type(post)}"
        )

    def merge(self, pre: "KatsuyoText") -> "KatsuyoText":
        """
        基本的には連用形で受けるが、下位クラスで上書きすることで
        任意の活用形に変換して返すことがある。
        """
        if isinstance(pre.katsuyo, k.RenyoMixin):
            return KatsuyoText(
                gokan=pre.gokan + pre.katsuyo.renyo + self.gokan,
                katsuyo=self.katsuyo,
            )

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in merge of {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )

    def __str__(self):
        return f"{self.gokan}{self.katsuyo}"


@attrs.define(frozen=True, slots=True)
class NonKatsuyoText:
    """
    活用形を含まない文字列を表すクラス。
    名詞,助詞,接続詞,感動詞,記号,連体詞,接頭辞,接尾辞,補助記号,フィラー,
    その他,そのままKatsuyoTextにaddする文字列を想定。
    基本的には体言だが、活用された用言を含むこともある。
    """

    text: str

    def __add__(
        self, post: Union["KatsuyoText", "NonKatsuyoText", "IKatsuyoTextHelper"]
    ) -> Union["KatsuyoText", "NonKatsuyoText"]:  # IKatsuyoTextHelper は return しない
        if isinstance(post, NonKatsuyoText):
            return NonKatsuyoText(text=self.text + post.text)
        elif isinstance(post, KatsuyoText):
            return KatsuyoText(
                gokan=self.text + post.gokan,
                katsuyo=post.katsuyo,
            )
        elif isinstance(post, IKatsuyoTextHelper):
            # 言語の特性上、活用形の前に接続される品詞の影響を受ける。
            # 値を調整できるようにbridgeとする
            if post.bridge is not None:
                return post.bridge(self)
            raise KatsuyoTextError(
                f"Unsupported IKatsuyoTextHelper which has no bridge in addition: {type(post)}"
            )

        raise KatsuyoTextError(f"Invalid type in addition: {type(post)}")

    def __str__(self):
        return self.text


class IKatsuyoTextHelper(abc.ABC):
    """
    柔軟に活用系を変換するためのクラス
    """

    BridgeFunction = Callable[[Union[KatsuyoText, NonKatsuyoText]], KatsuyoText]

    def __init__(
        self,
        bridge: Optional[BridgeFunction] = None,
    ) -> None:
        # 文法的には不正な活用形の組み合わせを
        # 任意の活用形に変換して返せるようにするための関数
        self.bridge = bridge

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        result = self.try_merge(pre)
        if result is None:
            if self.bridge is not None:
                return self.bridge(pre)
            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )
        return result

    @abc.abstractmethod
    def try_merge(self, pre: KatsuyoText) -> Optional[KatsuyoText]:
        raise NotImplementedError()


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
    @property
    def zyodoushi(self):
        return KatsuyoText(
            gokan=self.gokan,
            katsuyo=self.katsuyo,
        )


# ==============================================================================
# 助動詞::受身
# ==============================================================================


class Reru(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="れ",
            katsuyo=k.SHIMO_ICHIDAN,
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            if type(pre.katsuyo) is k.SaGyoHenkakuKatsuyo:
                mizen_reru = pre.katsuyo.mizen_reru
                return NonKatsuyoText(pre.gokan + mizen_reru) + self.zyodoushi
            return NonKatsuyoText(pre.gokan + pre.katsuyo.mizen) + self.zyodoushi

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


class Rareru(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="られ",
            katsuyo=k.SHIMO_ICHIDAN,
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            if type(pre.katsuyo) is k.SaGyoHenkakuKatsuyo:
                mizen_rareru = pre.katsuyo.mizen_rareru
                return NonKatsuyoText(pre.gokan + mizen_rareru) + self.zyodoushi
            return NonKatsuyoText(pre.gokan + pre.katsuyo.mizen) + self.zyodoushi

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


# ==============================================================================
# 助動詞::使役
# ==============================================================================


class Seru(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="せ",
            katsuyo=k.SHIMO_ICHIDAN,
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            if type(pre.katsuyo) is k.SaGyoHenkakuKatsuyo:
                mizen_reru = pre.katsuyo.mizen_reru
                return NonKatsuyoText(pre.gokan + mizen_reru) + self.zyodoushi
            return NonKatsuyoText(pre.gokan + pre.katsuyo.mizen) + self.zyodoushi

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


class Saseru(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="させ",
            katsuyo=k.SHIMO_ICHIDAN,
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            # サ変活用「〜ずる」には未然形「〜じ させる」を採用したため他と同一の未然形に
            return NonKatsuyoText(pre.gokan + pre.katsuyo.mizen) + self.zyodoushi

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


# ==============================================================================
# 助動詞::否定
# ==============================================================================


class Nai(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="な",
            katsuyo=k.KEIYOUSHI,
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            return NonKatsuyoText(pre.gokan + pre.katsuyo.mizen) + self.zyodoushi

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


# ==============================================================================
# 助動詞::希望
# ==============================================================================


class Tai(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="た",
            katsuyo=k.KEIYOUSHI,
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            return NonKatsuyoText(pre.gokan + pre.katsuyo.renyo) + self.zyodoushi

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


class Tagaru(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="たが",
            katsuyo=k.GODAN_RA_GYO,
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            return NonKatsuyoText(pre.gokan + pre.katsuyo.renyo) + self.zyodoushi

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


# ==============================================================================
# 助動詞::過去・完了
# ==============================================================================


class Ta(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="",
            katsuyo=k.ZYODOUSHI_TA,
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if isinstance(pre.katsuyo, k.RenyoMixin):
            if isinstance(pre.katsuyo, k.RenyoTaMixin):
                return NonKatsuyoText(pre.gokan + pre.katsuyo.renyo_ta) + self.zyodoushi
            return NonKatsuyoText(pre.gokan + pre.katsuyo.renyo) + self.zyodoushi

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


class Da(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="",
            katsuyo=k.ZYODOUSHI_DA,
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if isinstance(pre.katsuyo, k.RenyoMixin):
            if isinstance(pre.katsuyo, k.RenyoTaMixin):
                return NonKatsuyoText(pre.gokan + pre.katsuyo.renyo_ta) + self.zyodoushi
            return NonKatsuyoText(pre.gokan + pre.katsuyo.renyo) + self.zyodoushi

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


# ==============================================================================
# 助動詞::様態
# ==============================================================================


class SoudaYoutai(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="そう",
            katsuyo=k.KEIYOUDOUSHI,
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if isinstance(pre.katsuyo, (k.KeiyoushiKatsuyo, k.KeiyoudoushiKatsuyo)):
            return NonKatsuyoText(pre.gokan) + self.zyodoushi
        elif isinstance(pre.katsuyo, k.RenyoMixin):
            return NonKatsuyoText(pre.gokan + pre.katsuyo.renyo) + self.zyodoushi

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


# ==============================================================================
# 助動詞::伝聞
# ==============================================================================


class SoudaDenbun(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="そう",
            # NOTE: 本来「伝聞」の活用系は形容動詞とは異なる(e.g., 未然形が存在しない)
            #       現状の意味を厳密に扱わない状態においては、形容動詞の活用系を使う
            katsuyo=k.KEIYOUDOUSHI,
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if isinstance(pre.katsuyo, k.ShushiMixin):
            return NonKatsuyoText(pre.gokan + pre.katsuyo.shushi) + self.zyodoushi

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


# ==============================================================================
# 助動詞::推定
# ==============================================================================


class Rashii(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="らし",
            # NOTE: 本来の活用系は形容詞とは異なる(e.g., 未然形が存在しない)
            #       現状の意味を厳密に扱わない状態においては、形容詞の活用系を使う
            katsuyo=k.KEIYOUSHI,
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if isinstance(pre.katsuyo, k.KeiyoudoushiKatsuyo):
            return NonKatsuyoText(pre.gokan) + self.zyodoushi
        elif isinstance(pre.katsuyo, k.ShushiMixin):
            return NonKatsuyoText(pre.gokan + pre.katsuyo.shushi) + self.zyodoushi

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


# ==============================================================================
# 助動詞::当然
# ==============================================================================


class Bekida(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="べき",
            # NOTE: 本来の活用系は形容動詞とは異なる(e.g., 命令形が存在しない)
            #       現状の意味を厳密に扱わない状態においては、形容動詞の活用系を使う
            katsuyo=k.KEIYOUDOUSHI,
        )

    def merge(self, pre: KatsuyoText) -> KatsuyoText:
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            return NonKatsuyoText(pre.gokan + pre.katsuyo.shushi) + self.zyodoushi

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )
