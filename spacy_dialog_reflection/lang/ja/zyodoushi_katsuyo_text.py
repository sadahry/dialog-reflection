from collections.abc import Callable
from typing import Optional
import spacy_dialog_reflection.lang.ja.katsuyo as k
import spacy_dialog_reflection.lang.ja.katsuyo_text as kt


class ZyodoushiKatsuyoText(kt.KatsuyoText):
    def __init__(self, zyodoushi: kt.KatsuyoText):
        self.zyodoushi = zyodoushi
        super().__init__(
            zyodoushi.gokan,
            zyodoushi.katsuyo,
        )


class Reru(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            kt.KatsuyoText(
                gokan="れ",
                katsuyo=k.SHIMO_ICHIDAN,
            )
        )

    def merge(self, pre: kt.KatsuyoText) -> kt.KatsuyoText:
        if issubclass(type(pre.katsuyo), k.SaGyoHenkakuKatsuyo):
            prefix = pre.gokan + pre.katsuyo.mizen_reru
            return kt.NoKatsuyoText(prefix) + self.zyodoushi

        prefix = pre.gokan + pre.katsuyo.mizen
        return kt.NoKatsuyoText(prefix) + self.zyodoushi


class Rareru(ZyodoushiKatsuyoText):
    def __init__(self):
        super().__init__(
            kt.KatsuyoText(
                gokan="られ",
                katsuyo=k.SHIMO_ICHIDAN,
            )
        )

    def merge(self, pre: kt.KatsuyoText) -> kt.KatsuyoText:
        if issubclass(type(pre.katsuyo), k.SaGyoHenkakuKatsuyo):
            prefix = pre.gokan + pre.katsuyo.mizen_rareru
            return kt.NoKatsuyoText(prefix) + self.zyodoushi

        prefix = pre.gokan + pre.katsuyo.mizen
        return kt.NoKatsuyoText(prefix) + self.zyodoushi


class Ukemi(Reru):
    def __init__(
        self,
        bridge_text_func: Optional[Callable[[kt.KatsuyoText], str]] = None,
    ) -> None:
        super().__init__()

        if bridge_text_func is None:

            def __default(pre: kt.KatsuyoText) -> str:
                if issubclass(
                    type(pre.katsuyo),
                    (k.KeiyoushiKatsuyo, k.KeiyoudoushiKatsuyo),
                ):
                    # デフォルトでは動詞「なる」でブリッジ
                    naru = kt.KatsuyoText(
                        gokan="な",
                        katsuyo=k.GODAN_RA_GYO,
                    )
                    return pre + naru + Reru()

                raise ValueError(f"Unsupported katsuyo_text in Ukemi: {pre}")

            bridge_text_func = __default

        self.bridge_text_func: Callable[[kt.KatsuyoText], str] = bridge_text_func

    def merge(self, pre: kt.KatsuyoText) -> kt.KatsuyoText:
        katsuyo_class = type(pre.katsuyo)
        if issubclass(katsuyo_class, k.DoushiKatsuyo):
            # サ行変格活用のみ特殊
            if issubclass(katsuyo_class, k.SaGyoHenkakuKatsuyo):
                # 用法的に「〜する」は「れる/られる」どちらでもよいため固定
                # 用法的に「〜ずる」は文語が多いため未然形「〜ぜ られる」を採用
                if pre.katsuyo.shushi == "する":
                    return pre + Reru()
                elif pre.katsuyo.shushi == "ずる":
                    return pre + Rareru()

            mizen_text = pre.gokan + pre.katsuyo.mizen
            if mizen_text[-1] in k.DAN["あ"]:
                return pre + Reru()
            else:
                return pre + Rareru()

        # 文法的な置き換えができない単語はbridge_text_funcで処理
        return self.bridge_text_func(pre)


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
