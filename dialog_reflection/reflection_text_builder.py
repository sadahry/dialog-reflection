from typing import Any, Optional
import abc
import sys
import traceback
import warnings
import spacy


class ICancelledReason:
    pass


class NoValidSentence(ICancelledReason):
    def __init__(
        self, message: Optional[str] = None, doc: Optional[spacy.tokens.Doc] = None
    ):
        self.message = message
        self.doc = doc

    def __str__(self):
        if self.message:
            return self.message
        return f"No Valid Sentence in doc: {self.doc}"


class ReflectionCancelled(ValueError):
    def __init__(self, reason: ICancelledReason) -> None:
        self.reason = reason

    def __str__(self):
        return f"Reflection Cancelled. reason: {self.reason}"


class IReflectionTextBuilder(abc.ABC):
    def safe_build(self, doc: Any) -> str:
        """
        check if the doc is valid for reflection and build reflection message.
        **NEVER THROW THE EXCEPTION TO CONTINUE THE DIALOG**
        """
        try:
            return self.build(doc)
        except BaseException as e:
            type_, value, traceback_ = sys.exc_info()
            warnings.warn(
                "\n".join(traceback.format_exception(type_, value, traceback_)),
                UserWarning,
            )
            return self.build_instead_of_error(e)

    @abc.abstractmethod
    def build(self, doc: Any) -> str:
        """
        build reflection message from valid doc.
        raise `ReflectionCancelled` if the doc is not valid.
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

    def build(self, doc: spacy.tokens.Doc) -> str:
        if doc.text.strip() == "":
            raise ReflectionCancelled(reason=NoValidSentence(message="Empty Doc"))
        tokens = self.extract_tokens(doc)
        return self.build_text(tokens)

    @abc.abstractmethod
    def extract_tokens(self, doc: spacy.tokens.Doc) -> spacy.tokens.Span:
        raise NotImplementedError()

    @abc.abstractmethod
    def build_text(self, doc: spacy.tokens.Span) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def build_instead_of_error(self, e: BaseException) -> str:
        raise NotImplementedError()
