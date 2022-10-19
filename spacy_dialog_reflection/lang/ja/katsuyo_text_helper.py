from collections.abc import Callable
from typing import Optional, Union
import spacy_dialog_reflection.lang.ja.katsuyo as k
import spacy_dialog_reflection.lang.ja.katsuyo_text as kt


# TODO このクラスは、KatsuyoTextBuilder的な名前のクラスに変更する
#      gokan等が必要なく、KatsuyoTextを返すだけのクラスにする
class Ukemi(kt.IKatsuyoTextHelper):
    def __init__(
        self,
        bridge_func: Optional[
            Callable[[Union[kt.KatsuyoText, kt.NonKatsuyoText]], kt.KatsuyoText]
        ] = None,
    ) -> None:
        if bridge_func is None:

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
                    return pre + "に" + naru + kt.Reru()

                if issubclass(
                    type(pre.katsuyo),
                    (k.KeiyoushiKatsuyo, k.KeiyoudoushiKatsuyo),
                ):
                    return pre + naru + kt.Reru()

                raise ValueError(f"Unsupported katsuyo_text in Ukemi: {pre}")

            bridge_func = __default

        super().__init__(bridge_func)

    def try_merge(self, pre: kt.KatsuyoText) -> Optional[kt.KatsuyoText]:
        katsuyo_class = type(pre.katsuyo)
        if issubclass(katsuyo_class, k.DoushiKatsuyo):
            # サ行変格活用のみ特殊
            if issubclass(katsuyo_class, k.SaGyoHenkakuKatsuyo):
                # 用法的に「〜する」は「れる/られる」どちらでもよいため固定
                # 用法的に「〜ずる」は文語が多いため未然形「〜ぜ られる」を採用
                if pre.katsuyo.shushi == "する":
                    return pre + kt.Reru()
                elif pre.katsuyo.shushi == "ずる":
                    return pre + kt.Rareru()

            mizen_text = pre.gokan + pre.katsuyo.mizen
            if mizen_text[-1] in k.DAN["あ"]:
                return pre + kt.Reru()
            else:
                return pre + kt.Rareru()

        return None


# TODO 修正
# # 使役
# class Shieki(IKatsuyoTextAppendants):
#     def append(self, katsuyo_text: kt.KatsuyoText) -> kt.KatsuyoText:
#         katsuyo_class = type(katsuyo_text.katsuyo)
#         # サ行変格活用のみ特殊
#         if issubclass(katsuyo_class, k.SaGyoHenkakuKatsuyo):
#             # 用法的に「〜する」は「れる/られる」どちらでもよいため固定
#             # 用法的に「〜ずる」は文語が多いため未然形「〜ぜ られる」を採用
#             if katsuyo_text.katsuyo.shushi == "する":
#                 mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen_reru
#                 return kt.KatsuyoText(
#                     gokan=mizen_text + kt.SERU.gokan,
#                     katsuyo=kt.SERU.katsuyo,
#                 )
#             elif katsuyo_text.katsuyo.shushi == "ずる":
#                 mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.renyo
#                 return kt.KatsuyoText(
#                     gokan=mizen_text + kt.SASERU.gokan,
#                     katsuyo=kt.SASERU.katsuyo,
#                 )

#         mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen
#         if mizen_text[-1] in k.DAN["あ"]:
#             return kt.KatsuyoText(
#                 gokan=mizen_text + kt.SERU.gokan,
#                 katsuyo=kt.SERU.katsuyo,
#             )
#         else:
#             return kt.KatsuyoText(
#                 gokan=mizen_text + kt.SASERU.gokan,
#                 katsuyo=kt.SASERU.katsuyo,
#             )


# # 否定
# # NOTE: 現状は「仕方が無い」といった否定以外の文字列も取れてしまう。
# #       意味を扱うユースケースが発生したら、別途方針を決める。
# class Nai(IKatsuyoTextAppendants):
#     # 現状、出力文字列としては「ない」のみサポート
#     # TODO オプションで「ぬ」を選択できるように

#     def append(self, katsuyo_text: kt.KatsuyoText) -> kt.KatsuyoText:
#         mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen
#         return kt.KatsuyoText(
#             gokan=mizen_text + kt.NAI.gokan,
#             katsuyo=kt.NAI.katsuyo,
#         )


# # 自分の希望
# class KibouSelf(IKatsuyoTextAppendants):
#     def append(self, katsuyo_text: kt.KatsuyoText) -> kt.KatsuyoText:
#         if katsuyo_text.katsuyo.hinshi == k.KatsuyoHinshi.DOUSHI:
#             renyo_text = katsuyo_text.gokan + katsuyo_text.katsuyo.renyo
#             return kt.KatsuyoText(
#                 gokan=renyo_text + kt.TAI.gokan,
#                 katsuyo=kt.TAI.katsuyo,
#             )
#         # TODO 他のハンドリング
#         return kt.KatsuyoText(
#             gokan="",
#             katsuyo=kt.TAI.katsuyo,
#         )


# # 他人の希望
# class KibouOthers(IKatsuyoTextAppendants):
#     # 現状、出力文字列としては「ない」のみサポート
#     # TODO オプションで「ぬ」を選択できるように

#     def append(self, katsuyo_text: kt.KatsuyoText) -> kt.KatsuyoText:
#         renyo_text = katsuyo_text.gokan + katsuyo_text.katsuyo.renyo
#         return kt.KatsuyoText(
#             gokan=renyo_text + kt.TAGARU.gokan,
#             katsuyo=kt.TAGARU.katsuyo,
#         )
