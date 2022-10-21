from collections.abc import Callable
from typing import Optional, Union, cast
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    IKatsuyoTextHelper,
)
import spacy_dialog_reflection.lang.ja.katsuyo as k
import spacy_dialog_reflection.lang.ja.katsuyo_text as kt


# TODO このクラスは、KatsuyoTextBuilder的な名前のクラスに変更する
#      gokan等が必要なく、KatsuyoTextを返すだけのクラスにする
class Ukemi(kt.IKatsuyoTextHelper):
    def __init__(
        self,
        bridge: Optional[
            Callable[[Union[kt.KatsuyoText, kt.NonKatsuyoText]], kt.KatsuyoText]
        ] = None,
    ) -> None:
        if bridge is None:

            def __default(
                pre: Union[kt.KatsuyoText, kt.NonKatsuyoText]
            ) -> kt.KatsuyoText:
                # デフォルトでは動詞「なる」でブリッジ
                naru = kt.KatsuyoText(
                    gokan="な",
                    katsuyo=k.GODAN_RA_GYO,
                )

                if issubclass(
                    type(pre),
                    (kt.NonKatsuyoText),
                ):
                    pre = cast(kt.NonKatsuyoText, pre)
                    ni = kt.NonKatsuyoText("に")
                    return cast(kt.KatsuyoText, pre + ni + naru + kt.Reru())

                pre = cast(kt.KatsuyoText, pre)

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

                raise ValueError(
                    f"Unsupported katsuyo_text in {type(self)}: {pre} "
                    f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
                )

            bridge = __default

        super().__init__(bridge)

    def try_merge(self, pre: kt.KatsuyoText) -> Optional[kt.KatsuyoText]:
        if issubclass(type(pre.katsuyo), k.DoushiKatsuyo):
            # サ行変格活用のみ特殊
            if type(pre.katsuyo) is k.SaGyoHenkakuKatsuyo:
                # 用法的に「〜する」は「れる/られる」どちらでもよいため固定
                # 用法的に「〜ずる」は文語が多いため未然形「〜ぜ られる」を採用
                if pre.katsuyo.shushi == "する":
                    return cast(kt.KatsuyoText, pre + kt.Reru())
                elif pre.katsuyo.shushi == "ずる":
                    return cast(kt.KatsuyoText, pre + kt.Rareru())

            mizen = cast(k.DoushiKatsuyo, pre.katsuyo).mizen
            if mizen and mizen in k.DAN["あ"]:
                return cast(kt.KatsuyoText, pre + kt.Reru())
            else:
                return cast(kt.KatsuyoText, pre + kt.Rareru())

        return None


class Shieki(IKatsuyoTextHelper):
    def __init__(
        self,
        bridge: Optional[
            Callable[[Union[kt.KatsuyoText, kt.NonKatsuyoText]], kt.KatsuyoText]
        ] = None,
    ) -> None:
        if bridge is None:

            def __default(
                pre: Union[kt.KatsuyoText, kt.NonKatsuyoText]
            ) -> kt.KatsuyoText:
                if issubclass(
                    type(pre),
                    (kt.NonKatsuyoText),
                ):
                    pre = cast(kt.NonKatsuyoText, pre)
                    ni = kt.NonKatsuyoText("に")
                    return cast(kt.KatsuyoText, pre + ni + kt.Saseru())

                pre = cast(kt.KatsuyoText, pre)

                if type(pre.katsuyo) is k.KeiyoushiKatsuyo:
                    # 「させる」を動詞として扱い連用形でブリッジ
                    renyo = pre.katsuyo.renyo
                    return cast(
                        kt.KatsuyoText,
                        kt.NonKatsuyoText(pre.gokan + renyo) + kt.Saseru(),
                    )
                elif type(pre.katsuyo) is k.KeiyoudoushiKatsuyo:
                    # 「させる」を動詞として扱い連用形でブリッジ
                    renyo = pre.katsuyo.renyo
                    return cast(
                        kt.KatsuyoText,
                        kt.NonKatsuyoText(pre.gokan + renyo) + kt.Saseru(),
                    )

                raise ValueError(
                    f"Unsupported katsuyo_text in {type(self)}: {pre} "
                    f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
                )

            bridge = __default

        super().__init__(bridge)

    def try_merge(self, pre: kt.KatsuyoText) -> Optional[kt.KatsuyoText]:
        if issubclass(type(pre.katsuyo), k.DoushiKatsuyo):
            # サ行変格活用のみ特殊
            if type(pre.katsuyo) is k.SaGyoHenkakuKatsuyo:
                # 用法的に「〜する」は「せる/させる」どちらでもよいため固定
                # 用法的に「〜ずる」は「〜じ させる」を採用
                if pre.katsuyo.shushi == "する":
                    return cast(kt.KatsuyoText, pre + kt.Seru())
                elif pre.katsuyo.shushi == "ずる":
                    return cast(kt.KatsuyoText, pre + kt.Saseru())

            mizen = cast(k.DoushiKatsuyo, pre.katsuyo).mizen
            if mizen and mizen in k.DAN["あ"]:
                return cast(kt.KatsuyoText, pre + kt.Seru())
            else:
                return cast(kt.KatsuyoText, pre + kt.Saseru())

        return None


# 否定
class Hitei(IKatsuyoTextHelper):
    # 現状、出力文字列としては「ない」のみサポート
    # TODO オプションで「ぬ」を選択できるように

    def __init__(
        self,
        bridge: Optional[
            Callable[[Union[kt.KatsuyoText, kt.NonKatsuyoText]], kt.KatsuyoText]
        ] = None,
    ) -> None:
        if bridge is None:

            def __default(
                pre: Union[kt.KatsuyoText, kt.NonKatsuyoText]
            ) -> kt.KatsuyoText:
                if issubclass(
                    type(pre),
                    (kt.NonKatsuyoText),
                ):
                    pre = cast(kt.NonKatsuyoText, pre)
                    # TODO 助詞のハンドリング
                    deha = kt.NonKatsuyoText("では")
                    return cast(kt.KatsuyoText, pre + deha + kt.Nai())

                pre = cast(kt.KatsuyoText, pre)

                if type(pre.katsuyo) is k.KeiyoushiKatsuyo:
                    # 「ない」を形容詞として扱い連用形でブリッジ
                    renyo = pre.katsuyo.renyo
                    return cast(
                        kt.KatsuyoText,
                        kt.NonKatsuyoText(pre.gokan + renyo) + kt.Nai(),
                    )
                elif type(pre.katsuyo) is k.KeiyoudoushiKatsuyo:
                    # 「ない」を形容詞として扱い連用形でブリッジ
                    # 形容動詞は「ない」には特殊な形式で紐づく
                    renyo_nai = pre.katsuyo.renyo_nai
                    return cast(
                        kt.KatsuyoText,
                        kt.NonKatsuyoText(pre.gokan + renyo_nai) + kt.Nai(),
                    )

                raise ValueError(
                    f"Unsupported katsuyo_text in {type(self)}: {pre} "
                    f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
                )

            bridge = __default

        super().__init__(bridge)

    def try_merge(self, pre: kt.KatsuyoText) -> Optional[kt.KatsuyoText]:
        if issubclass(type(pre.katsuyo), k.DoushiKatsuyo):
            return cast(kt.KatsuyoText, pre + kt.Nai())

        return None


# 自分の希望
class KibouSelf(IKatsuyoTextHelper):
    def __init__(
        self,
        bridge: Optional[
            Callable[[Union[kt.KatsuyoText, kt.NonKatsuyoText]], kt.KatsuyoText]
        ] = None,
    ) -> None:
        if bridge is None:

            def __default(
                pre: Union[kt.KatsuyoText, kt.NonKatsuyoText]
            ) -> kt.KatsuyoText:
                # デフォルトでは特に何もしない
                # 「なりたい」「ありたい」「したい」など多様な選択肢が考えられるため
                raise ValueError(
                    f"Unsupported katsuyo_text in KibouSelf: {pre} type: {type(pre)}"
                )

            bridge = __default

        super().__init__(bridge)

    def try_merge(self, pre: kt.KatsuyoText) -> Optional[kt.KatsuyoText]:
        if issubclass(type(pre.katsuyo), k.DoushiKatsuyo):
            return cast(kt.KatsuyoText, pre + kt.Tai())

        return None


class KibouOthers(IKatsuyoTextHelper):
    def __init__(
        self,
        bridge: Optional[
            Callable[[Union[kt.KatsuyoText, kt.NonKatsuyoText]], kt.KatsuyoText]
        ] = None,
    ) -> None:
        if bridge is None:

            def __default(
                pre: Union[kt.KatsuyoText, kt.NonKatsuyoText]
            ) -> kt.KatsuyoText:
                # デフォルトでは特に何もしない
                # 「なりたがる」「ありたがる」「したがる」など多様な選択肢が考えられるため
                raise ValueError(
                    f"Unsupported katsuyo_text in KibouOthers: {pre} type: {type(pre)}"
                )

            bridge = __default

        super().__init__(bridge)

    def try_merge(self, pre: kt.KatsuyoText) -> Optional[kt.KatsuyoText]:
        if issubclass(type(pre.katsuyo), k.DoushiKatsuyo):
            return cast(kt.KatsuyoText, pre + kt.Tagaru())

        return None


# 過去/完了/存続/確認
class KakoKanryo(IKatsuyoTextHelper):
    def __init__(
        self,
        bridge: Optional[
            Callable[[Union[kt.KatsuyoText, kt.NonKatsuyoText]], kt.KatsuyoText]
        ] = None,
    ) -> None:
        if bridge is None:

            def __default(
                pre: Union[kt.KatsuyoText, kt.NonKatsuyoText]
            ) -> kt.KatsuyoText:
                if issubclass(
                    type(pre),
                    (kt.NonKatsuyoText),
                ):
                    pre = cast(kt.NonKatsuyoText, pre)
                    # TODO 助詞のハンドリング
                    dat = kt.NonKatsuyoText("だっ")
                    return cast(kt.KatsuyoText, pre + dat + kt.Ta())

                pre = cast(kt.KatsuyoText, pre)
                raise ValueError(
                    f"Unsupported katsuyo_text in {type(self)}: {pre} "
                    f"type: {type(pre)} katsuyo: {type(pre.katsuyo)}"
                )

            bridge = __default

        super().__init__(bridge)

    def try_merge(self, pre: kt.KatsuyoText) -> Optional[kt.KatsuyoText]:
        if issubclass(type(pre.katsuyo), k.RenyoMixin):
            if type(pre.katsuyo) is k.GodanKatsuyo and (
                pre.katsuyo.shushi in ["ぐ", "ぬ", "ぶ", "む"]
            ):
                return cast(kt.KatsuyoText, pre + kt.Da())

            return cast(kt.KatsuyoText, pre + kt.Ta())

        return None
