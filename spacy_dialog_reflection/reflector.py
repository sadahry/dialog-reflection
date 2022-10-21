from typing import Optional
import abc
import spacy

from spacy_dialog_reflection.reflection_text_builder import ISpacyReflectionTextBuilder


class IReflector(abc.ABC):
    @abc.abstractmethod
    def reflect(self, message: str) -> Optional[str]:
        """
        generate a reflection message that captures the outline of the message.
        return None if message is not supported.
        **NEVER CATCH THE EXCEPTION YOU WON'T BE EXPECTED!**
        """
        raise NotImplementedError()


class SpacyReflector(IReflector):
    def __init__(
        self, nlp: spacy.Language, builder: ISpacyReflectionTextBuilder
    ) -> None:
        self.nlp = nlp
        self.builder = builder

    def reflect(self, message: str) -> Optional[str]:
        doc = self.nlp(message)
        return self.builder.build(doc)
