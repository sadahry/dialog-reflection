from typing import Set
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
import re
import warnings
import spacy


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
        invalid_jodoushi_types: Set[str] = {
            "助動詞-ダ",
            "助動詞-デス",
            "助動詞-マス",
        },
        valid_jodoushi_types: Set[str] = {
            "助動詞-タ",
            "助動詞-タイ",
            "助動詞-ナイ",
            "助動詞-レル",
            "助動詞-ラシイ",
        },
        # 網羅はしない。あくまでWARNINGとして出すため
        dialect_jodoushi_types: Set[str] = {
            "助動詞-ジャ",
            "助動詞-ドス",
            "助動詞-ナンダ",
            "助動詞-ヘン",
            "助動詞-ヤ",
            "助動詞-ヤス",
        },
        invalid_setsuzokujoshi_norms: Set[str] = {
            "が",
            "し",
            "て",
            "で",
            "に",
            "から",
            "けど",
            "けれど",
        },
        valid_setsuzokujoshi_norms: Set[str] = {
            "と",
            "ど",
            "ば",
            "つつ",
            "ては",
            "とも",
            "とて",
            "なり",
            "たって",
            "ながら",
            "し",  # 終助詞的に扱われる用例が多いためVALIDに
            "というか",  # TODO ユーザー辞書での対応(spaCyモデルの再学習を含め)を実現する
        },
        dialect_setsuzokujoshi_norms={"きに", "けん", "すけ", "さかい", "ばってん"},
        invalid_shujoshi_norms={
            "い",
            "え",
            "さ",
            "ぜ",
            "ぞ",
            "や",
            "な",
            "ね",
            "よ",
            "わ",
            "もの",
            "よん",
            "じゃん",
        },
        valid_shujoshi_norms: Set[str] = {
            "とも",  # 接続助詞「とも」の代用
        },
        dialect_shujoshi_norms: Set[str] = {
            "で",
            "ど",
            "ラ",
            "かし",
            "ぞい",
            "たい",
            "ちょ",
            "てん",
            "ねん",
            "のう",
            "のん",
            "ばい",
            "ばや",
            "べい",
        },
        invalid_fukujoshi_norms: Set[str] = {
            "って",  # 終助詞的に扱われる用例が多いためVALIDに
        },
        valid_fukujoshi_norms: Set[str] = set(),
        invalid_keijoshi_norms: Set[str] = set(),
        valid_keijoshi_norms: Set[str] = set(),
        invalid_kakuoshi_norms: Set[str] = set(),
        valid_kakuoshi_norms: Set[str] = set(),
        taigen_suffix_regexp: str = ".*(名|代名|形状|助)詞",
    ) -> None:
        # TODO 柔軟に設定できるようにする
        self.suffix_taigen = "なんですね。"
        self.suffix_yougen = "んですね。"
        self.suffix_ambiguous = "、ですか。"
        self.message_when_error = "そうなんですね。"
        self.message_when_wh_token = "んー。"
        self.allowed_root_pos_tags = allowed_root_pos_tags
        self.forbidden_wh_norms = forbidden_wh_norms
        self.invalid_jodoushi_types = invalid_jodoushi_types
        self.valid_jodoushi_types = valid_jodoushi_types
        self.dialect_jodoushi_types = dialect_jodoushi_types
        self.invalid_setsuzokujoshi_norms = invalid_setsuzokujoshi_norms
        self.valid_setsuzokujoshi_norms = valid_setsuzokujoshi_norms
        self.dialect_setsuzokujoshi_norms = dialect_setsuzokujoshi_norms
        self.invalid_shujoshi_norms = invalid_shujoshi_norms
        self.valid_shujoshi_norms = valid_shujoshi_norms
        self.dialect_shujoshi_norms = dialect_shujoshi_norms
        self.valid_fukujoshi_norms = valid_fukujoshi_norms
        self.invalid_fukujoshi_norms = invalid_fukujoshi_norms
        self.invalid_keijoshi_norms = invalid_keijoshi_norms
        self.valid_keijoshi_norms = valid_keijoshi_norms
        self.invalid_kakuoshi_norms = invalid_kakuoshi_norms
        self.valid_kakuoshi_norms = valid_kakuoshi_norms
        self.taigen_suffix_pattern = re.compile(taigen_suffix_regexp)

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
        # TODO テスト強化
        return root.sent[head_token.i :]

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
                    if conjugation_type in self.invalid_jodoushi_types:
                        continue
                    # 助動詞以外の活用型は用言としてVALIDに
                    if "助動詞" not in conjugation_type:
                        break
                    # VALID判定候補がない場合は無条件でVALIDに
                    if not self.valid_jodoushi_types:
                        break
                    if conjugation_type in self.valid_jodoushi_types:
                        break
                    if conjugation_type in self.dialect_jodoushi_types:
                        raise ReflectionCancelled(
                            reason=DialectNotSupported(tokens, token)
                        )
                    # 未登録はCANCEL
                    raise ReflectionCancelled(
                        reason=CancelledByToken(tokens=tokens, token=token)
                    )
                case "助詞-接続助詞":
                    if token.norm_ in self.invalid_setsuzokujoshi_norms:
                        continue
                    # VALID判定候補がない場合は無条件でVALIDに
                    if not self.valid_setsuzokujoshi_norms:
                        break
                    if token.norm_ in self.valid_setsuzokujoshi_norms:
                        break
                    if token.norm_ in self.dialect_setsuzokujoshi_norms:
                        raise ReflectionCancelled(
                            reason=DialectNotSupported(tokens, token)
                        )
                    # 未登録はCANCEL
                    raise ReflectionCancelled(
                        reason=CancelledByToken(tokens=tokens, token=token)
                    )
                case "助詞-終助詞":
                    if token.norm_ in self.invalid_shujoshi_norms:
                        continue
                    # VALID判定候補がない場合は無条件でVALIDに
                    if not self.valid_shujoshi_norms:
                        break
                    if token.norm_ in self.valid_shujoshi_norms:
                        break
                    if token.norm_ in self.dialect_shujoshi_norms:
                        raise ReflectionCancelled(
                            reason=DialectNotSupported(tokens, token)
                        )
                    # 未登録はCANCEL
                    raise ReflectionCancelled(
                        reason=CancelledByToken(tokens=tokens, token=token)
                    )
                case "助詞-副助詞":
                    if token.norm_ in self.invalid_fukujoshi_norms:
                        continue
                    # VALID判定候補がない場合は無条件でVALIDに
                    if not self.valid_fukujoshi_norms:
                        break
                    if token.norm_ in self.valid_fukujoshi_norms:
                        continue
                    # 未登録はCANCEL
                    raise ReflectionCancelled(
                        reason=CancelledByToken(tokens=tokens, token=token)
                    )
                case "助詞-係助詞":
                    if token.norm_ in self.invalid_keijoshi_norms:
                        continue
                    # VALID判定候補がない場合は無条件でVALIDに
                    if not self.valid_keijoshi_norms:
                        break
                    if token.norm_ in self.valid_keijoshi_norms:
                        continue
                    # 未登録はCANCEL
                    raise ReflectionCancelled(
                        reason=CancelledByToken(tokens=tokens, token=token)
                    )
                case "助詞-格助詞":
                    if token.norm_ in self.invalid_kakuoshi_norms:
                        continue
                    # VALID判定候補がない場合は無条件でVALIDに
                    if not self.valid_kakuoshi_norms:
                        break
                    if token.norm_ in self.valid_kakuoshi_norms:
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

        tag = last_token.tag_
        is_taigen = self.taigen_suffix_pattern.match(tag) is not None

        last_text = last_token.text if is_taigen else last_token.lemma_
        suffix = self.suffix_taigen if is_taigen else self.suffix_yougen

        return tokens[:-1].text + last_text + suffix

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
