from typing import Any, Optional, List, Set, Tuple, Type
from itertools import dropwhile
from spacy_dialog_reflection.lang.ja.katsuyo import (
    GODAN_BA_GYO,
    GODAN_GA_GYO,
    GODAN_IKU,
    GODAN_KA_GYO,
    GODAN_MA_GYO,
    GODAN_NA_GYO,
    GODAN_RA_GYO,
    GODAN_SA_GYO,
    GODAN_TA_GYO,
    GODAN_WAA_GYO,
    KAMI_ICHIDAN,
    KEIYOUDOUSHI,
    KEIYOUSHI,
    SA_GYO_HENKAKU_SURU,
    SA_GYO_HENKAKU_ZURU,
    SHIMO_ICHIDAN,
)
from spacy_dialog_reflection.lang.ja.katsuyo_text import (
    KURU,
    KURU_KANJI,
    IKatsuyoTextHelper,
    KatsuyoText,
    KatsuyoTextError,
)

from spacy_dialog_reflection.lang.ja.katsuyo_text_helper import (
    Denbun,
    Hitei,
    KakoKanryo,
    KibouSelf,
    Shieki,
    Suitei,
    Ukemi,
    KibouOthers,
    Youtai,
)
import abc
import warnings
import spacy


class IKatsuyoTextDetector(abc.ABC):
    @abc.abstractmethod
    def detect(self, src: Any) -> Optional[KatsuyoText]:
        """
        不適切な値が代入された際は、Noneを返却する。
        """
        raise NotImplementedError()

    def __str__(self):
        return self.__class__.__name__


class IKatsuyoTextAppendantsDetector(abc.ABC):
    SUPPORTED_HELPERS = (
        Ukemi,
        Shieki,
        Hitei,
        KibouSelf,
        KibouOthers,
        KakoKanryo,
        Youtai,
        Denbun,
        Suitei,
    )

    def __init__(self, helpers: Set[IKatsuyoTextHelper]) -> None:
        # validate helpers
        for helper in helpers:
            if not isinstance(helper, self.SUPPORTED_HELPERS):
                raise KatsuyoTextError(f"Unsupported appendant helper: {helper}")

        self.appendants_dict = {type(helper): helper for helper in helpers}

        # check appendants_dict
        for supported_helper in self.SUPPORTED_HELPERS:
            if not issubclass(supported_helper, tuple(self.appendants_dict.keys())):
                warnings.warn(f"this object doesn't have helper: {supported_helper}")

    def try_append(self, typ: type, appendants: List[IKatsuyoTextHelper]) -> bool:
        if typ not in self.appendants_dict:
            # TODO ignoreリストを追加してここからwarningを出さないようにする
            warnings.warn(f"Unsupported type in try_append: {typ}")
            return False
        appendants.append(self.appendants_dict[typ])
        return True

    @abc.abstractmethod
    def detect(self, sent: Any, src: Any) -> Tuple[List[IKatsuyoTextHelper], bool]:
        """
        不適切な値が代入された際は、Noneを返却する。
        """
        raise NotImplementedError()

    def __str__(self):
        return self.__class__.__name__


class SpacyKatsuyoTextDetector(IKatsuyoTextDetector):
    VERB_KATSUYOS_BY_CONJUGATION_TYPE = {
        "五段-カ行": GODAN_KA_GYO,
        "五段-ガ行": GODAN_GA_GYO,
        "五段-サ行": GODAN_SA_GYO,
        "五段-タ行": GODAN_TA_GYO,
        "五段-ナ行": GODAN_NA_GYO,
        "五段-バ行": GODAN_BA_GYO,
        "五段-マ行": GODAN_MA_GYO,
        "五段-ラ行": GODAN_RA_GYO,
        "五段-ワア行": GODAN_WAA_GYO,
        "上一段-ア行": KAMI_ICHIDAN,
        "上一段-カ行": KAMI_ICHIDAN,
        "上一段-ガ行": KAMI_ICHIDAN,
        "上一段-ザ行": KAMI_ICHIDAN,
        "上一段-タ行": KAMI_ICHIDAN,
        "上一段-ナ行": KAMI_ICHIDAN,
        "上一段-バ行": KAMI_ICHIDAN,
        "上一段-マ行": KAMI_ICHIDAN,
        "上一段-ラ行": KAMI_ICHIDAN,
        "下一段-ア行": SHIMO_ICHIDAN,
        "下一段-カ行": SHIMO_ICHIDAN,
        "下一段-ガ行": SHIMO_ICHIDAN,
        "下一段-サ行": SHIMO_ICHIDAN,
        "下一段-ザ行": SHIMO_ICHIDAN,
        "下一段-タ行": SHIMO_ICHIDAN,
        "下一段-ダ行": SHIMO_ICHIDAN,
        "下一段-ナ行": SHIMO_ICHIDAN,
        "下一段-ハ行": SHIMO_ICHIDAN,
        "下一段-バ行": SHIMO_ICHIDAN,
        "下一段-マ行": SHIMO_ICHIDAN,
        "下一段-ラ行": SHIMO_ICHIDAN,
    }

    def detect(self, src: spacy.tokens.Token) -> Optional[KatsuyoText]:
        # spacy.tokens.Tokenから抽出される活用形の特徴を表す変数
        tag = src.tag_
        lemma = src.lemma_
        # sudachiの形態素解析結果(part_of_speech)5つ目以降(活用タイプ、活用形)が格納される
        # 品詞によっては活用タイプ、活用形が存在しないため、ここでは配列の取得のみ行う
        # e.g. 動詞
        # > m.part_of_speech() # => ['動詞', '一般', '*', '*', '下一段-バ行', '連用形-一般']
        # ref. https://github.com/explosion/spaCy/blob/v3.4.1/spacy/lang/ja/__init__.py#L102
        # ref. https://github.com/WorksApplications/SudachiPy/blob/v0.5.4/README.md
        # > Returns the part of speech as a six-element tuple. Tuple elements are four POS levels, conjugation type and conjugation form.
        # ref. https://worksapplications.github.io/sudachi.rs/python/api/sudachipy.html#sudachipy.Morpheme.part_of_speech
        inflection = src.morph.get("Inflection")
        if len(inflection) > 0:
            inflection = inflection[0].split(";")

        # There is no VBD tokens in Japanese
        # ref. https://universaldependencies.org/treebanks/ja_gsd/index.html#pos-tags
        # if pos_tag == "VBD":

        if tag.startswith("動詞"):
            # ==================================================
            # 動詞の判定
            # ==================================================
            # 「いく」は特殊な変形
            if lemma in ["行く", "逝く", "往く", "征く"]:
                return KatsuyoText(gokan=lemma[:-1], katsuyo=GODAN_IKU)
            elif lemma in ["いく", "ゆく"]:
                # 「ゆく」も「いく」に含める（過去・完了「た」を「ゆった」「ゆいた」とはできないため）
                return KatsuyoText(gokan="い", katsuyo=GODAN_IKU)

            # 活用タイプを取得して判定に利用
            assert inflection, f"inflection is not empty: {src}"
            conjugation_type = inflection[0]

            # 活用形の判定
            katsuyo = self.VERB_KATSUYOS_BY_CONJUGATION_TYPE.get(conjugation_type)
            if katsuyo:
                return KatsuyoText(gokan=lemma[:-1], katsuyo=katsuyo)

            # 例外的な活用形の判定
            if conjugation_type == "カ行変格":
                # カ変「くる」「来る」を別途ハンドリング
                if lemma == "来る":
                    return KURU_KANJI
                elif lemma == "くる":
                    return KURU
            elif conjugation_type == "サ行変格":
                # サ変「する」「ずる」を別途ハンドリング
                if lemma[-2:] == "する":
                    return KatsuyoText(gokan=lemma[:-2], katsuyo=SA_GYO_HENKAKU_SURU)
                elif lemma[-2:] == "ずる":
                    return KatsuyoText(gokan=lemma[:-2], katsuyo=SA_GYO_HENKAKU_ZURU)

            warnings.warn(
                f"Unsupported conjugation_type of VERB: {conjugation_type}", UserWarning
            )
            return None
        elif tag.startswith("形容詞"):
            # ==================================================
            # 形容詞の変形
            # ==================================================
            # e.g. 楽しい -> gokan=楽し + katsuyo=い
            return KatsuyoText(gokan=src.lemma_[:-1], katsuyo=KEIYOUSHI)
        elif tag.startswith("形状詞"):
            # ==================================================
            # 形容動詞の変形
            # ==================================================
            # 「形状詞」=「形容動詞の語幹」
            # universaldependenciesの形容動詞に語幹は含まれない
            # see: https://universaldependencies.org/treebanks/ja_gsd/ja_gsd-pos-ADJ.html
            # e.g. 健康 -> gokan=健康 + katsuyo=だ
            return KatsuyoText(gokan=src.lemma_, katsuyo=KEIYOUDOUSHI)
        elif tag.startswith("名詞"):
            # ==================================================
            # 例外：サ変動詞の判定
            # ==================================================
            # 体言を含むサ変動詞の判定
            # 名詞がVERBとして現れるため、conjugation_typeが取得できない
            # # text = ウォーキングする
            # 1       ウォーキング    ウォーキング    VERB    名詞-普通名詞-一般      _       0       root    _       SpaceAfter=No|BunsetuBILabel=B|BunsetuPositionType=ROOT|Reading=ウォーキング
            # 2       する    する    AUX     動詞-非自立可能 _       1       aux     _       SpaceAfter=No|BunsetuBILabel=I|BunsetuPositionType=SYN_HEAD|Inf=サ行変格,終止形-一般|Reading=スル
            if src.pos_ == "VERB":
                right = next(src.rights)
                if right.lemma_ == "する":
                    return KatsuyoText(gokan=lemma, katsuyo=SA_GYO_HENKAKU_SURU)
                # このパターンは存在しない
                # elif right.lemma_ == "ずる":
                #     return KatsuyoText(gokan=lemma, katsuyo=SA_GYO_HENKAKU_ZURU)
            # ==================================================
            # 名詞/固有名詞の変形
            # ==================================================
            # 名詞は形容動詞的に扱う
            # e.g. 健康 -> gokan=健康 + katsuyo=だ
            return KatsuyoText(gokan=src.text, katsuyo=KEIYOUDOUSHI)
        else:
            warnings.warn(f"Unsupported Tag: {tag}", UserWarning)
            return None


class SpacyKatsuyoTextAppendantsDetector(IKatsuyoTextAppendantsDetector):
    def detect(
        self, sent: spacy.tokens.Span, src: spacy.tokens.Token
    ) -> Tuple[List[IKatsuyoTextHelper], bool]:
        assert src in sent

        appendants: List[IKatsuyoTextHelper] = []
        has_error = False

        # NOTE: srcに紐づくトークンを取得するのに、依存関係を見ずにsrcトークンのindex以降のトークンを見る
        #       これは、srcがrootとなるとは限らないことと、sentをあらかじめ必要な長さに分割していることを前提としている
        candidate_tokens = dropwhile(lambda t: t.i <= src.i, sent)
        for candidate_token in candidate_tokens:
            helper, warning_msg = self._detect_appendant(candidate_token)
            if warning_msg:
                has_error = True
                warnings.warn(f"{warning_msg} src: {src} sent: {sent}", UserWarning)
            if helper is None:
                continue
            is_succeeded = self.try_append(helper, appendants)
            has_error = has_error or not is_succeeded

        return appendants, has_error

    def _detect_appendant(
        self, candidate_token: spacy.tokens.Token
    ) -> Tuple[Optional[Type[IKatsuyoTextHelper]], Optional[str]]:
        pos_tag = candidate_token.pos_
        norm = candidate_token.norm_

        if pos_tag == "AUX":
            # ==================================================
            # 助動詞の判定
            # ==================================================
            # NOTE: inflectionの情報のみでは、助動詞の活用形を判定できない
            #       e.g. せる -> Inf=下一段-サ行,終止形-一般 となる

            # TODO 無視する助動詞のリスト化
            if norm in {
                "だ",
                "です",
                "ます",
                "ちゃう",
                "やがる",
                # 「する」の助動詞はSpacyKatsuyoTextDetectorで対処されるので
                # ここでは無視する
                "為る",
            }:
                return None, None

            if norm in ["れる", "られる"]:
                return Ukemi, None
            elif norm in ["せる", "させる"]:
                return Shieki, None
            elif norm in ["ない", "ず"]:
                # 「ず」も「ない」として扱う
                return Hitei, None
            elif norm in ["たい"]:
                return KibouSelf, None
            elif norm in ["たがる"]:
                return KibouOthers, None
            elif norm in ["た"]:
                return KakoKanryo, None
            elif norm in ["そう"]:
                return self._detect_appendant_sou(candidate_token)
            elif norm in ["らしい"]:
                return Suitei, None

            return None, f"Unsupported AUX: {norm}"
        elif pos_tag == "ADJ":
            # 「ない」のみ対応
            # NOTE: 必ずしも正確に否定表現を解析できるとは限らない
            #       @see: https://github.com/sadahry/spacy-dialog-reflection/blob/17507db530da24c11816374d6caa4766e4614f69/tests/lang/ja/test_katsuyo_text_detector.py#L676-L693
            if norm in ["無い"]:
                return Hitei, None
        elif pos_tag == "ADV":
            # 「ない」のみ対応
            if norm in ["そう"]:
                return self._detect_appendant_sou(candidate_token)

        return None, None

    def _detect_appendant_sou(
        self, candidate_token: spacy.tokens.Token
    ) -> Tuple[Optional[Type[IKatsuyoTextHelper]], Optional[str]]:
        # 「様態」「伝聞」の判別
        left = candidate_token.doc[candidate_token.i - 1]
        # 動詞判定
        if left.tag_.startswith("動詞"):
            # @ref: https://github.com/sadahry/spacy-dialog-reflection/blob/6a56bd3378daee41a30bc7bb50b8de6c063a8437/spacy_dialog_reflection/lang/ja/katsuyo_text_detector.py#L136-L144
            inflection = left.morph.get("Inflection")[0].split(";")
            katsuyo_type = inflection[1]
            if "連用形" in katsuyo_type:
                return Youtai, None
            elif "終止形" in katsuyo_type or "連体形" in katsuyo_type:
                return Denbun, None
        # 形容詞判定
        if "形容詞" in left.tag_:
            # @ref: https://github.com/sadahry/spacy-dialog-reflection/blob/6a56bd3378daee41a30bc7bb50b8de6c063a8437/spacy_dialog_reflection/lang/ja/katsuyo_text_detector.py#L136-L144
            inflection = left.morph.get("Inflection")[0].split(";")
            katsuyo_type = inflection[1]
            if "語幹" in katsuyo_type:
                return Youtai, None
            elif "終止形" in katsuyo_type or "連体形" in katsuyo_type:
                return Denbun, None
        # 形容動詞判定
        if left.pos_ == "AUX" and left.text == "だ":
            # 形容動詞の基本形(終止or連体)が取れていると判断する
            return Denbun, None
        elif "形状詞" in left.tag_:
            # e.g.,
            # 困難    ADJ     名詞-普通名詞-形状詞可能
            # 的      PART    接尾辞-形状詞的
            return Youtai, None
        elif left.pos_ == "ADJ" and left.tag_.startswith("名詞"):
            # 形状詞可能ではない形容動詞の語幹が取れていると判断する
            return Youtai, None

        return None, f"Unexpected {candidate_token.norm_} no matched"
