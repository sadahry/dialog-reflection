from spacy_dialog_reflection.lang.ja.katsuyo_hinshi import KatsuyoHinshi


def test_katsuyo_hinshi_generate(nlp_ja):
    doc = nlp_ja("明日が来る")
    kuru_token = doc[-1]
    kuru = KatsuyoHinshi.from_token(kuru_token)
    assert kuru.gokan == ""
    assert kuru.katsuyo.shushi == "くる"
