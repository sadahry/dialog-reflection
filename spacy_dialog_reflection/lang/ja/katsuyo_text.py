from typing import Optional, Union, TypeVar, Generic
import attrs
import abc
import spacy_dialog_reflection.lang.ja.katsuyo as k

A = TypeVar("A", "KatsuyoText", "FixedKatsuyoText", "INonKatsuyoText")
M = TypeVar("M", "KatsuyoText", "FixedKatsuyoText", "INonKatsuyoText")


class KatsuyoTextError(ValueError):
    pass


@attrs.define(frozen=True, slots=False)
class IKatsuyoTextSource(abc.ABC):
    """活用系テキスト"""

    gokan: str
    katsuyo: Union[
        k.IKatsuyo,  # KatsuyoText
        k.FixedKatsuyo,  # FixedKatsuyoText
        None,  # INonKatsuyoText
    ]

    @abc.abstractmethod
    def __add__(self, post: "IKatsuyoTextAppendant[A]") -> A:
        # NOTE: postを保持しておいて文字列化する際に再帰呼び出し的にしてもいいかもしれない
        #       ただadd時のエラーがわかりにくくなるので現状は都度gokanに追記するようにしている
        raise NotImplementedError()


class IKatsuyoTextAppendant(abc.ABC, Generic[M]):
    """
    IKatsuyoTextSourceに追加する要素を表す。
    あくまでIKatsuyoTextSourceへaddするためのインターフェースであり、
    このインターフェースを実装したクラスへaddすることはできない。
    """

    @abc.abstractmethod
    def merge(self, pre: IKatsuyoTextSource) -> M:
        raise NotImplementedError()


@attrs.define(frozen=True, slots=True)
class KatsuyoText(IKatsuyoTextSource, IKatsuyoTextAppendant["KatsuyoText"]):
    """
    活用形を含む動詞,形容詞,形容動詞,副詞の表現を表すクラス。用言を表す。
    """

    gokan: str
    katsuyo: k.IKatsuyo

    def merge(self, pre: IKatsuyoTextSource) -> "KatsuyoText":
        """
        基本的には連用形で受けるが、下位クラスで上書きすることで
        任意の活用形に変換して返すことがある。
        """
        if isinstance(pre, FixedKatsuyoText):
            return pre + self
        elif isinstance(pre, INonKatsuyoText):
            # 簡単のため、INonKatsuyoTextはすべて許容とする
            # 助詞「だ」など不適切なものもあるが現状管理しない
            return pre + self
        else:
            assert isinstance(pre, KatsuyoText)
            if (fkt := pre.as_fkt_renyo) is not None:
                return fkt + self

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )

    def __add__(self, post: IKatsuyoTextAppendant[A]) -> A:
        # 日本語の特性上、KatsuyoTextの活用形は前に接続される品詞の影響を受ける。
        return post.merge(self)

    @property
    def as_fkt_gokan(self) -> Optional["FixedKatsuyoText"]:
        if isinstance(self.katsuyo, k.MizenMixin):
            return FixedKatsuyoText(
                gokan=self.gokan,
                katsuyo=k.NO_KATSUYO,
            )
        return None

    @property
    def as_fkt_mizen(self) -> Optional["FixedKatsuyoText"]:
        if isinstance(self.katsuyo, k.MizenMixin):
            return FixedKatsuyoText(
                gokan=self.gokan,
                katsuyo=self.katsuyo.mizen,
            )
        return None

    @property
    def as_fkt_renyo(self) -> Optional["FixedKatsuyoText"]:
        if isinstance(self.katsuyo, k.RenyoMixin):
            return FixedKatsuyoText(
                gokan=self.gokan,
                katsuyo=self.katsuyo.renyo,
            )
        return None

    @property
    def as_fkt_shushi(self) -> Optional["FixedKatsuyoText"]:
        if isinstance(self.katsuyo, k.ShushiMixin):
            return FixedKatsuyoText(
                gokan=self.gokan,
                katsuyo=self.katsuyo.shushi,
            )
        return None

    @property
    def as_fkt_rentai(self) -> Optional["FixedKatsuyoText"]:
        if isinstance(self.katsuyo, k.RentaiMixin):
            return FixedKatsuyoText(
                gokan=self.gokan,
                katsuyo=self.katsuyo.rentai,
            )
        return None

    @property
    def as_fkt_katei(self) -> Optional["FixedKatsuyoText"]:
        if isinstance(self.katsuyo, k.KateiMixin):
            return FixedKatsuyoText(
                gokan=self.gokan,
                katsuyo=self.katsuyo.katei,
            )
        return None

    @property
    def as_fkt_meirei(self) -> Optional["FixedKatsuyoText"]:
        if isinstance(self.katsuyo, k.MeireiMixin):
            return FixedKatsuyoText(
                gokan=self.gokan,
                katsuyo=self.katsuyo.meirei,
            )
        return None

    @property
    def as_fkt_mizen_u(self) -> Optional["FixedKatsuyoText"]:
        if isinstance(self.katsuyo, k.MizenUMixin):
            return FixedKatsuyoText(
                gokan=self.gokan,
                katsuyo=self.katsuyo.mizen_u,
            )
        return None

    @property
    def as_fkt_mizen_reru(self) -> Optional["FixedKatsuyoText"]:
        if isinstance(self.katsuyo, k.MizenReruMixin):
            return FixedKatsuyoText(
                gokan=self.gokan,
                katsuyo=self.katsuyo.mizen_reru,
            )
        return None

    @property
    def as_fkt_mizen_rareru(self) -> Optional["FixedKatsuyoText"]:
        if isinstance(self.katsuyo, k.MizenRareruMixin):
            return FixedKatsuyoText(
                gokan=self.gokan,
                katsuyo=self.katsuyo.mizen_rareru,
            )
        return None

    @property
    def as_fkt_renyo_ta(self) -> Optional["FixedKatsuyoText"]:
        if isinstance(self.katsuyo, k.RenyoTaMixin):
            return FixedKatsuyoText(
                gokan=self.gokan,
                katsuyo=self.katsuyo.renyo_ta,
            )
        return None

    @property
    def as_fkt_renyo_nai(self) -> Optional["FixedKatsuyoText"]:
        if isinstance(self.katsuyo, k.RenyoNaiMixin):
            return FixedKatsuyoText(
                gokan=self.gokan,
                katsuyo=self.katsuyo.renyo_nai,
            )
        return None

    def __str__(self):
        return f"{self.gokan}{self.katsuyo}"


@attrs.define(frozen=True, slots=True)
class FixedKatsuyoText(IKatsuyoTextSource, IKatsuyoTextAppendant["FixedKatsuyoText"]):
    """
    活用変形されたKatsuyoTextを格納するクラス。用言を表す。
    """

    gokan: str
    katsuyo: k.FixedKatsuyo

    def merge(self, pre: IKatsuyoTextSource) -> "FixedKatsuyoText":
        """
        基本的には連用形で受けるが、下位クラスで上書きすることで
        任意の活用形に変換して返すことがある。
        """
        # 現状あまり使われないため簡易的な実装
        if isinstance(pre, (FixedKatsuyoText, INonKatsuyoText)):
            return pre + self
        else:
            assert isinstance(pre, KatsuyoText)

            if (fkt := pre.as_fkt_renyo) is not None:
                return fkt + self

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )

    def __add__(self, post: IKatsuyoTextAppendant[A]) -> A:
        # 基本はそのまま引っ付ける
        if isinstance(post, FixedKatsuyoText):
            return FixedKatsuyoText(
                gokan=str(self) + post.gokan,
                katsuyo=post.katsuyo,
            )
        elif isinstance(post, INonKatsuyoText):
            return INonKatsuyoText(
                gokan=str(self) + post.gokan,
            )
        elif isinstance(post, KatsuyoText):
            return KatsuyoText(
                gokan=str(self) + post.gokan,
                katsuyo=post.katsuyo,
            )
        else:
            # gokanやkatsuyoを持たないクラスを想定(e.g., IKatsuyoHelper)
            return post.merge(self)

    def __str__(self):
        return f"{self.gokan}{self.katsuyo}"


@attrs.define(frozen=True, slots=True)
class INonKatsuyoText(IKatsuyoTextSource, IKatsuyoTextAppendant["INonKatsuyoText"]):
    """
    活用形を含まない文字列を表すクラス。
    名詞,助詞,接続詞,感動詞,記号,連体詞,接頭辞,接尾辞,補助記号,フィラー,
    その他,そのままKatsuyoTextにaddする品詞を想定。
    """

    gokan: str
    katsuyo: None = None

    def merge(self, pre: IKatsuyoTextSource) -> "INonKatsuyoText":
        """
        基本的には連体形で受けるが、下位クラスで上書きすることで
        任意の活用形に変換して返すことがある。
        """
        if isinstance(pre, (FixedKatsuyoText, INonKatsuyoText)):
            return pre + self
        else:
            assert isinstance(pre, KatsuyoText)

            if (fkt := pre.as_fkt_rentai) is not None:
                return fkt + self

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )

    def __add__(self, post: IKatsuyoTextAppendant[A]) -> A:
        # 基本はそのまま引っ付ける
        if isinstance(post, FixedKatsuyoText):
            return FixedKatsuyoText(
                gokan=str(self) + post.gokan,
                katsuyo=post.katsuyo,
            )
        elif isinstance(post, INonKatsuyoText):
            return INonKatsuyoText(
                gokan=str(self) + post.gokan,
            )
        elif isinstance(post, KatsuyoText):
            return KatsuyoText(
                gokan=str(self) + post.gokan,
                katsuyo=post.katsuyo,
            )
        else:
            # gokanやkatsuyoを持たないクラスを想定(e.g., IKatsuyoHelper)
            return post.merge(self)

    def __str__(self):
        return self.gokan


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


class HojoKatsuyoText(KatsuyoText):
    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self
        elif isinstance(pre, INonKatsuyoText):
            if isinstance(pre, JoshiText):
                # TODO 助詞の精査
                return pre + self

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
                if isinstance(pre.katsuyo, k.GodanKatsuyo) and (
                    pre.katsuyo.shushi in ["ぐ", "ぬ", "ぶ", "む"]
                ):
                    return pre + Da() + self
                return pre + Ta() + self
            elif isinstance(pre.katsuyo, k.KeiyoushiKatsuyo):
                assert (fkt := pre.as_fkt_renyo) is not None
                return fkt + self
            elif isinstance(pre.katsuyo, k.KeiyoudoushiKatsuyo):
                assert (fkt := pre.as_fkt_renyo_nai) is not None
                return fkt + self

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


HOZYO_NAI = HojoKatsuyoText(
    gokan="な",
    katsuyo=k.KEIYOUSHI,
)

HOZYO_ARU = HojoKatsuyoText(
    gokan="あ",
    katsuyo=k.GODAN_RA_GYO,
)

HOZYO_IRU = HojoKatsuyoText(
    gokan="い",
    katsuyo=k.KAMI_ICHIDAN,
)

# ==============================================================================
# 助動詞
# see: https://ja.wikipedia.org/wiki/助動詞_(国文法)
# ==============================================================================


class JodoushiKatsuyoText(KatsuyoText):
    @property
    def katsuyo_text(self) -> KatsuyoText:
        return KatsuyoText(
            gokan=self.gokan,
            katsuyo=self.katsuyo,
        )


# ==============================================================================
# 助動詞::受身
# ==============================================================================


class Reru(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="れ",
            katsuyo=k.SHIMO_ICHIDAN,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
                if isinstance(pre.katsuyo, k.SaGyoHenkakuKatsuyo):
                    assert (fkt := pre.as_fkt_mizen_reru) is not None
                    return fkt + self.katsuyo_text
                assert (fkt := pre.as_fkt_mizen) is not None
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


class Rareru(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="られ",
            katsuyo=k.SHIMO_ICHIDAN,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
                if isinstance(pre.katsuyo, k.SaGyoHenkakuKatsuyo):
                    assert (fkt := pre.as_fkt_mizen_rareru) is not None
                    return fkt + self.katsuyo_text
                assert (fkt := pre.as_fkt_mizen) is not None
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


# ==============================================================================
# 助動詞::使役
# ==============================================================================


class Seru(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="せ",
            katsuyo=k.SHIMO_ICHIDAN,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
                if isinstance(pre.katsuyo, k.SaGyoHenkakuKatsuyo):
                    assert (fkt := pre.as_fkt_mizen_reru) is not None
                    return fkt + self.katsuyo_text
                assert (fkt := pre.as_fkt_mizen) is not None
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


class Saseru(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="させ",
            katsuyo=k.SHIMO_ICHIDAN,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
                # サ変活用「〜ずる」には未然形「〜じ させる」を採用したため他と同一の未然形に
                assert (fkt := pre.as_fkt_mizen) is not None
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


# ==============================================================================
# 助動詞::否定
# ==============================================================================


class Nai(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="な",
            katsuyo=k.KEIYOUSHI,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            # 精査してもいいかもしれない
            return pre + self.katsuyo_text
        else:
            assert isinstance(pre, KatsuyoText)

            if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
                assert (fkt := pre.as_fkt_mizen) is not None
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


# ==============================================================================
# 助動詞::希望
# ==============================================================================


class Tai(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="た",
            katsuyo=k.KEIYOUSHI,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
                assert (fkt := pre.as_fkt_renyo) is not None
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


class Tagaru(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="たが",
            katsuyo=k.GODAN_RA_GYO,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
                assert (fkt := pre.as_fkt_renyo) is not None
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


# ==============================================================================
# 助動詞::過去・完了
# ==============================================================================


class Ta(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="",
            katsuyo=k.ZYODOUSHI_TA,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if (fkt := pre.as_fkt_renyo_ta) is not None:
                return fkt + self.katsuyo_text
            elif (fkt := pre.as_fkt_renyo) is not None:
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


class Da(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="",
            katsuyo=k.ZYODOUSHI_DA,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if (fkt := pre.as_fkt_renyo_ta) is not None:
                return fkt + self.katsuyo_text
            elif (fkt := pre.as_fkt_renyo) is not None:
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


# ==============================================================================
# 助動詞::様態
# ==============================================================================


class SoudaYoutai(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="そう",
            katsuyo=k.KEIYOUDOUSHI,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if isinstance(pre.katsuyo, (k.KeiyoushiKatsuyo, k.KeiyoudoushiKatsuyo)):
                assert (fkt := pre.as_fkt_gokan) is not None
                return fkt + self.katsuyo_text
            elif (fkt := pre.as_fkt_renyo) is not None:
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


# ==============================================================================
# 助動詞::伝聞
# ==============================================================================


class SoudaDenbun(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="そう",
            # NOTE: 本来「伝聞」の活用系は形容動詞とは異なる(e.g., 未然形が存在しない)
            #       現状の意味を厳密に扱わない状態においては、形容動詞の活用系を使う
            katsuyo=k.KEIYOUDOUSHI,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if (fkt := pre.as_fkt_shushi) is not None:
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


# ==============================================================================
# 助動詞::推定
# ==============================================================================


class Rashii(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="らし",
            # NOTE: 本来の活用系は形容詞とは異なる(e.g., 未然形が存在しない)
            #       現状の意味を厳密に扱わない状態においては、形容詞の活用系を使う
            katsuyo=k.KEIYOUSHI,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            if isinstance(pre, TaigenText):
                return pre + self.katsuyo_text
            elif isinstance(pre, JoshiText):
                # TODO 助詞の精査
                return pre + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if isinstance(pre.katsuyo, k.KeiyoudoushiKatsuyo):
                assert (fkt := pre.as_fkt_gokan) is not None
                return fkt + self.katsuyo_text
            elif (fkt := pre.as_fkt_shushi) is not None:
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


# ==============================================================================
# 助動詞::当然
# ==============================================================================


class Bekida(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="べき",
            katsuyo=k.KEIYOUDOUSHI,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
                assert (fkt := pre.as_fkt_shushi) is not None
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


# ==============================================================================
# 助動詞::比況 例示 推定
# ==============================================================================


class Youda(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="よう",
            katsuyo=k.KEIYOUDOUSHI,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            if isinstance(pre, JoshiText):
                # TODO 助詞の精査
                return pre + self.katsuyo_text

            # 定義上は連体詞「この」等に接続するが、現状はサポートしない

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if (fkt := pre.as_fkt_rentai) is not None:
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


# ==============================================================================
# 助動詞::継続
# 助動詞の参照リンクには含まれないが、口語では頻出されるため追記
# ref. https://ja.wiktionary.org/wiki/てる#助動詞
# ==============================================================================


class Teiru(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="てい",
            katsuyo=k.KAMI_ICHIDAN,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if (fkt := pre.as_fkt_renyo_ta) is not None:
                return fkt + self.katsuyo_text
            elif (fkt := pre.as_fkt_renyo) is not None:
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


class Deiru(JodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            gokan="でい",
            katsuyo=k.KAMI_ICHIDAN,
        )

    def merge(self, pre: IKatsuyoTextSource) -> KatsuyoText:
        if isinstance(pre, FixedKatsuyoText):
            return pre + self.katsuyo_text
        if isinstance(pre, INonKatsuyoText):
            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in merge of {type(self)}: "
                f"{pre} type: {type(pre)}"
            )
        else:
            assert isinstance(pre, KatsuyoText)

            if (fkt := pre.as_fkt_renyo_ta) is not None:
                return fkt + self.katsuyo_text
            elif (fkt := pre.as_fkt_renyo) is not None:
                return fkt + self.katsuyo_text

            raise KatsuyoTextError(
                f"Unsupported katsuyo_text in {type(self)}: {pre} "
                f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
            )


# ==============================================================================
# 体言
# ref. https://ja.wiktionary.org/wiki/体言
# ==============================================================================


class TaigenText(INonKatsuyoText):
    """体言"""

    pass


# ==============================================================================
# 動詞
# 細かく分類せず、動詞として扱うものをまとめる
# e.g. 格助詞,格助詞,接続助詞
#
# ref. https://ja.wikipedia.org/wiki/助詞
# ==============================================================================


class JoshiText(INonKatsuyoText):
    pass


NI = JoshiText("に")

DE = JoshiText("で")

HA = JoshiText("は")

DA = JoshiText("だ")

NO = JoshiText("の")
