import abc
import spacy

from dialog_reflection.reflection_text_builder import ISpacyReflectionTextBuilder


class IReflector(abc.ABC):
    @abc.abstractmethod
    def reflect(self, message: str) -> str:
        """
        generate a reflection text that captures the outline of the message.
        **NEVER THROW THE EXCEPTION TO CONTINUE THE DIALOG**
        """
        raise NotImplementedError()


class SpacyReflector(IReflector):
    def __init__(
        self, nlp: spacy.Language, builder: ISpacyReflectionTextBuilder
    ) -> None:
        self.nlp = nlp
        self.builder = builder

    def reflect(self, message: str) -> str:
        doc = self.nlp(message)
        return self.builder.safe_build(doc)
