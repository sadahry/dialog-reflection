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
        return cast(kt.KatsuyoText, pre + kt.NI + naru + kt.Reru())

    if isinstance(
        pre.katsuyo,
        (k.KeiyoushiKatsuyo, k.KeiyoudoushiKatsuyo),
    ):
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
        # 「させる」を動詞として扱い「に」でブリッジ
        return cast(kt.KatsuyoText, pre + kt.NI + kt.Saseru().katsuyo_text)

    if isinstance(
        pre.katsuyo,
        (k.KeiyoushiKatsuyo, k.KeiyoudoushiKatsuyo),
    ):
        # 「させる」を動詞として扱い連用形でブリッジ
        return cast(kt.KatsuyoText, pre + kt.Saseru().katsuyo_text)

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
        # TODO 「で」にも切り替えられるように
        return cast(kt.KatsuyoText, pre + kt.DE + kt.HA + kt.Nai())

    if isinstance(
        pre.katsuyo,
        (k.KeiyoushiKatsuyo, k.KeiyoudoushiKatsuyo),
    ):
        # 「ない」を補助形容詞としてブリッジ
        return cast(kt.KatsuyoText, pre + kt.HOZYO_NAI)

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
        da = kt.KatsuyoText(
            gokan="",
            katsuyo=k.KEIYOUDOUSHI,
        )
        return cast(kt.KatsuyoText, pre + da + kt.Ta())

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
        return cast(kt.KatsuyoText, pre + kt.DA + kt.SoudaDenbun())

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
    if isinstance(pre, kt.INonKatsuyoText):
        return cast(
            kt.KatsuyoText,
            pre + kt.DE + kt.HOZYO_ARU + kt.Bekida(),
        )

    if isinstance(
        pre.katsuyo,
        (k.KeiyoushiKatsuyo, k.KeiyoudoushiKatsuyo),
    ):
        # 補助動詞「ある」でブリッジ
        return cast(
            kt.KatsuyoText,
            pre + kt.HOZYO_ARU + kt.Bekida(),
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
        return cast(kt.KatsuyoText, pre + kt.NO + kt.Youda())

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

    if isinstance(
        pre.katsuyo,
        (k.KeiyoushiKatsuyo, k.KeiyoudoushiKatsuyo),
    ):
        # 形容詞/形容動詞では「いる」でブリッジ
        return cast(kt.KatsuyoText, pre + kt.HOZYO_IRU)

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
