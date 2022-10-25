from collections.abc import Callable
from typing import Optional, cast
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    KatsuyoTextError,
    IKatsuyoTextSource,
)
import abc
import sys
import spacy_dialog_reflection.lang.ja.katsuyo as k
import spacy_dialog_reflection.lang.ja.katsuyo_text as kt


class IKatsuyoTextHelper(kt.IKatsuyoTextAppendant):
    """
    柔軟に活用系を変換するためのクラス
    """

    BridgeFunction = Callable[[kt.IKatsuyoTextSource], kt.IKatsuyoTextSource]

    def __init__(
        self,
        bridge: Optional[BridgeFunction] = None,
    ) -> None:
        self.bridge = bridge
        """
        文法的には不正な活用形の組み合わせを
        任意の活用形に変換して返せるようにするための関数
        """

    def merge(self, pre: kt.IKatsuyoTextSource) -> kt.IKatsuyoTextSource:
        result = self.try_merge(pre)
        if result is not None:
            return result
        if self.bridge is not None:
            return self.bridge(pre)

        err_attr_katsuyo_type = (
            f"katsuyo: {type(pre.katsuyo)}" if isinstance(pre, kt.KatsuyoText) else None
        )
        raise kt.KatsuyoTextError(
            f"Unsupported katsuyo_text in merge of {type(self)}: {pre} "
            f"type: {type(pre)} {err_attr_katsuyo_type}"
        )

    @abc.abstractmethod
    def try_merge(self, pre: kt.IKatsuyoTextSource) -> Optional[kt.IKatsuyoTextSource]:
        raise NotImplementedError()


# ==============================================================================
# 助動詞::受身
# ==============================================================================


def bridge_Ukemi_default(pre: IKatsuyoTextSource) -> kt.KatsuyoText:
    # デフォルトでは動詞「なる」でブリッジ
    naru = kt.KatsuyoText(
        gokan="な",
        katsuyo=k.GODAN_RA_GYO,
    )

    if isinstance(pre, (kt.INonKatsuyoText)):
        ni = kt.INonKatsuyoText("に")
        return cast(kt.KatsuyoText, pre + ni + naru + kt.Reru())

    if type(pre.katsuyo) is k.KeiyoushiKatsuyo:
        return cast(
            kt.KatsuyoText,
            pre + naru + kt.Reru(),
        )
    elif type(pre.katsuyo) is k.KeiyoudoushiKatsuyo:
        return cast(
            kt.KatsuyoText,
            pre + naru + kt.Reru(),
        )

    raise KatsuyoTextError(
        f"Unsupported katsuyo_text in {sys._getframe().f_code.co_name}: {pre} "
        f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
    )


class Ukemi(IKatsuyoTextHelper):
    def __init__(
        self,
        bridge: Optional[IKatsuyoTextHelper.BridgeFunction] = bridge_Ukemi_default,
    ) -> None:
        super().__init__(bridge)

    def try_merge(self, pre: IKatsuyoTextSource) -> Optional[kt.KatsuyoText]:
        if isinstance(pre, kt.INonKatsuyoText):
            return None
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            # サ行変格活用のみ特殊
            if type(pre.katsuyo) is k.SaGyoHenkakuKatsuyo:
                # 用法的に「〜する」は「れる/られる」どちらでもよいため固定
                # 用法的に「〜ずる」は文語が多いため未然形「〜ぜ られる」を採用
                if pre.katsuyo.shushi == "する":
                    return cast(kt.KatsuyoText, pre + kt.Reru())
                elif pre.katsuyo.shushi == "ずる":
                    return cast(kt.KatsuyoText, pre + kt.Rareru())

            mizen = pre.katsuyo.mizen
            if mizen and mizen[-1] in k.DAN["あ"]:
                return cast(kt.KatsuyoText, pre + kt.Reru())
            else:
                return cast(kt.KatsuyoText, pre + kt.Rareru())

        return None


# ==============================================================================
# 助動詞::使役
# ==============================================================================


def bridge_Shieki_default(pre: IKatsuyoTextSource) -> kt.KatsuyoText:
    if isinstance(pre, kt.INonKatsuyoText):
        ni = kt.INonKatsuyoText("に")
        return cast(kt.KatsuyoText, pre + ni + kt.Saseru())

    if type(pre.katsuyo) is k.KeiyoushiKatsuyo:
        # 「させる」を動詞として扱い連用形でブリッジ
        renyo = pre.katsuyo.renyo
        return cast(
            kt.KatsuyoText,
            kt.INonKatsuyoText(pre.gokan + renyo) + kt.Saseru(),
        )
    elif type(pre.katsuyo) is k.KeiyoudoushiKatsuyo:
        # 「させる」を動詞として扱い連用形でブリッジ
        renyo = pre.katsuyo.renyo
        return cast(
            kt.KatsuyoText,
            kt.INonKatsuyoText(pre.gokan + renyo) + kt.Saseru(),
        )

    raise KatsuyoTextError(
        f"Unsupported katsuyo_text in {sys._getframe().f_code.co_name}: {pre} "
        f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
    )


class Shieki(IKatsuyoTextHelper):
    def __init__(
        self,
        bridge: Optional[IKatsuyoTextHelper.BridgeFunction] = bridge_Shieki_default,
    ) -> None:
        super().__init__(bridge)

    def try_merge(self, pre: IKatsuyoTextSource) -> Optional[kt.KatsuyoText]:
        if isinstance(pre, kt.INonKatsuyoText):
            return None
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            # サ行変格活用のみ特殊
            if type(pre.katsuyo) is k.SaGyoHenkakuKatsuyo:
                # 用法的に「〜する」は「せる/させる」どちらでもよいため固定
                # 用法的に「〜ずる」は「〜じ させる」を採用
                if pre.katsuyo.shushi == "する":
                    return cast(kt.KatsuyoText, pre + kt.Seru())
                elif pre.katsuyo.shushi == "ずる":
                    return cast(kt.KatsuyoText, pre + kt.Saseru())

            mizen = pre.katsuyo.mizen
            if mizen and mizen[-1] in k.DAN["あ"]:
                return cast(kt.KatsuyoText, pre + kt.Seru())
            else:
                return cast(kt.KatsuyoText, pre + kt.Saseru())

        return None


# ==============================================================================
# 助動詞::否定
# ==============================================================================


def bridge_Hitei_default(pre: IKatsuyoTextSource) -> kt.KatsuyoText:
    if isinstance(pre, kt.INonKatsuyoText):
        # TODO 助詞のハンドリング
        deha = kt.INonKatsuyoText("では")
        return cast(kt.KatsuyoText, pre + deha + kt.Nai())

    if type(pre.katsuyo) is k.KeiyoushiKatsuyo:
        # 「ない」を形容詞として扱い連用形でブリッジ
        renyo = pre.katsuyo.renyo
        return cast(
            kt.KatsuyoText,
            kt.INonKatsuyoText(pre.gokan + renyo) + kt.Nai(),
        )
    elif type(pre.katsuyo) is k.KeiyoudoushiKatsuyo:
        # 「ない」を形容詞として扱い連用形でブリッジ
        # 形容動詞は「ない」には特殊な形式で紐づく
        renyo_nai = pre.katsuyo.renyo_nai
        return cast(
            kt.KatsuyoText,
            kt.INonKatsuyoText(pre.gokan + renyo_nai) + kt.Nai(),
        )

    raise KatsuyoTextError(
        f"Unsupported katsuyo_text in {sys._getframe().f_code.co_name}: {pre} "
        f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
    )


class Hitei(IKatsuyoTextHelper):
    # 現状、出力文字列としては「ない」のみサポート
    # TODO オプションで「ぬ」を選択できるように

    def __init__(
        self,
        bridge: Optional[IKatsuyoTextHelper.BridgeFunction] = bridge_Hitei_default,
    ) -> None:
        super().__init__(bridge)

    def try_merge(self, pre: IKatsuyoTextSource) -> Optional[kt.KatsuyoText]:
        if isinstance(pre, kt.INonKatsuyoText):
            return None
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            return cast(kt.KatsuyoText, pre + kt.Nai())

        return None


# ==============================================================================
# 助動詞::希望
# ==============================================================================


class KibouSelf(IKatsuyoTextHelper):
    def __init__(
        self,
        # デフォルトでは特に何もbridgeしない
        bridge: Optional[IKatsuyoTextHelper.BridgeFunction] = None,
    ) -> None:
        super().__init__(bridge)

    def try_merge(self, pre: IKatsuyoTextSource) -> Optional[kt.KatsuyoText]:
        if isinstance(pre, kt.INonKatsuyoText):
            return None
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            return cast(kt.KatsuyoText, pre + kt.Tai())

        return None


class KibouOthers(IKatsuyoTextHelper):
    def __init__(
        self,
        # デフォルトでは特に何もbridgeしない
        bridge: Optional[IKatsuyoTextHelper.BridgeFunction] = None,
    ) -> None:
        super().__init__(bridge)

    def try_merge(self, pre: IKatsuyoTextSource) -> Optional[kt.KatsuyoText]:
        if isinstance(pre, kt.INonKatsuyoText):
            return None
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            return cast(kt.KatsuyoText, pre + kt.Tagaru())

        return None


# ==============================================================================
# 助動詞::過去/完了/存続/確認
# ==============================================================================


def bridge_KakoKanryo_default(pre: IKatsuyoTextSource) -> kt.KatsuyoText:
    if isinstance(pre, kt.INonKatsuyoText):
        # TODO 助詞のハンドリング
        dat = kt.INonKatsuyoText("だっ")
        return cast(kt.KatsuyoText, pre + dat + kt.Ta())

    raise KatsuyoTextError(
        f"Unsupported katsuyo_text in {sys._getframe().f_code.co_name}: {pre} "
        f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
    )


class KakoKanryo(IKatsuyoTextHelper):
    def __init__(
        self,
        bridge: Optional[IKatsuyoTextHelper.BridgeFunction] = bridge_KakoKanryo_default,
    ) -> None:
        super().__init__(bridge)

    def try_merge(self, pre: IKatsuyoTextSource) -> Optional[kt.KatsuyoText]:
        if isinstance(pre, kt.INonKatsuyoText):
            return None
        if isinstance(pre.katsuyo, k.RenyoMixin):
            if isinstance(pre.katsuyo, k.GodanKatsuyo) and (
                pre.katsuyo.shushi in ["ぐ", "ぬ", "ぶ", "む"]
            ):
                return cast(kt.KatsuyoText, pre + kt.Da())

            return cast(kt.KatsuyoText, pre + kt.Ta())

        return None


# ==============================================================================
# 助動詞::様態
# ==============================================================================


def bridge_Youtai_default(pre: IKatsuyoTextSource) -> kt.KatsuyoText:
    if isinstance(pre, kt.INonKatsuyoText):
        # TODO 助詞のハンドリング(体言のみ許容し助詞はエラー)
        return cast(kt.KatsuyoText, pre + kt.SoudaYoutai())

    raise KatsuyoTextError(
        f"Unsupported katsuyo_text in {sys._getframe().f_code.co_name}: {pre} "
        f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
    )


class Youtai(IKatsuyoTextHelper):
    def __init__(
        self,
        bridge: Optional[IKatsuyoTextHelper.BridgeFunction] = bridge_Youtai_default,
    ) -> None:
        super().__init__(bridge)

    def try_merge(self, pre: IKatsuyoTextSource) -> Optional[kt.KatsuyoText]:
        if isinstance(pre, kt.INonKatsuyoText):
            return None
        if isinstance(pre.katsuyo, k.RenyoMixin):
            return cast(kt.KatsuyoText, pre + kt.SoudaYoutai())

        return None


# ==============================================================================
# 助動詞::伝聞
# ==============================================================================


def bridge_Denbun_default(pre: IKatsuyoTextSource) -> kt.KatsuyoText:
    if isinstance(pre, kt.INonKatsuyoText):
        dearu = kt.INonKatsuyoText("だ")
        return cast(kt.KatsuyoText, pre + dearu + kt.SoudaDenbun())

    raise KatsuyoTextError(
        f"Unsupported katsuyo_text in {sys._getframe().f_code.co_name}: {pre} "
        f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
    )


class Denbun(IKatsuyoTextHelper):
    def __init__(
        self,
        bridge: Optional[IKatsuyoTextHelper.BridgeFunction] = bridge_Denbun_default,
    ) -> None:
        super().__init__(bridge)

    def try_merge(self, pre: IKatsuyoTextSource) -> Optional[kt.KatsuyoText]:
        if isinstance(pre, kt.INonKatsuyoText):
            return None
        if isinstance(pre.katsuyo, k.ShushiMixin):
            return cast(kt.KatsuyoText, pre + kt.SoudaDenbun())

        return None


# ==============================================================================
# 助動詞::伝聞
# ==============================================================================


def bridge_Suitei_default(pre: IKatsuyoTextSource) -> kt.KatsuyoText:
    # TODO 文法的にも体言に紐づけることができるため
    #      try_mergeにこのロジックを移植できるようにする
    if isinstance(pre, kt.INonKatsuyoText):
        return cast(kt.KatsuyoText, pre + kt.Rashii())

    raise KatsuyoTextError(
        f"Unsupported katsuyo_text in {sys._getframe().f_code.co_name}: {pre} "
        f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
    )


class Suitei(IKatsuyoTextHelper):
    def __init__(
        self,
        bridge: Optional[IKatsuyoTextHelper.BridgeFunction] = bridge_Suitei_default,
    ) -> None:
        super().__init__(bridge)

    def try_merge(self, pre: IKatsuyoTextSource) -> Optional[kt.KatsuyoText]:
        if isinstance(pre, kt.INonKatsuyoText):
            return None
        if isinstance(pre.katsuyo, k.ShushiMixin):
            return cast(kt.KatsuyoText, pre + kt.Rashii())

        return None


# ==============================================================================
# 助動詞::当然
# ==============================================================================


def bridge_Touzen_default(pre: IKatsuyoTextSource) -> kt.KatsuyoText:
    # デフォルトでは動詞「ある」でブリッジ
    aru = kt.KatsuyoText(
        gokan="あ",
        katsuyo=k.GODAN_RA_GYO,
    )

    if isinstance(pre, kt.INonKatsuyoText):
        de = kt.INonKatsuyoText("で")
        return cast(kt.KatsuyoText, pre + de + aru + kt.Bekida())

    if type(pre.katsuyo) is k.KeiyoushiKatsuyo:
        return cast(kt.KatsuyoText, pre + aru + kt.Bekida())
    elif type(pre.katsuyo) is k.KeiyoudoushiKatsuyo:
        # 形容動詞は「ある」には特殊な形式で紐づく
        renyo_nai = pre.katsuyo.renyo_nai
        return cast(
            kt.KatsuyoText,
            kt.INonKatsuyoText(pre.gokan + renyo_nai) + aru + kt.Bekida(),
        )

    raise KatsuyoTextError(
        f"Unsupported katsuyo_text in {sys._getframe().f_code.co_name}: {pre} "
        f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
    )


class Touzen(IKatsuyoTextHelper):
    def __init__(
        self,
        bridge: Optional[IKatsuyoTextHelper.BridgeFunction] = bridge_Touzen_default,
    ) -> None:
        super().__init__(bridge)

    def try_merge(self, pre: IKatsuyoTextSource) -> Optional[kt.KatsuyoText]:
        if isinstance(pre, kt.INonKatsuyoText):
            return None
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            return cast(kt.KatsuyoText, pre + kt.Bekida())

        return None


# ==============================================================================
# 助動詞::比況 例示 推定
# ==============================================================================


def bridge_HikyoReizi_default(pre: IKatsuyoTextSource) -> kt.KatsuyoText:
    if isinstance(pre, kt.INonKatsuyoText):
        no = kt.INonKatsuyoText("の")
        return cast(kt.KatsuyoText, pre + no + kt.Youda())

    raise KatsuyoTextError(
        f"Unsupported katsuyo_text in {sys._getframe().f_code.co_name}: {pre} "
        f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
    )


# NOTE: 文法的には連体詞「この」等に紐づけることができるが
#       文末表現として「このようだ」となる際はrootに「よう」がつくため
#       文末の品詞を分解する機能として扱ううえでは
#       「比況」にて連体詞を扱うロジックはIKatsuyoTextHelperに含めない
class HikyoReizi(IKatsuyoTextHelper):
    def __init__(
        self,
        bridge: Optional[IKatsuyoTextHelper.BridgeFunction] = bridge_HikyoReizi_default,
    ) -> None:
        super().__init__(bridge)

    def try_merge(self, pre: IKatsuyoTextSource) -> Optional[kt.KatsuyoText]:
        if isinstance(pre, kt.INonKatsuyoText):
            return None
        if isinstance(pre.katsuyo, k.RentaiMixin):
            return cast(kt.KatsuyoText, pre + kt.Youda())

        return None


# ==============================================================================
# 助動詞::継続
# ==============================================================================


def bridge_Keizoku_default(pre: IKatsuyoTextSource) -> kt.KatsuyoText:
    if isinstance(pre, kt.INonKatsuyoText):
        return cast(kt.KatsuyoText, pre + kt.Deiru())

    if type(pre.katsuyo) is k.KeiyoushiKatsuyo:
        # 形容詞では「いる」でブリッジ
        iru = kt.KatsuyoText(
            gokan="い",
            katsuyo=k.KAMI_ICHIDAN,
        )
        return cast(kt.KatsuyoText, pre + iru)
    elif type(pre.katsuyo) is k.KeiyoudoushiKatsuyo:
        return cast(
            kt.KatsuyoText,
            kt.INonKatsuyoText(pre.gokan) + kt.Deiru(),
        )

    raise KatsuyoTextError(
        f"Unsupported katsuyo_text in {sys._getframe().f_code.co_name}: {pre} "
        f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
    )


class Keizoku(IKatsuyoTextHelper):
    # 現状、出力文字列としては「ている」「でいる」のみサポート
    # TODO オプションで「てる」「でる」を選択できるように

    def __init__(
        self,
        bridge: Optional[IKatsuyoTextHelper.BridgeFunction] = bridge_Keizoku_default,
    ) -> None:
        super().__init__(bridge)

    def try_merge(self, pre: IKatsuyoTextSource) -> Optional[kt.KatsuyoText]:
        if isinstance(pre, kt.INonKatsuyoText):
            return None
        if isinstance(pre.katsuyo, k.IDoushiKatsuyo):
            if isinstance(pre.katsuyo, k.GodanKatsuyo) and (
                pre.katsuyo.shushi in ["ぐ", "ぬ", "ぶ", "む"]
            ):
                return cast(kt.KatsuyoText, pre + kt.Deiru())

            return cast(kt.KatsuyoText, pre + kt.Teiru())

        return None
