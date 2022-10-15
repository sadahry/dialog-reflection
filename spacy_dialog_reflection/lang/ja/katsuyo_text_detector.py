from typing import Dict, Optional, List, Tuple
from itertools import dropwhile
from spacy_dialog_reflection.lang.ja.katsuyo import KEIYOUDOUSHI, KEIYOUSHI
from spacy_dialog_reflection.lang.ja.katsuyo_text import KatsuyoText
from spacy_dialog_reflection.lang.ja.katsuyo_text_appender import (
    Hitei,
    IKatsuyoTextAppender,
    Shieki,
    Ukemi,
)
import abc
import warnings
import spacy


class IKatsuyoTextDetector(abc.ABC):
    @abc.abstractmethod
    def detect(self, src: any) -> Optional[KatsuyoText]:
        """
        不適切な値が代入された際は、Noneを返却する。
        """
        raise NotImplementedError()

    def __str__(self):
        return self.__class__.__name__


class IKatsuyoTextAppenderDetector(abc.ABC):
    APPENDERS = [
        Ukemi,
    ]

    def __init__(self, appender_dict: Dict[type, IKatsuyoTextAppender]) -> None:
        self.appender_dict = appender_dict
        # check appender_dict
        for appender in self.APPENDERS:
            if appender not in self.appender_dict:
                warnings.warn(f"appender_dict doesn't have appender: {appender}")

    def try_append(self, type: type, appenders: List[IKatsuyoTextAppender]) -> bool:
        if type not in self.appender_dict:
            warnings.warn(
                f"couldn't append: {type} since appender_dict doesn't have it"
            )
            return False
        appenders.append(self.appender_dict[type])
        return True

    @abc.abstractmethod
    def detect(self, src: any) -> Tuple[List[IKatsuyoTextAppender], bool]:
        """
        不適切な値が代入された際は、Noneを返却する。
        """
        raise NotImplementedError()

    def __str__(self):
        return self.__class__.__name__


class SpacyKatsuyoTextDetector(IKatsuyoTextDetector):
    def detect(self, src: spacy.tokens.Span) -> Optional[KatsuyoText]:
        sent = src
        root = sent.root

        # spacy.tokens.Tokenから抽出される活用形の特徴を表す変数
        pos_tag = root.pos_
        tag = root.tag_
        inflection = "".join(root.morph.get("Inflection"))

        # There is no VBD tokens in Japanese
        # ref. https://universaldependencies.org/treebanks/ja_gsd/index.html#pos-tags
        # if pos_tag == "VBD":

        # TODO 動詞の実装
        # if pos_tag == "VERB":
        #     return NotImplementedError()
        # elif pos_tag == "ADJ":
        if pos_tag == "ADJ":
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
            if not inflection:
                warnings.warn("No Inflections in ADJ", UserWarning)
                return None
            if "形容詞" in inflection:
                # e.g. 楽しい -> gokan=楽し + katsuyo=い
                return KatsuyoText(gokan=root.lemma_[:-1], katsuyo=KEIYOUSHI)

            warnings.warn(f"Unsupported Inflections of ADJ: {inflection}", UserWarning)
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


class SpacyKatsuyoTextAppenderDetector(IKatsuyoTextAppenderDetector):
    def detect(self, src: spacy.tokens.Span) -> Tuple[List[IKatsuyoTextAppender], bool]:
        sent = src
        # 現状はroot固定で処理
        root = sent.root

        appenders = []
        has_error = False

        # NOTE: rootに紐づくトークンを取得するのに、依存関係を見ずにrootトークンのindex以降のトークンを見る
        #       これは、rootの意味に関連する助動詞がroot位置以降に連続することと、rootに紐づかない助動詞も意味に影響することを前提としている
        candidate_tokens = dropwhile(lambda t: t.i > root.i, sent)
        for candidate_token in candidate_tokens:
            pos_tag = candidate_token.pos_
            norm = candidate_token.norm_

            if pos_tag == "AUX":
                # ==================================================
                # 助動詞の判定
                # ==================================================
                if norm in ["れる", "られる"]:
                    is_succeeded = self.try_append(Ukemi, appenders)
                    has_error = has_error or not is_succeeded
                    continue
                elif norm in ["せる", "させる"]:
                    is_succeeded = self.try_append(Shieki, appenders)
                    has_error = has_error or not is_succeeded
                    continue
                elif norm in ["ない", "ぬ"]:
                    is_succeeded = self.try_append(Hitei, appenders)
                    has_error = has_error or not is_succeeded
                    continue

                warnings.warn(f"Unsupported AUX: {norm}", UserWarning)
                has_error = True
                continue
            elif pos_tag == "ADJ":
                # 「ない」のみ対応
                if norm in ["ない", "無い"]:
                    is_succeeded = self.try_append(Hitei, appenders)
                    has_error = has_error or not is_succeeded
                    continue

        return appenders, has_error
