from spacy_dialog_reflection.lang.ja.katsuyo_text import NAI, KatsuyoText
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


# 受身,尊敬,自発,可能
class Ukemi(IKatsuyoTextAppender):
    def append(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        # TODO サ行変格活用の扱い
        mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen
        if mizen_text[-1] in k.DAN["あ"]:
            return KatsuyoText(gokan=mizen_text, katsuyo=k.RERU)
        else:
            return KatsuyoText(gokan=mizen_text, katsuyo=k.RARERU)


# 使役
class Shieki(IKatsuyoTextAppender):
    def append(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        # TODO サ行変格活用の扱い
        mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen
        if mizen_text[-1] in k.DAN["あ"]:
            return KatsuyoText(gokan=mizen_text, katsuyo=k.SERU)
        else:
            return KatsuyoText(gokan=mizen_text, katsuyo=k.SASERU)


# 否定
# NOTE: 現状は「仕方が無い」といった否定以外の文字列も取れてしまう。
#       意味を扱うユースケースが発生したら、別途方針を決める。
class Nai(IKatsuyoTextAppender):
    # 現状、出力文字列としては「ない」のみサポート
    # TODO オプションで「ぬ」を選択できるように

    def append(self, katsuyo_text: KatsuyoText) -> KatsuyoText:
        mizen_text = katsuyo_text.gokan + katsuyo_text.katsuyo.mizen
        return KatsuyoText(
            gokan=mizen_text + NAI.gokan,
            katsuyo=NAI.katsuyo,
        )
