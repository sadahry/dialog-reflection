import spacy_dialog_reflection.lang.ja.katsuyo as k
from dataclasses import dataclass


@dataclass(frozen=True)
class KatsuyoHinshi:
    gokan: str
    katsuyo: k.Katsuyo

    @classmethod
    def from_token(cls, token):
        # TODO: tokenからの活用の判定
        return KatsuyoHinshi(
            gokan="",
            katsuyo=k.KA_GYO_HENKAKU_KURU,
        )
