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
        assert message is not None or doc is not None

    def __str__(self):
        if self.message:
            return self.message
        return f"No Valid Sentence in doc: {self.doc}"


class NoValidToken(ICancelledReason):
    def __init__(
        self, message: Optional[str] = None, tokens: Optional[spacy.tokens.Span] = None
    ):
        self.tokens = tokens
        assert message is not None or tokens is not None

    def __str__(self):
        if self.message:
            return self.message
        return f"No Valid Token In Tokens. tokens: {self.tokens}"


class CancelledByToken(ICancelledReason):
    def __init__(
        self,
        message: Optional[str] = None,
        tokens: Optional[spacy.tokens.Span] = None,
        token: Optional[spacy.tokens.Token] = None,
    ):
        self.token = token
        self.tokens = tokens
        assert message is not None or token is not None

    def __str__(self):
        if self.message:
            return self.message
        message = f"Cancelled By Token. token: {self.token}"
        if self.tokens:
            message += f"in {self.tokens}"
        return message
