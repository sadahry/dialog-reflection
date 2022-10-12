from dataclasses import dataclass, replace
from typing import List
from spacy_dialog_reflection.lang.ja.katsuyo_text import KatsuyoText
import abc
import warnings
import spacy_dialog_reflection.lang.ja.katsuyo as k


@dataclass(frozen=True)
class ZyodohshiKatsuyo(k.Katsuyo):
    pass


# ref. https://ja.wikipedia.org/wiki助動詞_(国文法)
class IZyodohshiBuilder(abc.ABC):
    @abc.abstractmethod
    def build(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        raise NotImplementedError()

    def __str__(self):
        return self.__class__.__name__


# 受身
class Ukemi(IZyodohshiBuilder):
    RERU = ZyodohshiKatsuyo(
        mizen="れ",
        renyo="れ",
        shushi="れる",
        rentai="れる",
        katei="れれ",
        # 命令形「れよ」は省略
        meirei="れろ",
    )
    RARERU = ZyodohshiKatsuyo(
        mizen="られ",
        renyo="られ",
        shushi="られる",
        rentai="られる",
        katei="られれ",
        # 命令形「られよ」は省略
        meirei="られろ",
    )

    def build(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        return KatsuyoText(
            gokan=katsuyo_text.gokan + katsuyo_text.katsuyo.mizen,
            katsuyo=self.RARERU,
        )


def build_zyodohshi(
    src: KatsuyoText, zyodohshi_builders: List[IZyodohshiBuilder]
) -> KatsuyoText:
    # clone katsuyo_text
    result = replace(src)
    for zodohshi_builder in zyodohshi_builders:
        try:
            result = zodohshi_builder.build(result)
        except ValueError as e:
            warnings.warn(f"ValueError: {e}", UserWarning)
            warnings.warn(
                f"Invalid zodohshi_builder:{zodohshi_builder}. katsuyo_text: {result}",
                UserWarning,
            )
    return result
