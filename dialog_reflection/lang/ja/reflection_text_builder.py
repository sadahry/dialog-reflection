from typing import Set
from dialog_reflection.reflection_text_builder import (
    ReflectionCancelled,
    ICancelledReason,
    NoValidSentence,
)
from dialog_reflection.reflector import (
    ISpacyReflectionTextBuilder,
    SpacyReflector,
)
import warnings
import spacy

# TODO あとでちゃんと実装
from tests.lang.ja.test_builder import build
from tests.lang.ja.test_detector import cut_suffix_until_valid


class WhTokenNotSupported(ICancelledReason):
    def __init__(self, doc: spacy.tokens.Doc, wh_token: spacy.tokens.Token):
        self.doc = doc
        self.wh_token = wh_token

    def __str__(self):
        return f"5W1H Token Not Supported. doc: {self.doc} wh_token: {self.wh_token}"


class JaPlainReflectionTextBuilder(ISpacyReflectionTextBuilder):
    def __init__(
        self,
        # restrict root pos tags to facilitate handling of suffixes in Japanese
        # root: -VERB (29585; 52% instances), -NOUN (19528; 34% instances), -ADJ (3807; 7% instances), -PROPN (1508; 3% instances), -NUM (953; 2% instances), ...
        # https://universaldependencies.org/treebanks/ja_bccwj/ja_bccwj-dep-root.html
        allowed_root_pos_tags: Set[str] = {"VERB", "NOUN", "PROPN", "ADJ", "NUM"},
        forbidden_wh_norms: Set[str] = {
            "何",
            "何故",
            "誰",
            "いつ",
            "どこ",
            "どちら",
            "どう",
            "どの",
            "どれ",
            "どんな",
            "どっち",
            "幾ら",
            "幾つ",
            "?",
        },
    ) -> None:
        # TODO 柔軟に設定できるようにする
        self.suffix = "んですね。"
        self.suffix_ambiguous = "、ですか。"
        self.message_when_error = "そうなんですね。"
        self.message_when_wh_token = "んー。"
        self.allowed_root_pos_tags = allowed_root_pos_tags
        self.forbidden_wh_norms = forbidden_wh_norms

    def extract_tokens(
        self,
        doc: spacy.tokens.Doc,
    ) -> spacy.tokens.Span:
        root = self._extract_root_token(doc)
        tokens = self._extract_tokens_with_nearest_heads(root)
        return tokens

    def _extract_root_token(
        self,
        doc: spacy.tokens.Doc,
    ) -> spacy.tokens.Token:
        """
        extract the root token,
        e.g. "私は彼女を愛している。私は幸せだ。" -> "幸せ"
        """
        # search from the latest sent in Japanese
        sents = reversed(list(doc.sents))
        wh_token = None
        for sent in sents:
            # check wh_token
            _wh_token = next(
                filter(lambda x: x.norm_ in self.forbidden_wh_norms, sent), None
            )
            if _wh_token:
                wh_token = _wh_token if wh_token is None else wh_token
                warnings.warn(f"sent has wh_word: {wh_token} in {sent}", UserWarning)
                continue
            # check pos_tag
            if sent.root.pos_ in self.allowed_root_pos_tags:
                return sent.root

        if wh_token:
            raise ReflectionCancelled(WhTokenNotSupported(doc, wh_token))

        raise ReflectionCancelled(
            reason=NoValidSentence(
                message=f"No Valid Sentenses In Doc: '{doc}' "
                f"ALLOWED_ROOT_POS_TAGS: ({self.allowed_root_pos_tags})",
                doc=doc,
            )
        )

    def _extract_tokens_with_nearest_heads(
        self,
        root: spacy.tokens.Token,
    ) -> spacy.tokens.Span:
        """
        e.g. "愛し" from "私は彼女を愛している。" -> ["彼女", "を", "愛", "し", "て", "いる"]
        """

        # process recursively
        def _extract_head_token(token):
            # extract head_token with nearest token dependencies
            head_token = None
            for head_token in filter(
                lambda t: t.head.i == token.i,
                # the search is done from left in Japanese
                token.lefts,
            ):
                # NOTE: the head_token is not always the nearest token
                #       compound/nummod tokens will have combined nouns like "50メートル走"
                if head_token.dep_ in {"compound", "nummod"}:
                    break
                pass
            if head_token is not None:
                return _extract_head_token(head_token)

            return token

        head_token = _extract_head_token(root)
        return root.sent[head_token.i :]

    def build_text(
        self,
        tokens: spacy.tokens.Span,
    ) -> str:
        _tokens = cut_suffix_until_valid(tokens)
        # TODO tokenがないときの対処
        # if _tokens is None:
        #     return self.message_when_error
        return build(_tokens)

    def build_instead_of_error(self, e: BaseException) -> str:
        if isinstance(e, ReflectionCancelled):
            match e.reason:
                case NoValidSentence():
                    if e.reason.doc is None:
                        return self.message_when_error
                    sents = list(e.reason.doc.sents)
                    if not sents:
                        return self.message_when_error
                    return sents[-1].root.text + self.suffix_ambiguous
                case WhTokenNotSupported():
                    return self.message_when_wh_token  # 固定

        return self.message_when_error


class JaSpacyReflector(SpacyReflector):
    def __init__(
        self,
        model: str,  # need to be installed
        builder: JaPlainReflectionTextBuilder = JaPlainReflectionTextBuilder(),
    ) -> None:
        nlp = spacy.load(model)
        super().__init__(nlp, builder)
