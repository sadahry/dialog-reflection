from typing import Optional
import spacy

class Reflector:
    def __init__(self, nlp: spacy.Language):
        self.nlp = nlp

    @classmethod
    def from_name(cls, name: str):
        return cls(spacy.load(name))

    def reflect(self, message: str)-> Optional[str]:
        doc = self.nlp(message)
        return self.reflect_from_doc(doc)

    @classmethod
    def reflect_from_doc(self, doc: spacy.tokens.Doc)-> Optional[str]:
        if doc.text == "":
            return None
        sent = next(doc.sents)

        return sent.text
