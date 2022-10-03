from typing import Optional
import spacy


class Reflector:
    def __init__(self, nlp: spacy.Language):
        self.nlp = nlp
        self.builder = ReflectionBuilder()

    @classmethod
    def from_name(cls, name: str):
        return cls(spacy.load(name))

    def reflect(self, message: str) -> Optional[str]:
        doc = self.nlp(message)
        return self.builder.build(doc)


class ReflectionBuilder:
    ROOT_POS_SET = {"VERB", "NOUN", "PROPN", "ADJ"}

    def build(
        self,
        doc: spacy.tokens.Doc,
    ) -> Optional[str]:
        if doc.text.strip() == "":
            print("empty message")
            return None
        sent = self._select_sentence(doc)

        return sent.text

    def _select_sentence(
        self,
        doc: spacy.tokens.Doc,
    ) -> Optional[spacy.tokens.Span]:
        for sent in reversed(list(doc.sents)):
            if sent.root.pos_ in self.ROOT_POS_SET:
                return sent

        print("no valid sentenses")
        return None
