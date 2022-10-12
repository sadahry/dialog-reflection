from dataclasses import dataclass
import spacy_dialog_reflection.lang.ja.katsuyo as k


@dataclass(frozen=True)
class KatsuyoText:
    """
    活用形を含む動詞,形容詞,形容動詞,副詞の表現を表すクラス
    """

    gokan: str
    """
    文字列のうち活用されない部分。
    接続される品詞の情報を含むことがある。
    e.g. こられるそうだ -> gokan=こられる
    """
    katsuyo: k.Katsuyo

    @classmethod
    def from_token(cls, token):
        # TODO: tokenからの活用の判定
        return KatsuyoText(
            gokan="",
            katsuyo=k.KA_GYO_HENKAKU_KURU,
        )

    def __str__(self):
        return self.gokan + self.katsuyo.shushi
