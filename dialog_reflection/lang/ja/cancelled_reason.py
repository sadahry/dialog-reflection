from dialog_reflection.cancelled_reason import (
    ICancelledReason,
)
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
