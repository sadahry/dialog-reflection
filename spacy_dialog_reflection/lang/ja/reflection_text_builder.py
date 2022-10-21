from spacy_dialog_reflection.reflection_text_builder import (
    ReflectionTextError,
)
from spacy_dialog_reflection.reflector import ISpacyReflectionTextBuilder
from spacy_dialog_reflection.lang.ja.katsuyo_text_builder import (
    SpacyKatsuyoTextBuilder,
)
import spacy


class JaSpacyReflectionTextBuilder(ISpacyReflectionTextBuilder):
    def __init__(self) -> None:
        # TODO 柔軟に設定できるようにする
        self.word_ending = "んですね。"
        self.word_ending_unpersed = "、ですか。"
        self.message_when_not_valid_doc = "続けてください。"
        self.text_builder = SpacyKatsuyoTextBuilder()

    # restrict root pos tags to facilitate handling of suffixes in Japanese
    # VERB (5100; 63% instances), -NOUN (2328; 29% instances), -ADJ (529; 7% instances), -PROPN (62; 1% instances) in UD_Japanese-GSD
    # ref. https://universaldependencies.org/treebanks/ja_gsd/ja_gsd-dep-root.html
    ALLOWED_ROOT_POS_TAGS = {"VERB", "NOUN", "PROPN", "ADJ"}

    def build(self, doc: spacy.tokens.Doc) -> str:
        if doc.text.strip() == "":
            raise ReflectionTextError("EMPTY DOC")
        sent = self._select_sentence(doc)

        root = sent.root
        reflection_tokens = self._extract_tokens_with_nearest_root_heads(root)
        return self._build_text(reflection_tokens, root)

    def _select_sentence(
        self,
        doc: spacy.tokens.Doc,
    ) -> spacy.tokens.Span:
        """
        e.g. "私は彼女を愛している。私は幸せだ。" -> "私は幸せだ。"
        """
        # ref. https://stackoverflow.com/a/2138894
        sent = None
        for sent in filter(
            lambda sent: sent.root.pos_ in self.ALLOWED_ROOT_POS_TAGS,
            doc.sents,
        ):
            pass

        if sent is None:
            raise ReflectionTextError(
                f"NO VALID SENTENSES IN DOC: '{doc}' "
                f"ALLOWED_ROOT_POS_TAGS: {self.ALLOWED_ROOT_POS_TAGS}"
            )

        return sent

    def _extract_tokens_with_nearest_root_heads(
        self,
        root: spacy.tokens.Token,
    ) -> spacy.tokens.Span:
        """
        e.g. "私は彼女を愛している。" -> ["私", "は", "彼女", "を"]
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
                pass
            if head_token is not None:
                return _extract_head_token(head_token)

            return token

        head_token = _extract_head_token(root)
        return root.doc[head_token.i : root.i]

    def _build_text(
        self,
        tokens: spacy.tokens.Span,
        root: spacy.tokens.Token,
    ) -> str:
        reflection_text = ""
        reflection_text += "".join(map(lambda t: t.text, tokens))
        # build suffix in other method
        # suffix(=root in Japanese) should be placed carefully in Japanese
        reflection_text += self._build_suffix(root)
        return reflection_text

    def _build_suffix(
        self,
        root: spacy.tokens.Token,
    ) -> str:
        try:
            # use whole sent to build katsuyo_text
            sent = root.sent

            # supress `has_error` warning as `_`
            katsuyo_text, _ = self.text_builder.build(sent=sent, src=root)

            if katsuyo_text is None:
                raise Exception(
                    f"unsupported parse. root: {root} sent: {sent}", UserWarning
                )

            return str(katsuyo_text) + self.word_ending
        except BaseException as e:
            # ReflectionTextErrorでwrapしてinstant_reflection_textを残す
            instant_reflection_text = str(root) + self.word_ending_unpersed
            raise ReflectionTextError(
                e, instant_reflection_text=instant_reflection_text
            )

    def build_instead_of_error(self, e: BaseException) -> str:
        if type(e) is ReflectionTextError and e.instant_reflection_text is not None:
            return e.instant_reflection_text
        return self.message_when_not_valid_doc