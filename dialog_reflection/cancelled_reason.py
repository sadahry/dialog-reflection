from typing import Optional
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
