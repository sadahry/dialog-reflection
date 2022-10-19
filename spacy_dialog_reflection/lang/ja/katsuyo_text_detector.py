from typing import Any, Dict, Optional, List, Tuple
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
from spacy_dialog_reflection.lang.ja.katsuyo_text import KURU, KURU_KANJI, KatsuyoText

from spacy_dialog_reflection.lang.ja.katsuyo_text_helper import (
    Hitei,
    KibouSelf,
    Shieki,
    Ukemi,
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
    APPENDANTS = [
        Ukemi,
        Shieki,
        Hitei,
        KibouSelf,
    ]

    def __init__(self, appendants_dict: Dict[type, KatsuyoText]) -> None:
        self.appendants_dict = appendants_dict
        # check appendants_dict
        for appendant in self.APPENDANTS:
            if appendant not in self.appendants_dict:
                warnings.warn(f"appendants_dict doesn't have appendant: {appendant}")

    def try_append(self, type: type, appendants: List[KatsuyoText]) -> bool:
        if type not in self.appendants_dict:
            warnings.warn(
                f"couldn't append: {type} since appendants_dict doesn't have it"
            )
            return False
        appendants.append(self.appendants_dict[type])
        return True

    @abc.abstractmethod
    def detect(self, src: Any) -> Tuple[List[KatsuyoText], bool]:
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

    def detect(self, src: spacy.tokens.Span) -> Optional[KatsuyoText]:
        sent = src
        root = sent.root

        # spacy.tokens.Tokenから抽出される活用形の特徴を表す変数
        pos_tag = root.pos_
        tag = root.tag_
        lemma = root.lemma_
        # sudachiの形態素解析結果(part_of_speech)5つ目以降(活用タイプ、活用形)が格納される
        # 品詞によっては活用タイプ、活用形が存在しないため、ここでは配列の取得のみ行う
        # e.g. 動詞
        # > m.part_of_speech() # => ['動詞', '一般', '*', '*', '下一段-バ行', '連用形-一般']
        # ref. https://github.com/explosion/spaCy/blob/v3.4.1/spacy/lang/ja/__init__.py#L102
        # ref. https://github.com/WorksApplications/SudachiPy/blob/v0.5.4/README.md
        # > Returns the part of speech as a six-element tuple. Tuple elements are four POS levels, conjugation type and conjugation form.
        # ref. https://worksapplications.github.io/sudachi.rs/python/api/sudachipy.html#sudachipy.Morpheme.part_of_speech
        inflection = root.morph.get("Inflection")
        if len(inflection) > 0:
            inflection = inflection[0].split(";")

        # There is no VBD tokens in Japanese
        # ref. https://universaldependencies.org/treebanks/ja_gsd/index.html#pos-tags
        # if pos_tag == "VBD":

        # TODO 動詞の実装
        if pos_tag == "VERB":
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
            conjugation_type = inflection[0] if len(inflection) > 0 else None

            if conjugation_type is None:
                # 体言を含むサ変動詞の判定
                # 名詞がVERBとして現れるため、conjugation_typeが取得できない
                # # text = ウォーキングする
                # 1       ウォーキング    ウォーキング    VERB    名詞-普通名詞-一般      _       0       root    _       SpaceAfter=No|BunsetuBILabel=B|BunsetuPositionType=ROOT|Reading=ウォーキング
                # 2       する    する    AUX     動詞-非自立可能 _       1       aux     _       SpaceAfter=No|BunsetuBILabel=I|BunsetuPositionType=SYN_HEAD|Inf=サ行変格,終止形-一般|Reading=スル
                right = next(root.rights)
                if right.lemma_ == "する":
                    return KatsuyoText(gokan=lemma, katsuyo=SA_GYO_HENKAKU_SURU)
                # このパターンは存在しない
                # elif right.lemma_ == "ずる":
                #     return KatsuyoText(gokan=lemma, katsuyo=SA_GYO_HENKAKU_ZURU)
            else:
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
                        return KatsuyoText(
                            gokan=lemma[:-2], katsuyo=SA_GYO_HENKAKU_SURU
                        )
                    elif lemma[-2:] == "ずる":
                        return KatsuyoText(
                            gokan=lemma[:-2], katsuyo=SA_GYO_HENKAKU_ZURU
                        )

            warnings.warn(
                f"Unsupported conjugation_type of VERB: {conjugation_type}", UserWarning
            )
            return None
        elif pos_tag == "ADJ":
            # ==================================================
            # 形容動詞の判定
            # ==================================================
            # 「形状詞」=「形容動詞の語幹」
            if "形状詞" in tag:
                # universaldependenciesの形容動詞に語幹は含まれない
                # see: https://universaldependencies.org/treebanks/ja_gsd/ja_gsd-pos-ADJ.html
                # e.g. 健康 -> gokan=健康 + katsuyo=だ
                return KatsuyoText(gokan=root.lemma_, katsuyo=KEIYOUDOUSHI)
            # ==================================================
            # 形容詞の判定
            # ==================================================
            if "形容詞" in tag:
                # e.g. 楽しい -> gokan=楽し + katsuyo=い
                return KatsuyoText(gokan=root.lemma_[:-1], katsuyo=KEIYOUSHI)

            warnings.warn(f"Unsupported tag of ADJ: {tag}", UserWarning)
            return None
        elif pos_tag == "NOUN":
            # ==================================================
            # 名詞の変形
            # ==================================================
            # 名詞は形容動詞的に扱う
            # e.g. 健康 -> gokan=健康 + katsuyo=だ
            return KatsuyoText(gokan=root.text, katsuyo=KEIYOUDOUSHI)
        elif pos_tag == "PROPN":
            # ==================================================
            # 固有名詞の変形
            # ==================================================
            # 固有名詞は形容動詞的に扱う
            # e.g. ジョニー -> gokan=ジョニー + katsuyo=だ
            return KatsuyoText(gokan=root.text, katsuyo=KEIYOUDOUSHI)
        else:
            warnings.warn(f"Unsupported POS Tag: {pos_tag}", UserWarning)
            return None


class SpacyKatsuyoTextAppendantsDetector(IKatsuyoTextAppendantsDetector):
    def detect(self, src: spacy.tokens.Span) -> Tuple[List[KatsuyoText], bool]:
        sent = src
        # 現状はroot固定で処理
        root = sent.root

        appendants: List[KatsuyoText] = []
        has_error = False

        # NOTE: rootに紐づくトークンを取得するのに、依存関係を見ずにrootトークンのindex以降のトークンを見る
        #       これは、rootの意味に関連する助動詞がroot位置以降に連続することと、rootに紐づかない助動詞も意味に影響することを前提としている
        candidate_tokens = dropwhile(lambda t: t.i > root.i, sent)
        for candidate_token in candidate_tokens:
            pos_tag = candidate_token.pos_
            lemma = candidate_token.lemma_

            if pos_tag == "AUX":
                # ==================================================
                # 助動詞の判定
                # ==================================================
                if lemma in ["れる", "られる"]:
                    is_succeeded = self.try_append(Ukemi, appendants)
                    has_error = has_error or not is_succeeded
                    continue
                elif lemma in ["せる", "させる"]:
                    is_succeeded = self.try_append(Shieki, appendants)
                    has_error = has_error or not is_succeeded
                    continue
                elif lemma in ["ない", "ぬ"]:
                    # 「ぬ」も「ない」として扱う
                    is_succeeded = self.try_append(Hitei, appendants)
                    has_error = has_error or not is_succeeded
                    continue

                warnings.warn(f"Unsupported AUX: {lemma}", UserWarning)
                has_error = True
                continue
            elif pos_tag == "ADJ":
                # 「ない」のみ対応
                if lemma in ["ない", "無い"]:
                    is_succeeded = self.try_append(Hitei, appendants)
                    has_error = has_error or not is_succeeded
                    continue

        return appendants, has_error
