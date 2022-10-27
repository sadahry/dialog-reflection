from typing import Any, Optional, List, Tuple
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    IKatsuyoTextAppendant,
    IKatsuyoTextSource,
    KatsuyoTextError,
    KatsuyoTextHasError,
)
from spacy_dialog_reflection.lang.ja.katsuyo_text_helper import (
    Denbun,
    HikyoReizi,
    Hitei,
    KakoKanryo,
    Keizoku,
    Shieki,
    Suitei,
    Touzen,
    Ukemi,
    KibouSelf,
    KibouOthers,
    Youtai,
)
from spacy_dialog_reflection.lang.ja.katsuyo_text_detector import (
    IKatsuyoTextDetector,
    IKatsuyoTextAppendantsDetector,
    SpacyKatsuyoTextAppendantsDetector,
    SpacyKatsuyoTextDetector,
)
import abc
import attrs
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
        self, root: IKatsuyoTextSource, appendants: List[IKatsuyoTextAppendant]
    ) -> Tuple[IKatsuyoTextSource, KatsuyoTextHasError]:
        # clone KatsuyoText
        result: IKatsuyoTextSource = attrs.evolve(root)

        has_error = False
        for appendant in appendants:
            try:
                result += appendant
            except (KatsuyoTextError, AttributeError) as e:
                warnings.warn(f"Error in append_multiple: {type(e)} {e}", UserWarning)
                warnings.warn(
                    f"Skip invalid appendant:{type(appendant)} "
                    f"katsuyo_text:{type(result)} value: {result}",
                    UserWarning,
                )
                has_error = True

        return result, KatsuyoTextHasError(has_error)

    def build(
        self, sent: Any, src: Any
    ) -> Tuple[Optional[IKatsuyoTextSource], KatsuyoTextHasError]:
        """
        サポートされていないrootを検知した際は、Noneとhas_error=Trueを返却する。
        予期されたエラーを検知した場合は、UserWarningを発生させてKatsuyoTextとhas_error=Trueを返却する。
        予期されないエラーを検知した場合は、そのままraiseされる。
        """
        has_error = False

        katsuyo_text = self.root_detector.detect(src)
        if katsuyo_text is None:
            has_error = True
            return None, KatsuyoTextHasError(has_error)

        appendants, _has_error = self.appendants_detector.detect_from_sent(sent, src)
        has_error = has_error or _has_error

        result, _has_error = self.append_multiple(katsuyo_text, appendants)
        has_error = has_error or _has_error

        return result, KatsuyoTextHasError(has_error)

    def __str__(self):
        return self.__class__.__name__


class SpacyKatsuyoTextBuilder(IKatsuyoTextBuilder):
    def __init__(self):
        super().__init__(
            root_detector=SpacyKatsuyoTextDetector(),
            appendants_detector=SpacyKatsuyoTextAppendantsDetector(
                # TODO もっと柔軟な設定ができるように
                (
                    Ukemi(),
                    Shieki(),
                    Hitei(),
                    KibouSelf(),
                    KibouOthers(),
                    KakoKanryo(),
                    Youtai(),
                    Denbun(),
                    Suitei(),
                    Touzen(),
                    HikyoReizi(),
                    Keizoku(),
                ),
            ),
        )
