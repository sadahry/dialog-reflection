from dialog_reflection.reflector import (
    SpacyReflector,
    ISpacyReflectionTextBuilder,
)
from dialog_reflection.lang.ja.reflection_text_builder import (
    JaSpacyPlainReflectionTextBuilder,
)
import spacy


class JaSpacyReflector(SpacyReflector):
    def __init__(
        self,
        model: str,  # need to be installed
        builder: ISpacyReflectionTextBuilder = JaSpacyPlainReflectionTextBuilder(),
    ) -> None:
        nlp = spacy.load(model)
        super().__init__(nlp, builder)
