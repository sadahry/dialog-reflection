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
        # TODO 動詞の実装
        # if pos_tag == "VERB":
        #     return KatsuyoText(gokan=src.lemma_, katsuyo=NO_KATSUYO)
        # elif pos_tag == "ADJ":
        if pos_tag == "ADJ":
            inflection = src.morph.get("Inflection")
            if "形容詞" in inflection:
                # e.g. 楽しい -> gokan=楽し + katsuyo=い
                return KatsuyoText(gokan=src.lemma_[-1], katsuyo=KEIYOUSHI)
            elif "形容動詞" in inflection:
                # universaldependenciesの形容動詞に語幹は含まれない
                # see: https://universaldependencies.org/treebanks/ja_gsd/ja_gsd-pos-ADJ.html
                # e.g. 健康 -> gokan=健康 + katsuyo=だ
                return KatsuyoText(gokan=src.lemma_, katsuyo=KEIYOUDOUSHI)
            else:
                warnings.warn(
                    f"Unsupported Inflection as ADJ: {inflection}", UserWarning
                )
                return None
        elif pos_tag == "NOUN":
            # 名詞は形容動詞的に扱う
            # e.g. 健康 -> gokan=健康 + katsuyo=だ
            return KatsuyoText(gokan=src.text, katsuyo=KEIYOUDOUSHI)
        elif pos_tag == "PROPN":
            # 固有名詞は形容動詞的に扱う
            # e.g. ジョニー -> gokan=ジョニー + katsuyo=だ
            return KatsuyoText(gokan=src.text, katsuyo=KEIYOUDOUSHI)
        else:
            warnings.warn(f"Unsupported POS Tag: {pos_tag}", UserWarning)
            return None
