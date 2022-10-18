from collections.abc import Callable
from typing import Optional
import abc
import spacy_dialog_reflection.lang.ja.katsuyo as k
import spacy_dialog_reflection.lang.ja.katsuyo_text as kt


class IKatsuyoTextAppender(abc.ABC):
    @abc.abstractmethod
    def append(self, katsuyo_text: kt.KatsuyoText) -> kt.KatsuyoText:
        """
        不適切な値が代入された際は、ValueErrorを発生させる。
        """
        raise NotImplementedError()

    def __str__(self):
        return self.__class__.__name__


# 受身,尊敬,自発,可能
class Ukemi(IKatsuyoTextAppender):
    def __init__(
        self,
        bridge_text_func: Optional[Callable[[kt.KatsuyoText], str]] = None,
    ) -> None:
        if bridge_text_func is None:

            # デフォルトでは動詞「なる」でブリッジ
            def __default(katsuyo_text: kt.KatsuyoText) -> str:
                bridge_text = "なら"

                katsuyo_class = type(katsuyo_text.katsuyo)
                if issubclass(katsuyo_class, k.KeiyoushiKatsuyo):
                    # 形容詞
                    renyo_text = katsuyo_text.gokan + katsuyo_text.katsuyo.renyo
                    return kt.KatsuyoText(
                        gokan=renyo_text + bridge_text + kt.RERU.gokan,
                        katsuyo=kt.RERU.katsuyo,
                    )
                elif issubclass(katsuyo_class, k.KeiyoudoushiKatsuyo):
                    # 形容動詞
                    renyo_text = katsuyo_text.gokan + katsuyo_text.katsuyo.renyo_naru
                    return kt.KatsuyoText(
                        gokan=renyo_text + bridge_text + kt.RERU.gokan,
                        katsuyo=kt.RERU.katsuyo,
                    )

                raise ValueError(f"Unsupported katsuyo_text in Ukemi: {katsuyo_text}")

            bridge_text_func = __default

        self.bridge_text_func: Callable[[kt.KatsuyoText], str] = bridge_text_func

    def append(self, katsuyo_text: kt.KatsuyoText) -> kt.KatsuyoText:
        katsuyo_class = type(katsuyo_text.katsuyo)
        if issubclass(katsuyo_class, k.DoushiKatsuyo):
            # サ行変格活用のみ特殊
            if issubclass(katsuyo_class, k.SaGyoHenkakuKatsuyo):
                # 用法的に「〜する」は「れる/られる」どちらでもよいため固定
                # 用法的に「〜ずる」は文語が多いため未然形「〜ぜ られる」を採用
                if katsuyo_text.katsuyo.shushi == "する":
                    mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen_reru
                    return kt.KatsuyoText(
                        gokan=mizen_text + kt.RERU.gokan,
                        katsuyo=kt.RERU.katsuyo,
                    )
                elif katsuyo_text.katsuyo.shushi == "ずる":
                    mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen_rareru
                    return kt.KatsuyoText(
                        gokan=mizen_text + kt.RARERU.gokan,
                        katsuyo=kt.RARERU.katsuyo,
                    )

            mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen
            if mizen_text[-1] in k.DAN["あ"]:
                return kt.KatsuyoText(
                    gokan=mizen_text + kt.RERU.gokan,
                    katsuyo=kt.RERU.katsuyo,
                )
            else:
                return kt.KatsuyoText(
                    gokan=mizen_text + kt.RARERU.gokan,
                    katsuyo=kt.RARERU.katsuyo,
                )

        # 文法的な置き換えができない単語はbridge_text_funcで処理
        return self.bridge_text_func(katsuyo_text)


# 使役
class Shieki(IKatsuyoTextAppender):
    def append(self, katsuyo_text: kt.KatsuyoText) -> kt.KatsuyoText:
        katsuyo_class = type(katsuyo_text.katsuyo)
        # サ行変格活用のみ特殊
        if issubclass(katsuyo_class, k.SaGyoHenkakuKatsuyo):
            # 用法的に「〜する」は「れる/られる」どちらでもよいため固定
            # 用法的に「〜ずる」は文語が多いため未然形「〜ぜ られる」を採用
            if katsuyo_text.katsuyo.shushi == "する":
                mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen_reru
                return kt.KatsuyoText(
                    gokan=mizen_text + kt.SERU.gokan,
                    katsuyo=kt.SERU.katsuyo,
                )
            elif katsuyo_text.katsuyo.shushi == "ずる":
                mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.renyo
                return kt.KatsuyoText(
                    gokan=mizen_text + kt.SASERU.gokan,
                    katsuyo=kt.SASERU.katsuyo,
                )

        mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen
        if mizen_text[-1] in k.DAN["あ"]:
            return kt.KatsuyoText(
                gokan=mizen_text + kt.SERU.gokan,
                katsuyo=kt.SERU.katsuyo,
            )
        else:
            return kt.KatsuyoText(
                gokan=mizen_text + kt.SASERU.gokan,
                katsuyo=kt.SASERU.katsuyo,
            )


# 否定
# NOTE: 現状は「仕方が無い」といった否定以外の文字列も取れてしまう。
#       意味を扱うユースケースが発生したら、別途方針を決める。
class Nai(IKatsuyoTextAppender):
    # 現状、出力文字列としては「ない」のみサポート
    # TODO オプションで「ぬ」を選択できるように

    def append(self, katsuyo_text: kt.KatsuyoText) -> kt.KatsuyoText:
        mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen
        return kt.KatsuyoText(
            gokan=mizen_text + kt.NAI.gokan,
            katsuyo=kt.NAI.katsuyo,
        )


# 自分の希望
class KibouSelf(IKatsuyoTextAppender):
    def append(self, katsuyo_text: kt.KatsuyoText) -> kt.KatsuyoText:
        if katsuyo_text.katsuyo.hinshi == k.KatsuyoHinshi.DOUSHI:
            renyo_text = katsuyo_text.gokan + katsuyo_text.katsuyo.renyo
            return kt.KatsuyoText(
                gokan=renyo_text + kt.TAI.gokan,
                katsuyo=kt.TAI.katsuyo,
            )
        # TODO 他のハンドリング
        return kt.KatsuyoText(
            gokan="",
            katsuyo=kt.TAI.katsuyo,
        )


# 他人の希望
class KibouOthers(IKatsuyoTextAppender):
    # 現状、出力文字列としては「ない」のみサポート
    # TODO オプションで「ぬ」を選択できるように

    def append(self, katsuyo_text: kt.KatsuyoText) -> kt.KatsuyoText:
        renyo_text = katsuyo_text.gokan + katsuyo_text.katsuyo.renyo
        return kt.KatsuyoText(
            gokan=renyo_text + kt.TAGARU.gokan,
            katsuyo=kt.TAGARU.katsuyo,
        )
