from typing import Optional
import spacy


class Reflector:
    def __init__(self, nlp: spacy.Language):
        self.nlp = nlp
        self.buidler = ReflectionBuilder()

    @classmethod
    def from_name(cls, name: str):
        return cls(spacy.load(name))

    def reflect(self, message: str) -> Optional[str]:
        doc = self.nlp(message)
        return self.buidler.build(doc)


class ReflectionBuilder:
    def build(self, doc: spacy.tokens.Doc) -> Optional[str]:
        if doc.text == "":
            return None
        sent = self._select_sentence(doc)

        return sent.text

    def _select_sentence(self, doc: spacy.tokens.Doc) -> spacy.tokens.Span:
        return next(doc.sents)
