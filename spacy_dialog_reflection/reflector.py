from typing import List, Optional
import warnings
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
    def __init__(self) -> None:
        self.wordEnding = "んですね。"

    # 語尾のハンドリングに影響するのでパターンを絞る
    # VERB (5100; 63% instances), -NOUN (2328; 29% instances), -ADJ (529; 7% instances), -PROPN (62; 1% instances) in UD_Japanese-GSD
    # ref. https://universaldependencies.org/treebanks/ja_gsd/ja_gsd-dep-root.html
    ALLOWED_ROOT_POSES = {"VERB", "NOUN", "PROPN", "ADJ"}

    def check_valid(
        self,
        doc: spacy.tokens.Doc,
    ) -> bool:
        """
        Check if the doc is valid for reflection
        """
        if doc.text.strip() == "":
            message = "empty message"
            warnings.warn(message, UserWarning)
            return False, message
        return True

    def build(
        self,
        doc: spacy.tokens.Doc,
    ) -> Optional[str]:
        valid, _ = self.check_valid(doc)
        if not valid:
            return None
        sent = self._select_sentence(doc)
        if sent is None:
            return None

        root = sent.root
        reflection_tokens = self._extract_tokens_with_nearest_root_heads(root)
        return self._build_text(reflection_tokens, root)

    def _select_sentence(
        self,
        doc: spacy.tokens.Doc,
    ) -> Optional[spacy.tokens.Span]:
        # extract last sentence
        # ref. https://stackoverflow.com/a/2138894
        sent = None
        for sent in filter(
            lambda sent: sent.root.pos_ in self.ALLOWED_ROOT_POSES,
            doc.sents,
        ):
            pass

        if sent is None:
            warnings.warn("no valid sentenses", UserWarning)
        return sent

    def _extract_tokens_with_nearest_root_heads(
        self,
        root: spacy.tokens.Span,
    ) -> List[spacy.tokens.Token]:
        """
        Extract tokens with nearest root dependencies
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
        return root.doc[head_token.i:root.i]

    def _build_text(
        self,
        tokens: List[spacy.tokens.Token],
        root: spacy.tokens.Token,
    ) -> str:
        """
        Build text of reflection
        """
        reflection_text = ""
        reflection_text += "".join(map(lambda t: t.text, tokens))
        reflection_text += self._build_suffix(root)
        return reflection_text

    def _build_suffix(
        self,
        root: spacy.tokens.Token,
    ) -> str:
        """
        Build suffix of reflection
        suffix(=root in Japanese) should be placed carefully in Japanese
        """

        # There is no VBD tokens in Japanese
        # ref. https://universaldependencies.org/treebanks/ja_gsd/index.html#pos-tags
        # if root.pos_ == "VBD":

        if root.pos_ == "VERB":
            return root.lemma_ + self.wordEnding
        return ""
