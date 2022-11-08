import pytest
from dialog_reflection.reflection_text_builder import (
    ReflectionCancelled,
    NoValidSentence,
)
from dialog_reflection.reflector import SpacyReflector
from dialog_reflection.lang.ja.reflection_text_builder import (
    JaPlainReflectionTextBuilder,
    WhTokenNotSupported,
)


@pytest.fixture(scope="session")
def builder():
    return JaPlainReflectionTextBuilder()


@pytest.fixture(scope="session")
def reflector(nlp_ja, builder):
    return SpacyReflector(nlp_ja, builder)


def test_work_well(reflector):
    message = "今日は旅行へ行く"
    response = reflector.reflect(message)
    assert response == "旅行へ行くんですね。"


class TestReflectionBuilder:
    """Test of ReflectionBuilder private methods"""

    @pytest.mark.parametrize(
        "text, assert_message",
        [
            ("", "empty text should be error"),
            (" ", "half-width space should be error"),
            ("　", "full-width space should be error"),
        ],
    )
    @pytest.mark.filterwarnings("ignore:empty text")
    def test_no_sentence(
        self,
        nlp_ja,
        builder: JaPlainReflectionTextBuilder,
        text,
        assert_message,
    ):
        doc = nlp_ja(text)
        with pytest.raises(ReflectionCancelled):
            builder.build(doc)
            assert False, assert_message

    @pytest.mark.parametrize(
        "text, expected, assert_message",
        [
            (
                "今日は旅行に行きました。",
                "行き",
                "extract sentence",
            ),
            (
                "こんにちは。今日は旅行に行きました。",
                "行き",
                "extract last sentence VERB",
            ),
            (
                "こんにちは。今日は旅行に行きました。最高でした。",
                "最高",
                "extract last sentence NOUN",
            ),
            (
                "こんにちは。今日は旅行に行きました。田中とです。",
                "田中",
                "extract last sentence PROUN",
            ),
            (
                "こんにちは。今日は旅行に行きました。楽しかったです。",
                "楽しかっ",
                "extract last sentence ADJ",
            ),
            (
                "こんにちは。今日は旅行に行きました。そこそこでした。",
                "行き",
                "not extract last sentence ADV",
            ),
            (
                "こんにちは。今日は旅行に行きました。何で行ったんでしょうね。",
                "行き",
                "not extract last sentence 何",
            ),
            (
                "こんにちは。今日は旅行に行きました。なんで行ったんでしょうね。",
                "行き",
                "not extract last sentence なん",
            ),
            (
                "こんにちは。今日は旅行に行きました。なにで行ったんでしょうね。",
                "行き",
                "not extract last sentence なに",
            ),
            (
                "こんにちは。今日は旅行に行きました。なぜ行ったんでしょうね。",
                "行き",
                "not extract last sentence なぜ",
            ),
            (
                "こんにちは。今日は旅行に行きました。誰と行ったんでしょうね。",
                "行き",
                "not extract last sentence 誰",
            ),
            (
                "こんにちは。今日は旅行に行きました。いつ行ったんでしょうね。",
                "行き",
                "not extract last sentence いつ",
            ),
            (
                "こんにちは。今日は旅行に行きました。 どこに行ったんでしょうね。",
                "行き",
                "not extract last sentence どこ",
            ),
            (
                "こんにちは。今日は旅行に行きました。 どちらに行ったんでしょうね。",
                "行き",
                "not extract last sentence どちら",
            ),
            (
                "こんにちは。今日は旅行に行きました。 どう行ったんでしょうね。",
                "行き",
                "not extract last sentence どう",
            ),
            (
                "こんにちは。今日は旅行に行きました。 どのように行ったんでしょうね。",
                "行き",
                "not extract last sentence どの",
            ),
            (
                "こんにちは。今日は旅行に行きました。 どれくらい行ったんでしょうね。",
                "行き",
                "not extract last sentence どれ",
            ),
            (
                "こんにちは。今日は旅行に行きました。 どんなので行ったんでしょうね。",
                "行き",
                "not extract last sentence どんな",
            ),
            (
                "こんにちは。今日は旅行に行きました。 どっちに行ったんでしょうね。",
                "行き",
                "not extract last sentence どっち",
            ),
            (
                "こんにちは。今日は旅行に行きました。 いくらで行ったんでしょうね。",
                "行き",
                "not extract last sentence いくら",
            ),
            (
                "こんにちは。今日は旅行に行きました。 いくつの頃に行ったんでしょうね。",
                "行き",
                "not extract last sentence いくつ",
            ),
            (
                "こんにちは。今日は旅行に行きました。 どうでしょう？",
                "行き",
                "not extract last sentence ？",
            ),
            (
                "こんにちは。今日は旅行に行きました。 どうでしょう?",
                "行き",
                "not extract last sentence ?",
            ),
        ],
    )
    @pytest.mark.filterwarnings("ignore:sent has wh_word")
    def test_extract_root_token(
        self,
        nlp_ja,
        builder: JaPlainReflectionTextBuilder,
        text,
        expected,
        assert_message,
    ):
        doc = nlp_ja(text)
        root = builder._extract_root_token(doc)
        assert root.text == expected, assert_message

    @pytest.mark.parametrize(
        "text, assert_message",
        [
            (
                "とてもなんでしょうね。",
                "cannot extract one sentence not in ROOT_POS_SET",
            ),
            (
                "あれはとてもでしょうね。あれじゃこうでも。",
                "cannot extract sentences not in ROOT_POS_SET",
            ),
        ],
    )
    @pytest.mark.filterwarnings("ignore:no valid sentenses")
    def test_select_no_sentence(
        self,
        nlp_ja,
        builder: JaPlainReflectionTextBuilder,
        text,
        assert_message,
    ):
        doc = nlp_ja(text)
        with pytest.raises(ReflectionCancelled) as e:
            builder._extract_root_token(doc)

        assert isinstance(e.value.reason, NoValidSentence), assert_message

    @pytest.mark.parametrize(
        "text, assert_message",
        [
            (
                "どうでしょうね。",
                "has WH in one sentence",
            ),
            (
                "あれはとてもでしょうね。あれじゃどうしようにも。",
                "has WH in last sentence",
            ),
            (
                "どうしてこうなんでしょうね。これじゃどうにも。",
                "has WH in both sentences",
            ),
        ],
    )
    @pytest.mark.filterwarnings("ignore:sent has wh_word")
    def test_wh_token_not_supported(
        self,
        nlp_ja,
        builder: JaPlainReflectionTextBuilder,
        text,
        assert_message,
    ):
        doc = nlp_ja(text)
        with pytest.raises(ReflectionCancelled) as e:
            builder._extract_root_token(doc)

        assert isinstance(e.value.reason, WhTokenNotSupported), assert_message

    @pytest.mark.parametrize(
        "text, expected, assert_message",
        [
            (
                "今日は旅行へ行った。",
                "旅行へ行った。",
                "sample sentence",
            ),
            (
                "社員をする。",
                "社員をする。",
                "obj dependency",
            ),
            (
                "民間の社員をする。",
                "民間の社員をする。",
                "obj dependency multi-word",
            ),
            (
                "今年から社員をする。",
                "社員をする。",
                "obj dependency does not extract distant dependencies",
            ),
            (
                "旅行に行ってくる。",
                "旅行に行ってくる。",
                "latest root(VARB) after root token(VERB)",
            ),
            (
                "旅行に行ってくるか迷ったけど雨だったので今日は家で過ごすことにした。",
                "過ごすことにした。",
                "long sentence",
            ),
            (
                "働く。",
                "働く。",
                "no dependencies",
            ),
            (
                "対人恐怖症を克服する。",
                "対人恐怖症を克服する。",
                "with compound",
            ),
            (
                "400メートル走を頑張る。",
                "400メートル走を頑張る。",
                "with nummod",
            ),
            (
                "面接での対人恐怖症を克服する。",
                "対人恐怖症を克服する。",
                "with compound",
            ),
            (
                "難しいんですよね。それが。",
                "難しいんですよね。",
                "rootが不適切なため前文が参照される",
            ),
        ],
    )
    def test_extract_tokens_with_nearest_heads(
        self,
        nlp_ja,
        builder: JaPlainReflectionTextBuilder,
        text,
        expected,
        assert_message,
    ):
        doc = nlp_ja(text)
        root = builder._extract_root_token(doc)
        tokens = builder._extract_tokens_with_nearest_heads(root)
        result = "".join(map(lambda t: t.text, tokens))
        assert result == expected, assert_message

    def test_extract_root_token_error(
        self,
        nlp_ja,
        builder: JaPlainReflectionTextBuilder,
    ):
        """
        _extract_root_tokenでエラーとなりテキストを返すかをテストする
        """
        # rootが副詞の場合はエラーとなる想定
        text = "そう"
        doc = nlp_ja(text)
        assert doc[0].tag_ == "副詞"
        func = builder._extract_root_token
        with pytest.raises(ReflectionCancelled) as e:
            func(doc)

        assert isinstance(e.value.reason, NoValidSentence)
        assert e.value.reason.doc is not None
        assert text in e.value.reason.doc.text, "e has doc when error"

    @pytest.mark.filterwarnings(r"ignore:.*Traceback")
    def test_safe_build_catch_error(
        self,
        nlp_ja,
        builder: JaPlainReflectionTextBuilder,
    ):
        """
        safe_buildがエラー時にもテキストを返すかをテストする
        """
        # textが空の場合はエラーとなる想定
        text = ""
        doc = nlp_ja(text)

        result = builder.safe_build(doc)

        # rootの選出時にエラーとなるはずなので、エラー用テキストを返す想定
        excepted = builder.message_when_error
        assert result == excepted
