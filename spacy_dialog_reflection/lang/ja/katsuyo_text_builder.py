from dataclasses import replace
from typing import Optional, List, Tuple
from spacy_dialog_reflection.lang.ja.katsuyo_text import KatsuyoText
from spacy_dialog_reflection.lang.ja.katsuyo_text_appender import (
    IKatsuyoTextAppender,
)
import abc
import warnings


class IKatsuyoTextBuilder(abc.ABC):
    @abc.abstractmethod
    def detect_appender(self, src: any) -> Tuple[List[IKatsuyoTextAppender], bool]:
        """
        不適切な値が代入された際は、has_error=Trueを返却する。
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def detect_root(self, src: any) -> Optional[KatsuyoText]:
        """
        不適切な値が代入された際は、Noneを返却する。
        """
        raise NotImplementedError()

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
        サポートされていないsrcを検知した際は、Noneとhas_error=Trueを返却する。
        予期されたエラーを検知した場合は、UserWarningを発生させてKatsuyoTextとhas_error=Trueを返却する。
        予期されないエラーを検知した場合は、そのままraiseされる。
        """
        has_error = False

        root = self.detect_root(src)
        if root is None:
            has_error = True
            return None, has_error

        appenders, is_error = self.detect_appender(src)
        has_error = has_error or is_error

        result, is_error = self.append_multiple(root, appenders)
        has_error = has_error or is_error

        return result, has_error

    def __str__(self):
        return self.__class__.__name__
