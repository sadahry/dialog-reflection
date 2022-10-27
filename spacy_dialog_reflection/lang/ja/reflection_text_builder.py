from itertools import takewhile
from typing import Callable, Set
from spacy_dialog_reflection.lang.ja.katsuyo import KeiyoudoushiKatsuyo
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    FukujoshiText,
    IKatsuyoTextSource,
    TaigenText,
)
from spacy_dialog_reflection.reflection_text_builder import (
    ReflectionTextError,
)
from spacy_dialog_reflection.reflector import ISpacyReflectionTextBuilder
from spacy_dialog_reflection.lang.ja.katsuyo_text_builder import (
    SpacyKatsuyoTextBuilder,
)
import re
import spacy


def finalize_build_suffix_default(katsuyo_text: IKatsuyoTextSource) -> str:
    if isinstance(katsuyo_text, (TaigenText, FukujoshiText)) or (
        type(katsuyo_text.katsuyo) is KeiyoudoushiKatsuyo
    ):
        return katsuyo_text.gokan + "なんですね。"

    return str(katsuyo_text) + "んですね。"


class JaSpacyReflectionTextBuilder(ISpacyReflectionTextBuilder):
    def __init__(
        self,
        # restrict root pos tags to facilitate handling of suffixes in Japanese
        # VERB (5100; 63% instances), -NOUN (2328; 29% instances), -ADJ (529; 7% instances), -PROPN (62; 1% instances) in UD_Japanese-GSD
        # ref. https://universaldependencies.org/treebanks/ja_gsd/ja_gsd-dep-root.html
        allowed_root_pos_tags: Set[str] = {"VERB", "NOUN", "PROPN", "ADJ"},
        # NOTE: Will not use pos tags when build text in Japanese
        #       extract source token with tag instead
        allowed_bottom_token_tags: Set[str] = {
            "動詞",  # VERB
            "名詞",  # NOUN & PROPN
            "形容詞",  # ADJ
            "形状詞",  # ADJ
        },
        finalize_build_suffix: Callable[
            [IKatsuyoTextSource], str
        ] = finalize_build_suffix_default,
    ) -> None:
        # TODO 柔軟に設定できるようにする
        self.word_ending = "んですね。"
        self.word_ending_unpersed = "、ですか。"
        self.message_when_not_valid_doc = "続けてください。"
        self.text_builder = SpacyKatsuyoTextBuilder()
        self.allowed_root_pos_tags = allowed_root_pos_tags
        self.allowed_tag_pattern = self._build_allowed_tag_pattern(
            allowed_bottom_token_tags
        )
        self.finalize_build_suffix = finalize_build_suffix

    def _build_allowed_tag_pattern(self, allowed_root_tags: Set[str]) -> re.Pattern:
        # e.g. /^動詞.*|^名詞.*|^形容詞.*|^形状詞.*/
        return re.compile(r"^" + r".*|^".join(allowed_root_tags) + r".*")

    def build(self, doc: spacy.tokens.Doc) -> str:
        if doc.text.strip() == "":
            raise ReflectionTextError("EMPTY DOC")
        root = self._extract_root_token(doc)
        reflection_tokens = self._extract_tokens_with_nearest_heads(root)
        return self._build_text(reflection_tokens)

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
        for sent in sents:
            if sent.root.pos_ in self.allowed_root_pos_tags:
                return sent.root

        raise ReflectionTextError(
            f"NO VALID SENTENSES IN DOC: '{doc}' "
            f"ALLOWED_ROOT_POS_TAGS: ({self.allowed_root_pos_tags})"
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
                pass
            if head_token is not None:
                return _extract_head_token(head_token)

            return token

        head_token = _extract_head_token(root)
        return root.doc[head_token.i :]

    def _build_text(
        self,
        tokens: spacy.tokens.Span,
    ) -> str:
        bottom_token = self._extract_bottom_token(tokens)
        prefix_tokens = takewhile(lambda t: t.i < bottom_token.i, tokens)

        reflection_text = ""
        reflection_text += "".join(map(lambda t: t.text, prefix_tokens))
        # build suffix in other method
        # suffix(=root in Japanese) should be placed carefully in Japanese
        reflection_text += self._build_suffix(bottom_token)
        return reflection_text

    def _extract_bottom_token(
        self,
        tokens: spacy.tokens.Span,
    ) -> spacy.tokens.Token:
        for token in reversed(tokens):
            if self.allowed_tag_pattern.match(token.tag_):
                return token

        raise ReflectionTextError(
            f"NO VALID TOKENS IN SPAN: '{tokens}' "
            f"ALLOWED_TAG_PATTERN: ({self.allowed_tag_pattern})"
        )

    def _build_suffix(
        self,
        bottom_token: spacy.tokens.Token,
    ) -> str:
        try:
            # use whole sent to build katsuyo_text
            sent = bottom_token.sent

            # supress `has_error` warning as `_`
            katsuyo_text, _ = self.text_builder.build(sent=sent, src=bottom_token)

            if katsuyo_text is None:
                raise Exception(
                    f"unsupported parse. bottom_token: {bottom_token} sent: {sent}",
                    UserWarning,
                )

            return self.finalize_build_suffix(katsuyo_text)
        except BaseException as e:
            # ReflectionTextErrorでwrapしてinstant_reflection_textを残す
            instant_reflection_text = str(sent.root) + self.word_ending_unpersed
            raise ReflectionTextError(
                e, instant_reflection_text=instant_reflection_text
            )

    def build_instead_of_error(self, e: BaseException) -> str:
        if isinstance(e, ReflectionTextError) and e.instant_reflection_text is not None:
            return e.instant_reflection_text
        return self.message_when_not_valid_doc
