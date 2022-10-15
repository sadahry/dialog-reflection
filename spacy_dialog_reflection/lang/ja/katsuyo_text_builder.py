from dataclasses import replace
from typing import Optional, List, Tuple
from spacy_dialog_reflection.lang.ja.katsuyo_text import KatsuyoText
from spacy_dialog_reflection.lang.ja.katsuyo_text_appender import (
    IKatsuyoTextAppender,
    Shieki,
    Ukemi,
    Nai,
)
from spacy_dialog_reflection.lang.ja.katsuyo_text_detector import (
    IKatsuyoTextDetector,
    IKatsuyoTextAppenderDetector,
    SpacyKatsuyoTextAppenderDetector,
    SpacyKatsuyoTextDetector,
)
import abc
import warnings


class IKatsuyoTextBuilder(abc.ABC):
    def __init__(
        self,
        root_detector: IKatsuyoTextDetector,
        appender_detector: IKatsuyoTextAppenderDetector,
    ) -> None:
        self.root_detector = root_detector
        self.appender_detector = appender_detector

    def append_multiple(
        self, root: KatsuyoText, appenders: List[IKatsuyoTextAppender]
    ) -> Tuple[KatsuyoText, bool]:
        # clone KatsuyoText
        result = replace(root)

        has_error = False
        for appender in appenders:
            try:
                result = appender.append(result)
            except ValueError as e:
                warnings.warn(f"ValueError: {e}", UserWarning)
                warnings.warn(
                    f"Invalid appender:{appender}. katsuyo_text: {result}",
                    UserWarning,
                )
                has_error = True
            except TypeError as e:
                # see: https://github.com/sadahry/spacy-dialog-reflection/issues/1
                if "NoneType" not in str(e):
                    raise e
                warnings.warn(f"None value TypeError Detected: {e}", UserWarning)
                warnings.warn(
                    f"Invalid appender:{appender}. katsuyo_text: {result}",
                    UserWarning,
                )
                has_error = True

        return result, has_error

    def build(self, src: any) -> Tuple[Optional[KatsuyoText], bool]:
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

        appenders, is_error = self.appender_detector.detect(src)
        has_error = has_error or is_error

        result, is_error = self.append_multiple(katsuyo_text, appenders)
        has_error = has_error or is_error

        return result, has_error

    def __str__(self):
        return self.__class__.__name__


class SpacyKatsuyoTextBuilder(IKatsuyoTextBuilder):
    def __init__(self):
        super().__init__(
            root_detector=SpacyKatsuyoTextDetector(),
            appender_detector=SpacyKatsuyoTextAppenderDetector(
                {
                    Ukemi: Ukemi(),
                    Shieki: Shieki(),
                    Nai: Nai(),
                }
            ),
        )
