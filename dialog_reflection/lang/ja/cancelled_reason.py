from dialog_reflection.cancelled_reason import (
    ICancelledReason,
)
from katsuyo_text.katsuyo_text import KatsuyoTextError
import spacy


class WhTokenNotSupported(ICancelledReason):
    def __init__(self, doc: spacy.tokens.Doc, wh_token: spacy.tokens.Token):
        self.doc = doc
        self.wh_token = wh_token

    def __str__(self):
        return f"5W1H Token Not Supported. doc: {self.doc} wh_token: {self.wh_token}"


class DialectNotSupported(ICancelledReason):
    def __init__(self, tokens: spacy.tokens.Span, dialect_token: spacy.tokens.Token):
        self.tokens = tokens
        self.dialect_token = dialect_token

    def __str__(self):
        return f"Dialect Token Not Supported. tokens: {self.tokens} token: {self.dialect_token}"


class KeigoExclusionFailed(ICancelledReason):
    def __init__(self, e: KatsuyoTextError, tokens: spacy.tokens.Span):
        self.e = e
        self.tokens = tokens

    def __str__(self):
        return str(self.e)
