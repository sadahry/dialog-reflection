from typing import Any, Optional, Tuple
import abc
import spacy


class IReflectionTextBuilder(abc.ABC):
    @abc.abstractmethod
    def check_valid(self, doc: Any) -> Tuple[bool, Optional[str]]:
        """
        check if the doc is valid for reflection.
        use `warnings.warn()` and return `False` if the doc is not valid.
        """
        raise NotImplementedError()

    def build(self, doc: Any) -> Optional[str]:
        """
        check if the doc is valid for reflection and build reflection message.
        """
        valid, _ = self.check_valid(doc)
        if not valid:
            return None

        return self.build_from_valid_doc(doc)

    @abc.abstractmethod
    def build_from_valid_doc(self, doc: Any) -> Optional[str]:
        """
        build reflection message from valid doc.
        """
        raise NotImplementedError()


class ISpacyReflectionTextBuilder(IReflectionTextBuilder):
    def build(self, doc: spacy.tokens.Doc) -> Optional[str]:
        return super().build(doc)

    @abc.abstractmethod
    def build_from_valid_doc(self, doc: spacy.tokens.Doc) -> Optional[str]:
        raise NotImplementedError()

    @abc.abstractmethod
    def check_valid(self, doc: spacy.tokens.Doc) -> Tuple[bool, Optional[str]]:
        raise NotImplementedError()
