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
        self.wordEndingPast = "たんですね。"

    # VERB (5100; 63% instances), -NOUN (2328; 29% instances), -ADJ (529; 7% instances), -PROPN (62; 1% instances) in UD_Japanese-GSD
    # ref. https://universaldependencies.org/treebanks/ja_gsd/ja_gsd-dep-root.html
    ROOT_POS_SET = {"VERB", "NOUN", "PROPN", "ADJ"}

    def build(
        self,
        doc: spacy.tokens.Doc,
    ) -> Optional[str]:
        if doc.text.strip() == "":
            warnings.warn("empty message", UserWarning)
            return None
        sent = self._select_sentence(doc)
        if sent is None:
            warnings.warn("no valid sentenses", UserWarning)
            return None
        root = sent.root
        reflection_text = self._extract_text_with_nearest_root_deps(root)
        reflection_text_suffix = self._build_suffix(root)

        return reflection_text + reflection_text_suffix

    def _select_sentence(
        self,
        doc: spacy.tokens.Doc,
    ) -> Optional[spacy.tokens.Span]:
        # extract last sentence
        # ref. https://stackoverflow.com/a/2138894
        sent = None
        for sent in filter(
            lambda sent: sent.root.pos_ in self.ROOT_POS_SET,
            doc.sents,
        ):
            pass

        return sent

    def _extract_text_with_nearest_root_deps(
        self,
        root: spacy.tokens.Token,
    ) -> List[spacy.tokens.Token]:
        """Extract tokens with nearest root dependencies"""

        # process recursively
        def _extract_deps_texts(token, is_root=False):
            text = ""

            # extract deps_token with nearest token dependencies
            deps_token = None
            for deps_token in filter(
                lambda t: t.head.i == token.i,
                # the search is done from left in Japanese
                token.lefts,
            ):
                pass
            if deps_token is not None:
                text += _extract_deps_texts(deps_token)

            # Do not add root token
            # will be added in self._build_suffix()
            if not is_root:
                text += token.text
                for token in token.rights:
                    text += token.text

            return text

        # Dependency path from root
        return _extract_deps_texts(root, is_root=True)

    def _build_suffix(
        self,
        root: spacy.tokens.Token,
    ) -> str:
        """
        Build suffixes of reflection
        Reflection suffixes(=root in Japanese) should be placed carefully in Japanese
        """

        # There is no VBD tokens in Japanese
        # ref. https://universaldependencies.org/treebanks/ja_gsd/index.html#pos-tags
        # if root.pos_ == "VBD":

        if root.pos_ == "VERB":
            return root.lemma_ + self.wordEnding
        return ""
