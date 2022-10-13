from dataclasses import replace
from typing import List, Tuple
from spacy_dialog_reflection.lang.ja.katsuyo_text import KatsuyoText
import abc
import warnings
import spacy_dialog_reflection.lang.ja.katsuyo as k


class IKatsuyoTextBuilder(abc.ABC):
    @abc.abstractmethod
    def build(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        """
        不適切な値が代入された際は、ValueErrorを発生させる。
        """
        raise NotImplementedError()

    def __str__(self):
        return self.__class__.__name__


def build_multiple(
    src: KatsuyoText, katsuyo_text_builders: List[IKatsuyoTextBuilder]
) -> Tuple[KatsuyoText, bool]:
    # clone KatsuyoText
    result = replace(src)
    has_error = False
    for katsuyo_text_builder in katsuyo_text_builders:
        try:
            result = katsuyo_text_builder.build(result)
        except ValueError as e:
            warnings.warn(f"ValueError: {e}", UserWarning)
            warnings.warn(
                f"Invalid katsuyo_text_builder:{katsuyo_text_builder}. katsuyo_text: {result}",
                UserWarning,
            )
            has_error = True
        except TypeError as e:
            # see: https://github.com/sadahry/spacy-dialog-reflection/issues/1
            if "NoneType" not in str(e):
                raise e
            warnings.warn(f"None value TypeError Detected: {e}", UserWarning)
            warnings.warn(
                f"Invalid katsuyo_text_builder:{katsuyo_text_builder}. katsuyo_text: {result}",
                UserWarning,
            )
            has_error = True
    return result, has_error


class Ukemi(IKatsuyoTextBuilder):
    def build(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        # TODO サ行変格活用の扱い
        mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen
        if mizen_text[-1] in k.DAN["あ"]:
            return KatsuyoText(gokan=mizen_text, katsuyo=k.RERU)
        else:
            return KatsuyoText(gokan=mizen_text, katsuyo=k.RARERU)
