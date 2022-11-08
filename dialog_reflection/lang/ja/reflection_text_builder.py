from dialog_reflection.reflection_cancelled import (
    ReflectionCancelled,
)
from dialog_reflection.cancelled_reason import (
    NoValidSentence,
    NoValidToken,
    CancelledByToken,
)
from dialog_reflection.reflector import (
    ISpacyReflectionTextBuilder,
)
from dialog_reflection.lang.ja.cancelled_reason import (
    WhTokenNotSupported,
    DialectNotSupported,
)
from dialog_reflection.lang.ja.reflection_text_builder_option import (
    JaSpacyPlainTextBuilderOption,
)
import warnings
import spacy


class JaSpacyPlainReflectionTextBuilder(ISpacyReflectionTextBuilder):
    def __init__(
        self,
        op: JaSpacyPlainTextBuilderOption = JaSpacyPlainTextBuilderOption(),
    ) -> None:
        self.op = op

    def extract_tokens(
        self,
        doc: spacy.tokens.Doc,
    ) -> spacy.tokens.Span:
        root = self._extract_root_token(doc)
        tokens = self._extract_tokens_with_nearest_heads(root)
        assert len(tokens) > 0
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
                filter(lambda x: x.norm_ in self.op.forbidden_wh_norms, sent), None
            )
            if _wh_token:
                wh_token = _wh_token if wh_token is None else wh_token
                warnings.warn(f"sent has wh_word: {wh_token} in {sent}", UserWarning)
                continue
            # check pos_tag
            if sent.root.pos_ in self.op.allowed_root_pos_tags:
                return sent.root

        if wh_token:
            raise ReflectionCancelled(WhTokenNotSupported(doc, wh_token))

        raise ReflectionCancelled(
            reason=NoValidSentence(
                message=f"No Valid Sentenses In Doc: '{doc}' "
                f"ALLOWED_ROOT_POS_TAGS: ({self.op.allowed_root_pos_tags})",
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
        last_token_of_root_sent = root.sent[-1]
        return root.doc[head_token.i : last_token_of_root_sent.i + 1]

    def build_text(
        self,
        tokens: spacy.tokens.Span,
    ) -> str:
        _tokens = self._cut_suffix(tokens)
        return self._finalize(_tokens)

    def _cut_suffix(self, tokens: spacy.tokens.Span) -> spacy.tokens.Span:
        assert len(tokens) > 0

        for i in reversed(range(-1, len(tokens))):
            # 最後のtokenまでinvalidだった場合エラーを返す
            if i == -1:
                raise ReflectionCancelled(
                    reason=NoValidToken(
                        message=f"All Tokens Are Cut As invalid. tokens: {tokens} ",
                        tokens=tokens,
                    )
                )

            token = tokens[i]
            tag = token.tag_
            conjugation_type, _ = get_conjugation(token)

            # break -> VALID
            # continue -> invalid
            # raise -> CANCEL

            match tag:
                case ("感動詞-一般" | "感動詞-フィラー" | "連体詞" | "助詞-準体助詞" | "補助記号-読点"):
                    continue
                case ("補助記号-句点"):
                    if token.norm_ == "?":
                        raise ReflectionCancelled(
                            reason=CancelledByToken(tokens=tokens, token=token)
                        )
                    continue
                case "助動詞":
                    if conjugation_type in self.op.invalid_jodoushi_types:
                        continue
                    # 助動詞以外の活用型は用言としてVALIDに
                    if "助動詞" not in conjugation_type:
                        break
                    # VALID判定候補がない場合は無条件でVALIDに
                    if not self.op.valid_jodoushi_types:
                        break
                    if conjugation_type in self.op.valid_jodoushi_types:
                        break
                    if conjugation_type in self.op.dialect_jodoushi_types:
                        raise ReflectionCancelled(
                            reason=DialectNotSupported(tokens, token)
                        )
                    # 未登録はCANCEL
                    raise ReflectionCancelled(
                        reason=CancelledByToken(tokens=tokens, token=token)
                    )
                case "助詞-接続助詞":
                    if token.norm_ in self.op.invalid_setsuzokujoshi_norms:
                        continue
                    # VALID判定候補がない場合は無条件でVALIDに
                    if not self.op.valid_setsuzokujoshi_norms:
                        break
                    if token.norm_ in self.op.valid_setsuzokujoshi_norms:
                        break
                    if token.norm_ in self.op.dialect_setsuzokujoshi_norms:
                        raise ReflectionCancelled(
                            reason=DialectNotSupported(tokens, token)
                        )
                    # 未登録はCANCEL
                    raise ReflectionCancelled(
                        reason=CancelledByToken(tokens=tokens, token=token)
                    )
                case "助詞-終助詞":
                    if token.norm_ in self.op.invalid_shujoshi_norms:
                        continue
                    # VALID判定候補がない場合は無条件でVALIDに
                    if not self.op.valid_shujoshi_norms:
                        break
                    if token.norm_ in self.op.valid_shujoshi_norms:
                        break
                    if token.norm_ in self.op.dialect_shujoshi_norms:
                        raise ReflectionCancelled(
                            reason=DialectNotSupported(tokens, token)
                        )
                    # 未登録はCANCEL
                    raise ReflectionCancelled(
                        reason=CancelledByToken(tokens=tokens, token=token)
                    )
                case "助詞-副助詞":
                    if token.norm_ in self.op.invalid_fukujoshi_norms:
                        continue
                    # VALID判定候補がない場合は無条件でVALIDに
                    if not self.op.valid_fukujoshi_norms:
                        break
                    if token.norm_ in self.op.valid_fukujoshi_norms:
                        continue
                    # 未登録はCANCEL
                    raise ReflectionCancelled(
                        reason=CancelledByToken(tokens=tokens, token=token)
                    )
                case "助詞-係助詞":
                    if token.norm_ in self.op.invalid_keijoshi_norms:
                        continue
                    # VALID判定候補がない場合は無条件でVALIDに
                    if not self.op.valid_keijoshi_norms:
                        break
                    if token.norm_ in self.op.valid_keijoshi_norms:
                        continue
                    # 未登録はCANCEL
                    raise ReflectionCancelled(
                        reason=CancelledByToken(tokens=tokens, token=token)
                    )
                case "助詞-格助詞":
                    if token.norm_ in self.op.invalid_kakuoshi_norms:
                        continue
                    # VALID判定候補がない場合は無条件でVALIDに
                    if not self.op.valid_kakuoshi_norms:
                        break
                    if token.norm_ in self.op.valid_kakuoshi_norms:
                        continue
                    # 未登録はCANCEL
                    raise ReflectionCancelled(
                        reason=CancelledByToken(tokens=tokens, token=token)
                    )

            # その他はVALIDに
            break

        return tokens[: i + 1]

    def _finalize(self, tokens: spacy.tokens.Span) -> str:
        assert len(tokens) > 0

        last_token = tokens[-1]
        last_token_text = self._finalize_last_token(last_token)

        return tokens[:-1].text + last_token_text

    def _finalize_last_token(self, last_token: spacy.tokens.Token) -> str:
        tag = last_token.tag_
        is_taigen = self.op.taigen_suffix_pattern.match(tag) is not None

        last_text = last_token.text if is_taigen else last_token.lemma_
        suffix = (
            self.op.fn_suffix_taigen(last_token)
            if is_taigen
            else self.op.fn_suffix_yougen(last_token)
        )

        return last_text + suffix

    def build_instead_of_error(self, e: BaseException) -> str:
        if isinstance(e, ReflectionCancelled):
            match (reason := e.reason):
                case NoValidSentence():
                    if (doc := reason.doc) is None:
                        return self.op.fn_message_when_error(e)
                    sents = list(doc.sents)
                    if not sents:
                        return self.op.fn_message_when_error(e)
                    return self.op.fn_suffix_ambiguous(sents[-1])
                case NoValidToken():
                    return self.op.fn_suffix_ambiguous(reason.tokens)
                case CancelledByToken():
                    return self.op.fn_message_cancelled_by_token(reason.token)
                case WhTokenNotSupported():
                    return self.op.fn_message_when_wh_token(reason)
                case DialectNotSupported():
                    return self.op.fn_message_dialect_not_supported(reason)

        return self.op.fn_message_when_error(e)


def get_conjugation(token):
    # sudachiの形態素解析結果(part_of_speech)5つ目以降(活用タイプ、活用形)が格納される
    # 品詞によっては活用タイプ、活用形が存在しないため、ここでは配列の取得のみ行う
    # e.g. 動詞
    # > m.part_of_speech() # => ['動詞', '一般', '*', '*', '下一段-バ行', '連用形-一般']
    # ref. https://github.com/explosion/spaCy/blob/v3.4.1/spacy/lang/ja/__init__.py#L102
    # ref. https://github.com/WorksApplications/SudachiPy/blob/v0.5.4/README.md
    # > Returns the part of speech as a six-element tuple. Tuple elements are four POS levels, conjugation type and conjugation form.
    # ref. https://worksapplications.github.io/sudachi.rs/python/api/sudachipy.html#sudachipy.Morpheme.part_of_speech
    inflection = token.morph.get("Inflection")
    if not inflection:
        return None, None
    inflection = inflection[0].split(";")
    conjugation_type = inflection[0]
    conjugation_form = inflection[1]
    return conjugation_type, conjugation_form
