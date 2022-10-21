from typing import Any, Optional
import abc
import spacy
import warnings


class ReflectionTextError(ValueError):
    def __init__(
        self, *args: object, instant_reflection_text: Optional[str] = None
    ) -> None:
        self.instant_reflection_text = instant_reflection_text
        super().__init__(*args)


class IReflectionTextBuilder(abc.ABC):
    def safe_build(self, doc: Any) -> str:
        """
        check if the doc is valid for reflection and build reflection message.
        **NEVER THROW THE EXCEPTION TO CONTINUE THE DIALOG**
        """
        try:
            return self.build(doc)
        except BaseException as e:
            warnings.warn(
                f"Failed to build reflection text: {type(e)} {e}", UserWarning
            )
            return self.build_instead_of_error(e)

    @abc.abstractmethod
    def build(self, doc: Any) -> str:
        """
        build reflection message from valid doc.
        raise `ReflectionTextValidationError` if the doc is not valid.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def build_instead_of_error(self, e: BaseException) -> str:
        """
        build reflection message from the valid doc.
        **NEVER THROW THE EXCEPTION TO CONTINUE THE DIALOG**
        """
        raise NotImplementedError()


class ISpacyReflectionTextBuilder(IReflectionTextBuilder):
    def safe_build(self, doc: spacy.tokens.Doc) -> str:
        return super().safe_build(doc)

    @abc.abstractmethod
    def build(self, doc: spacy.tokens.Doc) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def build_instead_of_error(self, e: BaseException) -> str:
        raise NotImplementedError()
