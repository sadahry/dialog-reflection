# ref. https://ja.wikipedia.org/wiki/助動詞_(国文法)
from dataclasses import replace
from typing import List
from spacy_dialog_reflection.lang.ja.katsuyo_text import KatsuyoText
import abc
import warnings
import spacy_dialog_reflection.lang.ja.katsuyo as k


class IZyodoushiBuilder(abc.ABC):
    @abc.abstractmethod
    def build(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        """
        不適切な値が代入された際は、ValueErrorを発生させる。
        """
        raise NotImplementedError()

    def __str__(self):
        return self.__class__.__name__


def build_zyodoushi(
    src: KatsuyoText, zyodoushi_builders: List[IZyodoushiBuilder]
) -> KatsuyoText:
    # clone katsuyo_text
    result = replace(src)
    for zodoushi_builder in zyodoushi_builders:
        try:
            result = zodoushi_builder.build(result)
        except ValueError as e:
            warnings.warn(f"ValueError: {e}", UserWarning)
            warnings.warn(
                f"Invalid zodoushi_builder:{zodoushi_builder}. katsuyo_text: {result}",
                UserWarning,
            )
    return result


# ==============================================================================
# 受身
# ==============================================================================

RERU = k.ZyodoushiKatsuyo(
    mizen="れ",
    renyo="れ",
    shushi="れる",
    rentai="れる",
    katei="れれ",
    # 命令形「れよ」は省略
    meirei="れろ",
)

RARERU = k.ZyodoushiKatsuyo(
    mizen="られ",
    renyo="られ",
    shushi="られる",
    rentai="られる",
    katei="られれ",
    # 命令形「られよ」は省略
    meirei="られろ",
)


class Ukemi(IZyodoushiBuilder):
    def build(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        return KatsuyoText(
            gokan=katsuyo_text.gokan + katsuyo_text.katsuyo.mizen,
            katsuyo=RARERU,
        )
