from dataclasses import replace
from typing import Any, Optional, List, Tuple
from spacy_dialog_reflection.lang.ja.katsuyo_text import KatsuyoText

from spacy_dialog_reflection.lang.ja.katsuyo_text_helper import (
    Hitei,
    Shieki,
    Ukemi,
    KibouSelf,
)
from spacy_dialog_reflection.lang.ja.katsuyo_text_detector import (
    IKatsuyoTextDetector,
    IKatsuyoTextAppendantsDetector,
    SpacyKatsuyoTextAppendantsDetector,
    SpacyKatsuyoTextDetector,
)
import abc
import warnings


class IKatsuyoTextBuilder(abc.ABC):
    def __init__(
        self,
        root_detector: IKatsuyoTextDetector,
        appendants_detector: IKatsuyoTextAppendantsDetector,
    ) -> None:
        self.root_detector = root_detector
        self.appendants_detector = appendants_detector

    def append_multiple(
        self, root: KatsuyoText, appendants: List[KatsuyoText]
    ) -> Tuple[KatsuyoText, bool]:
        # clone KatsuyoText
        result = replace(root)

        has_error = False
        for appendant in appendants:
            try:
                result += appendant
            except ValueError as e:
                warnings.warn(f"ValueError: {e}", UserWarning)
                warnings.warn(
                    f"Invalid appendant:{appendant}. katsuyo_text: {result}",
                    UserWarning,
                )
                has_error = True
            except TypeError as e:
                # see: https://github.com/sadahry/spacy-dialog-reflection/issues/1
                if "NoneType" not in str(e):
                    raise e
                warnings.warn(f"None value TypeError Detected: {e}", UserWarning)
                warnings.warn(
                    f"Invalid appendant:{appendant}. katsuyo_text: {result}",
                    UserWarning,
                )
                has_error = True

        return result, has_error

    def build(self, src: Any) -> Tuple[Optional[KatsuyoText], bool]:
        """
        サポートされていないrootを検知した際は、Noneとhas_error=Trueを返却する。
        予期されたエラーを検知した場合は、UserWarningを発生させてKatsuyoTextとhas_error=Trueを返却する。
        予期されないエラーを検知した場合は、そのままraiseされる。
        """
        has_error = False

        katsuyo_text = self.root_detector.detect(src)
        if katsuyo_text is None:
            has_error = True
            return None, has_error

        appendants, is_error = self.appendants_detector.detect(src)
        has_error = has_error or is_error

        result, is_error = self.append_multiple(katsuyo_text, appendants)
        has_error = has_error or is_error

        return result, has_error

    def __str__(self):
        return self.__class__.__name__


class SpacyKatsuyoTextBuilder(IKatsuyoTextBuilder):
    def __init__(self):
        super().__init__(
            root_detector=SpacyKatsuyoTextDetector(),
            appendants_detector=SpacyKatsuyoTextAppendantsDetector(
                # TODO もっと柔軟な設定ができるように
                {
                    Ukemi: Ukemi(),
                    Shieki: Shieki(),
                    Hitei: Hitei(),
                    KibouSelf: KibouSelf(),
                }
            ),
        )
