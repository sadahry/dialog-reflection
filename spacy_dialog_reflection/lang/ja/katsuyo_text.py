from typing import Union, cast, get_args
import attrs
import abc
import spacy_dialog_reflection.lang.ja.katsuyo as k


class KatsuyoTextError(ValueError):
    pass


class IKatsuyoTextAddition(abc.ABC):
    """
    IKatsuyoTextSource + IKatsuyoTextAppendant = IKatsuyoTextSource の演算が
    できるようにするためのインターフェース
    """

    def __add__(self, post: "IKatsuyoTextAppendant") -> "IKatsuyoTextSource":
        # NOTE: postを保持しておいて文字列化する際に再帰呼び出し的にしてもいいかもしれない
        #       ただadd時のエラーがわかりにくくなるので現状は都度gokanに追記するようにしている

        # NOTE: IKatsuyoTextSourceしか許可しない
        assert isinstance(
            self, get_args(IKatsuyoTextSource)
        ), "self must be IKatsuyoTextSource"
        self = cast(IKatsuyoTextSource, self)

        # 言語の特性上、活用形の前に接続される品詞の影響を受ける。
        return post.merge(self)

    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError()


class IKatsuyoTextAppendant(abc.ABC):
    """
    IKatsuyoTextSourceに追加する要素を表す。
    あくまでIKatsuyoTextSourceへaddするためのインターフェースであり、
    このインターフェースを実装したクラスへaddすることはできない。
    """

    @abc.abstractmethod
    def merge(self, pre: "IKatsuyoTextSource") -> "IKatsuyoTextSource":
        raise NotImplementedError()


@attrs.define(frozen=True, slots=True)
class KatsuyoText(IKatsuyoTextAddition, IKatsuyoTextAppendant):
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

    def merge(self, pre: "IKatsuyoTextSource") -> "KatsuyoText":
        """
        基本的には連用形で受けるが、下位クラスで上書きすることで
        任意の活用形に変換して返すことがある。
        """
        if isinstance(pre, INonKatsuyoText):
            # TODO 許可したクラス以外はエラーするように変更
            return KatsuyoText(
                gokan=pre.text + self.gokan,
                katsuyo=self.katsuyo,
            )

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
class INonKatsuyoText(IKatsuyoTextAddition, IKatsuyoTextAppendant):
    """
    活用形を含まない文字列を表すクラス。
    名詞,助詞,接続詞,感動詞,記号,連体詞,接頭辞,接尾辞,補助記号,フィラー,
    その他,そのままKatsuyoTextにaddする文字列を想定。
    基本的には体言。活用された用言を含むこともあるため、下位クラスで定義する。
    """

    text: str

    def merge(self, pre: "IKatsuyoTextSource") -> "INonKatsuyoText":
        """
        基本的には連体形で受けるが、下位クラスで上書きすることで
        任意の活用形に変換して返すことがある。
        """
        if isinstance(pre, INonKatsuyoText):
            return INonKatsuyoText(text=pre.text + self.text)

        if isinstance(pre.katsuyo, k.RentaiMixin):
            return INonKatsuyoText(
                text=pre.gokan + pre.katsuyo.rentai + self.text,
            )

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in merge of {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )

    def __str__(self):
        return self.text


# 文字列で定義するとget_argsの参照先が変わってしまうため下部に定義
# IKatsuyoTextSource = Union["KatsuyoText", "INonKatsuyoText"] # NG
IKatsuyoTextSource = Union[KatsuyoText, INonKatsuyoText]


# ==============================================================================
# KatsuyoText
# TODO 別ファイルに分割する
# ==============================================================================

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
# 補助動詞/補助形容詞
# see:https://www.kokugobunpou.com/用言/補助動詞-補助形容詞
# ==============================================================================


class HozyoKatsuyoText(KatsuyoText):
    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            if isinstance(pre.katsuyo, k.GodanKatsuyo) and (
                pre.katsuyo.shushi in ["ぐ", "ぬ", "ぶ", "む"]
            ):
                return cast(KatsuyoText, pre + Da() + self)
            return cast(KatsuyoText, pre + Ta() + self)
        elif type(pre.katsuyo) is k.KeiyoushiKatsuyo:
            renyo = pre.gokan + pre.katsuyo.renyo
            return cast(
                KatsuyoText,
                INonKatsuyoText(renyo) + self,
            )
        elif type(pre.katsuyo) is k.KeiyoudoushiKatsuyo:
            renyo_nai = pre.gokan + pre.katsuyo.renyo_nai
            return cast(
                KatsuyoText,
                INonKatsuyoText(renyo_nai) + self,
            )

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


HOZYO_NAI = HozyoKatsuyoText(
    gokan="な",
    katsuyo=k.KEIYOUSHI,
)

HOZYO_ARU = HozyoKatsuyoText(
    gokan="あ",
    katsuyo=k.GODAN_RA_GYO,
)

HOZYO_IRU = HozyoKatsuyoText(
    gokan="い",
    katsuyo=k.KAMI_ICHIDAN,
)

# ==============================================================================
# 助動詞
# see: https://ja.wikipedia.org/wiki/助動詞_(国文法)
# ==============================================================================


class ZyodoushiKatsuyoText(KatsuyoText):
    @property
    def katsuyo_text(self) -> KatsuyoText:
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

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            if type(pre.katsuyo) is k.SaGyoHenkakuKatsuyo:
                mizen_reru = pre.katsuyo.mizen_reru
                return cast(
                    KatsuyoText,
                    INonKatsuyoText(pre.gokan + mizen_reru) + self.katsuyo_text,
                )
            return cast(
                KatsuyoText,
                INonKatsuyoText(pre.gokan + pre.katsuyo.mizen) + self.katsuyo_text,
            )

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

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            if type(pre.katsuyo) is k.SaGyoHenkakuKatsuyo:
                mizen_rareru = pre.katsuyo.mizen_rareru
                return cast(
                    KatsuyoText,
                    INonKatsuyoText(pre.gokan + mizen_rareru) + self.katsuyo_text,
                )
            return cast(
                KatsuyoText,
                INonKatsuyoText(pre.gokan + pre.katsuyo.mizen) + self.katsuyo_text,
            )

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

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            if type(pre.katsuyo) is k.SaGyoHenkakuKatsuyo:
                mizen_reru = pre.katsuyo.mizen_reru
                return cast(
                    KatsuyoText,
                    INonKatsuyoText(pre.gokan + mizen_reru) + self.katsuyo_text,
                )
            return cast(
                KatsuyoText,
                INonKatsuyoText(pre.gokan + pre.katsuyo.mizen) + self.katsuyo_text,
            )

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

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            # サ変活用「〜ずる」には未然形「〜じ させる」を採用したため他と同一の未然形に
            return cast(
                KatsuyoText,
                INonKatsuyoText(pre.gokan + pre.katsuyo.mizen) + self.katsuyo_text,
            )

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

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            return cast(
                KatsuyoText,
                INonKatsuyoText(pre.gokan + pre.katsuyo.mizen) + self.katsuyo_text,
            )

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

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            return cast(
                KatsuyoText,
                INonKatsuyoText(pre.gokan + pre.katsuyo.renyo) + self.katsuyo_text,
            )

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

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            return cast(
                KatsuyoText,
                INonKatsuyoText(pre.gokan + pre.katsuyo.renyo) + self.katsuyo_text,
            )

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

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.RenyoMixin):
            if isinstance(pre.katsuyo, k.RenyoTaMixin):
                renyo_ta = pre.gokan + pre.katsuyo.renyo_ta
                return cast(
                    KatsuyoText,
                    INonKatsuyoText(renyo_ta) + self.katsuyo_text,
                )
            renyo = pre.gokan + pre.katsuyo.renyo
            return cast(
                KatsuyoText,
                INonKatsuyoText(renyo) + self.katsuyo_text,
            )

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

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.RenyoMixin):
            if isinstance(pre.katsuyo, k.RenyoTaMixin):
                renyo_ta = pre.gokan + pre.katsuyo.renyo_ta
                return cast(
                    KatsuyoText,
                    INonKatsuyoText(renyo_ta) + self.katsuyo_text,
                )
            renyo = pre.gokan + pre.katsuyo.renyo
            return cast(
                KatsuyoText,
                INonKatsuyoText(renyo) + self.katsuyo_text,
            )

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

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, (k.KeiyoushiKatsuyo, k.KeiyoudoushiKatsuyo)):
            return cast(
                KatsuyoText,
                INonKatsuyoText(pre.gokan) + self.katsuyo_text,
            )
        elif isinstance(pre.katsuyo, k.RenyoMixin):
            return cast(
                KatsuyoText,
                INonKatsuyoText(pre.gokan + pre.katsuyo.renyo) + self.katsuyo_text,
            )

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

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.ShushiMixin):
            return cast(
                KatsuyoText,
                INonKatsuyoText(pre.gokan + pre.katsuyo.shushi) + self.katsuyo_text,
            )

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

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO 体言と一部の助詞に対応
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.KeiyoudoushiKatsuyo):
            return cast(
                KatsuyoText,
                INonKatsuyoText(pre.gokan) + self.katsuyo_text,
            )
        elif isinstance(pre.katsuyo, k.ShushiMixin):
            return cast(
                KatsuyoText,
                INonKatsuyoText(pre.gokan + pre.katsuyo.shushi) + self.katsuyo_text,
            )

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
            katsuyo=k.KEIYOUDOUSHI,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            return cast(
                KatsuyoText,
                INonKatsuyoText(pre.gokan + pre.katsuyo.shushi) + self.katsuyo_text,
            )

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


# ==============================================================================
# 助動詞::比況 例示 推定
# ==============================================================================


class Youda(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="よう",
            katsuyo=k.KEIYOUDOUSHI,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.RentaiMixin):
            return cast(
                KatsuyoText,
                INonKatsuyoText(pre.gokan + pre.katsuyo.rentai) + self.katsuyo_text,
            )

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


# ==============================================================================
# 助動詞::継続
# 助動詞の参照リンクには含まれないが、口語では頻出されるため追記
# ref. https://ja.wiktionary.org/wiki/てる#助動詞
# ==============================================================================


class Teiru(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="てい",
            katsuyo=k.KAMI_ICHIDAN,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.RenyoMixin):
            if isinstance(pre.katsuyo, k.RenyoTaMixin):
                renyo_ta = pre.gokan + pre.katsuyo.renyo_ta
                return cast(
                    KatsuyoText,
                    INonKatsuyoText(renyo_ta) + self.katsuyo_text,
                )
            renyo = pre.gokan + pre.katsuyo.renyo
            return cast(
                KatsuyoText,
                INonKatsuyoText(renyo) + self.katsuyo_text,
            )

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )


class Deiru(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="でい",
            katsuyo=k.KAMI_ICHIDAN,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, INonKatsuyoText):
            # TODO エラー出す
            return super().merge(pre)
        if isinstance(pre.katsuyo, k.RenyoMixin):
            if isinstance(pre.katsuyo, k.RenyoTaMixin):
                renyo_ta = pre.gokan + pre.katsuyo.renyo_ta
                return cast(
                    KatsuyoText,
                    INonKatsuyoText(renyo_ta) + self.katsuyo_text,
                )
            renyo = pre.gokan + pre.katsuyo.renyo
            return cast(
                KatsuyoText,
                INonKatsuyoText(renyo) + self.katsuyo_text,
            )

        raise KatsuyoTextError(
            f"Unsupported katsuyo_text in {type(self)}: {pre} "
            f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
        )
