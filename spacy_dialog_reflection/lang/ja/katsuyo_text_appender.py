from collections.abc import Callable
from typing import Optional
from spacy_dialog_reflection.lang.ja.katsuyo_text import NAI, TAGARU, TAI, KatsuyoText
import abc
import spacy_dialog_reflection.lang.ja.katsuyo as k


class IKatsuyoTextAppender(abc.ABC):
    @abc.abstractmethod
    def append(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
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
        bridge_text_func: Optional[Callable[[KatsuyoText], str]] = None,
    ) -> None:
        if bridge_text_func is None:
            # デフォルトでは動詞「なる」でブリッジ
            def __nara(_):
                return "なら"

            bridge_text_func = __nara

        self.bridge_text_func: Callable[[KatsuyoText], str] = bridge_text_func

    def append(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        katsuyo_class = type(katsuyo_text.katsuyo)
        if issubclass(katsuyo_class, k.DoushiKatsuyo):
            # サ行変格活用のみ特殊
            if issubclass(katsuyo_class, k.SaGyoHenkakuKatsuyo):
                # 用法的に「〜する」は「れる/られる」どちらでもよいため固定
                # 用法的に「〜ずる」は文語が多いため未然形「〜ぜ られる」を採用
                if katsuyo_text.katsuyo.shushi == "する":
                    return KatsuyoText(
                        gokan=katsuyo_text.gokan + katsuyo_text.katsuyo.mizen_reru,
                        katsuyo=k.RERU,
                    )
                elif katsuyo_text.katsuyo.shushi == "ずる":
                    return KatsuyoText(
                        gokan=katsuyo_text.gokan + katsuyo_text.katsuyo.mizen_rareru,
                        katsuyo=k.RARERU,
                    )

            mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen
            if mizen_text[-1] in k.DAN["あ"]:
                return KatsuyoText(gokan=mizen_text, katsuyo=k.RERU)
            else:
                return KatsuyoText(gokan=mizen_text, katsuyo=k.RARERU)
        elif issubclass(katsuyo_class, k.KeiyoushiKatsuyo):
            renyo_text = katsuyo_text.gokan + katsuyo_text.katsuyo.renyo
            bridge_text = self.bridge_text_func(katsuyo_text)
            return KatsuyoText(
                gokan=renyo_text + bridge_text,
                katsuyo=k.RERU,
            )
        elif issubclass(katsuyo_class, k.KeiyoudoushiKatsuyo):
            renyo_text = katsuyo_text.gokan + katsuyo_text.katsuyo.renyo_naru
            bridge_text = self.bridge_text_func(katsuyo_text)
            return KatsuyoText(
                gokan=renyo_text + bridge_text,
                katsuyo=k.RERU,
            )

        raise ValueError(f"Unsupported katsuyo_text in Ukemi: {katsuyo_text}")


# 使役
class Shieki(IKatsuyoTextAppender):
    def append(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        # サ行変格活用のみ特殊
        if type(katsuyo_text.katsuyo) is k.SaGyoHenkakuKatsuyo:
            # 用法的に「〜する」は「さ せる」となるため固定
            # 用法的に「〜ずる」は連用形「~じ させる」を採用
            if katsuyo_text.katsuyo.shushi == "する":
                return KatsuyoText(
                    gokan=katsuyo_text.gokan + katsuyo_text.katsuyo.mizen_reru,
                    katsuyo=k.SERU,
                )
            elif katsuyo_text.katsuyo.shushi == "ずる":
                return KatsuyoText(
                    gokan=katsuyo_text.gokan + katsuyo_text.katsuyo.renyo,
                    katsuyo=k.SASERU,
                )

        mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen
        if mizen_text[-1] in k.DAN["あ"]:
            return KatsuyoText(gokan=mizen_text, katsuyo=k.SERU)
        else:
            return KatsuyoText(gokan=mizen_text, katsuyo=k.SASERU)


# 否定
# NOTE: 現状は「仕方が無い」といった否定以外の文字列も取れてしまう。
#       意味を扱うユースケースが発生したら、別途方針を決める。
class Nai(IKatsuyoTextAppender):
    # 現状、出力文字列としては「ない」のみサポート
    # TODO オプションで「ぬ」を選択できるように

    def append(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen
        return KatsuyoText(
            gokan=mizen_text + NAI.gokan,
            katsuyo=NAI.katsuyo,
        )


# 自分の希望
class KibouSelf(IKatsuyoTextAppender):
    def append(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        if katsuyo_text.katsuyo.hinshi == k.KatsuyoHinshi.DOUSHI:
            renyo_text = katsuyo_text.gokan + katsuyo_text.katsuyo.renyo
            return KatsuyoText(
                gokan=renyo_text + TAI.gokan,
                katsuyo=TAI.katsuyo,
            )
        # TODO 他のハンドリング
        return KatsuyoText(
            gokan="",
            katsuyo=TAI.katsuyo,
        )


# 他人の希望
class KibouOthers(IKatsuyoTextAppender):
    # 現状、出力文字列としては「ない」のみサポート
    # TODO オプションで「ぬ」を選択できるように

    def append(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        renyo_text = katsuyo_text.gokan + katsuyo_text.katsuyo.renyo
        return KatsuyoText(
            gokan=renyo_text + TAGARU.gokan,
            katsuyo=TAGARU.katsuyo,
        )
