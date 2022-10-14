from spacy_dialog_reflection.lang.ja.katsuyo_text import KatsuyoText
import abc
import spacy_dialog_reflection.lang.ja.katsuyo as k


class IKatsuyoTextAppender(abc.ABC):
    @abc.abstractmethod
    def append(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        """
        不適切な値が代入された際は、ValueErrorを発生させる。
        """
        raise NotImplementedError()

    def __str__(self):
        return self.__class__.__name__


class Ukemi(IKatsuyoTextAppender):
    def append(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        # TODO サ行変格活用の扱い
        mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen
        if mizen_text[-1] in k.DAN["あ"]:
            return KatsuyoText(gokan=mizen_text, katsuyo=k.RERU)
        else:
            return KatsuyoText(gokan=mizen_text, katsuyo=k.RARERU)
