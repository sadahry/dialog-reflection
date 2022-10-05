from typing import List, Optional
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
    # VERB (5100; 63% instances), -NOUN (2328; 29% instances), -ADJ (529; 7% instances), -PROPN (62; 1% instances) in UD_Japanese-GSD
    # ref. https://universaldependencies.org/treebanks/ja_gsd/ja_gsd-dep-root.html
    ROOT_POS_SET = {"VERB", "NOUN", "PROPN", "ADJ"}

    def build(
        self,
        doc: spacy.tokens.Doc,
    ) -> Optional[str]:
        if doc.text.strip() == "":
            print("[WARNING] empty message")
            return None
        sent = self._select_sentence(doc)
        if sent is None:
            print("[WARNING] no valid sentenses")
            return None
        tokens = self._extract_tokens_with_nearest_root_deps(sent)

        return sent.text

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

    def _extract_tokens_with_nearest_root_deps(
        self,
        sent: spacy.tokens.Span,
    ) -> List[spacy.tokens.Token]:
        """Extract tokens with nearest root dependencies"""

        # process recursively
        def _extract_deps_tokens(token, is_root=True):
            tokens = []

            # extract deps_token with nearest token dependencies
            deps_token = None
            for deps_token in filter(
                lambda t: t.head.i == token.i,
                # the search is done from left in Japanese
                token.lefts,
            ):
                pass
            if deps_token is not None:
                tokens += _extract_deps_tokens(deps_token, is_root=False)

            # Do not add root token
            # Reflection suffixes(=root in Japanese) should be placed carefully
            if not is_root:
                tokens.append(token)
                tokens += token.rights

            return tokens

        # Dependency path from root
        return _extract_deps_tokens(sent.root)
