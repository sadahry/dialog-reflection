import pytest
from dialog_reflection.reflection_cancelled import (
    ReflectionCancelled,
)
from dialog_reflection.lang.ja.cancelled_reason import (
    KeigoExclusionFailed,
)


@pytest.mark.parametrize(
    "msg, text, expected",
    [
        (
            "五段活用",
            "あなたと歩きました",
            "あなたと歩いた",
        ),
        # ref, https://ja.wikipedia.org/wiki/上一段活用
        (
            "上一段活用",
            "あなたと老いました",
            "あなたと老いた",
        ),
        # ref, https://ja.wikipedia.org/wiki/下一段活用
        (
            "下一段活用",
            "下に見えました",
            "下に見えた",
        ),
        # 「いく」のみ特殊
        (
            "五段活用",
            "あなたといきました",
            "あなたといった",
        ),
        # ref. https://ja.wikipedia.org/wiki/カ行変格活用
        (
            "カ行変格活用",
            "家にきました",
            "家にきた",
        ),
        (
            "カ行変格活用",
            "家に来ました",
            "家に来た",
        ),
        # ref. https://ja.wikipedia.org/wiki/サ行変格活用
        (
            "サ行変格活用",
            "軽くウォーキングしました",
            "軽くウォーキングした",
        ),
        (
            "サ行変格活用",
            "影響が生じました",
            "影響が生じた",
        ),
        # 形容詞
        # 語尾に過去がつく例が稀
        (
            "形容詞",
            "あなたは美しいのでした",
            "あなたは美しいのだった",
        ),
        # 形容動詞
        (
            "形容動詞",
            "あなたは傲慢でした",
            "あなたは傲慢だった",
        ),
        # 名詞
        (
            "名詞",
            "それは明日でした",
            "それは明日だった",
        ),
        # 固有名詞
        (
            "固有名詞",
            "それはステファンでした",
            "それはステファンだった",
        ),
        # 代名詞
        (
            "代名詞",
            "それはそれでした",
            "それはそれだった",
        ),
        # 接尾辞
        (
            "接尾辞-名詞的",
            "田中さんでした",
            "田中さんだった",
        ),
        (
            "接尾辞-動詞的",
            "汗ばみました",
            "汗ばんだ",
        ),
        # 語尾に過去がつく例が稀
        (
            "接尾辞-形容詞的",
            "田中っぽいのでした",
            "田中っぽいのだった",
        ),
        (
            "接尾辞-形状詞的",
            "田中だらけでした",
            "田中だらけだった",
        ),
        # 稀なケースであり想定されないためスキップ
        # (
        #     "連体詞",
        #     "その",
        # ),
        # (
        #     "接頭辞",
        #     "超",
        # ),
        # (
        #     "感動詞",
        #     "ほら",
        # ),
    ],
)
def test_spacy_keigo_exlude(nlp_ja, builder, msg, text, expected):
    sent = next(nlp_ja(text).sents)
    result = builder._exclude_keigo(sent)
    assert result == expected, msg


@pytest.mark.filterwarnings("ignore:.*")
def test_spacy_keigo_exlude_error(nlp_ja, builder):
    # 実運用上、「でしょう」が末尾にくることは想定されない
    sent = next(nlp_ja("あなたは美しくあるでしょう").sents)
    with pytest.raises(ReflectionCancelled) as e:
        builder._exclude_keigo(sent)
    type(e.value.reason) is KeigoExclusionFailed
