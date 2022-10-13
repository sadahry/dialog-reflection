from typing import Optional
from spacy_dialog_reflection.lang.ja.katsuyo import KEIYOUDOUSHI, KEIYOUSHI
from spacy_dialog_reflection.lang.ja.katsuyo_text import KatsuyoText
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


class SpacyKatsuyoTextDetector(IKatsuyoTextDetector):
    def detect(self, src: spacy.tokens.Token) -> Optional[KatsuyoText]:
        pos_tag = src.pos_
        if pos_tag == "VERB":
            # TODO 動詞の実装
            return NotImplementedError()
        elif pos_tag == "ADJ":
            # ==================================================
            # 形容動詞の判定
            # ==================================================
            tag = src.tag_
            # 「形状詞」=「形容動詞の語幹」
            if "形状詞" in tag:
                # universaldependenciesの形容動詞に語幹は含まれない
                # see: https://universaldependencies.org/treebanks/ja_gsd/ja_gsd-pos-ADJ.html
                # e.g. 健康 -> gokan=健康 + katsuyo=だ
                return KatsuyoText(gokan=src.lemma_, katsuyo=KEIYOUDOUSHI)
            # ==================================================
            # 形容詞の判定
            # ==================================================
            inflection = "".join(src.morph.get("Inflection"))
            if not inflection:
                warnings.warn("No Inflections in ADJ", UserWarning)
                return None
            if "形容詞" in inflection:
                # e.g. 楽しい -> gokan=楽し + katsuyo=い
                return KatsuyoText(gokan=src.lemma_[:-1], katsuyo=KEIYOUSHI)
            else:
                warnings.warn(
                    f"Unsupported Inflections of ADJ: {inflection}", UserWarning
                )
                return None
        elif pos_tag == "NOUN":
            # ==================================================
            # 名詞の変形
            # ==================================================
            # 名詞は形容動詞的に扱う
            # e.g. 健康 -> gokan=健康 + katsuyo=だ
            return KatsuyoText(gokan=src.text, katsuyo=KEIYOUDOUSHI)
        elif pos_tag == "PROPN":
            # ==================================================
            # 固有名詞の変形
            # ==================================================
            # 固有名詞は形容動詞的に扱う
            # e.g. ジョニー -> gokan=ジョニー + katsuyo=だ
            return KatsuyoText(gokan=src.text, katsuyo=KEIYOUDOUSHI)
        else:
            warnings.warn(f"Unsupported POS Tag: {pos_tag}", UserWarning)
            return None
