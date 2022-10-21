import pytest
from spacy_dialog_reflection.reflector import Reflector


@pytest.fixture(scope="session")
def reflector(nlp_ja):
    return Reflector(nlp_ja)


def test_work_well(reflector):
    message = "今日は旅行へ行く"
    response = reflector.reflect(message)
    assert response == "旅行へ行くんですね。"


class TestReflectionBuilder:
    """Test of ReflectionBuilder private methods"""

    @pytest.mark.parametrize(
        "text, assert_message",
        [
            ("", "empty text"),
            (" ", "half-width space"),
            ("　", "full-width space"),
        ],
    )
    @pytest.mark.filterwarnings("ignore:empty text")
    def test_no_sentence(
        self,
        reflector: Reflector,
        text,
        assert_message,
    ):
        doc = reflector.nlp(text)
        vaild, _ = reflector.builder.check_valid(doc)
        assert not vaild, assert_message

    @pytest.mark.parametrize(
        "text, expected, assert_message",
        [
            (
                "今日は旅行に行きました。",
                "今日は旅行に行きました。",
                "extract sentence",
            ),
            (
                "こんにちは。今日は旅行に行きました。",
                "今日は旅行に行きました。",
                "extract last sentence VERB",
            ),
            (
                "こんにちは。今日は旅行に行きました。最高でした。",
                "最高でした。",
                "extract last sentence NOUN",
            ),
            (
                "こんにちは。今日は旅行に行きました。田中さんとです。",
                "田中さんとです。",
                "extract last sentence PROUN",
            ),
            (
                "こんにちは。今日は旅行に行きました。楽しかったです。",
                "楽しかったです。",
                "extract last sentence ADJ",
            ),
            (
                "こんにちは。今日は旅行に行きました。そこそこでした。",
                "今日は旅行に行きました。",
                "not extract last sentence ADV",
            ),
        ],
    )
    def test_select_sentence(
        self,
        reflector: Reflector,
        text,
        expected,
        assert_message,
    ):
        doc = reflector.nlp(text)
        sentence = reflector.builder._select_sentence(doc)
        assert sentence is not None
        assert sentence.text == expected, assert_message

    @pytest.mark.parametrize(
        "text, assert_message",
        [
            (
                "そういうのってどうなんですか。",
                "cannot extract one sentence not in ROOT_POS_SET",
            ),
            (
                "そういうのってどうなんですか。ここはどこですか。まだですか。",
                "cannot extract sentences not in ROOT_POS_SET",
            ),
        ],
    )
    @pytest.mark.filterwarnings("ignore:no valid sentenses")
    def test_select_no_sentence(
        self,
        reflector: Reflector,
        text,
        assert_message,
    ):
        doc = reflector.nlp(text)
        sentence = reflector.builder._select_sentence(doc)
        assert sentence is None, assert_message

    @pytest.mark.parametrize(
        "text, expected, assert_message",
        [
            (
                "今日は旅行へ行った。",
                "旅行へ",
                "sample sentence",
            ),
            (
                "社員をする。",
                "社員を",
                "obj dependency",
            ),
            (
                "民間の社員をする。",
                "民間の社員を",
                "obj dependency multi-word",
            ),
            (
                "今年から社員をする。",
                "社員を",
                "obj dependency does not extract distant dependencies",
            ),
            (
                "働く。",
                "",
                "no dependencies",
            ),
        ],
    )
    def test_extract_tokens_with_nearest_root_heads(
        self,
        reflector: Reflector,
        text,
        expected,
        assert_message,
    ):
        root = next(reflector.nlp(text).sents).root
        func = reflector.builder._extract_tokens_with_nearest_root_heads
        tokens = func(root)
        text = "".join(map(lambda t: t.text, tokens))
        assert text == expected, assert_message

    @pytest.mark.parametrize(
        "text, expected, assert_message",
        [
            (
                "今日は旅行へ行った。",
                "行ったんですね。",
                "sample sentence",
            ),
            (
                "社員をする。",
                "するんですね。",
                "obj dependency",
            ),
            (
                "民間の社員をする。",
                "するんですね。",
                "obj dependency multi-word",
            ),
            (
                "今年から社員をする。",
                "するんですね。",
                "obj dependency does not extract distant dependencies",
            ),
            (
                "働く。",
                "働くんですね。",
                "no dependencies",
            ),
        ],
    )
    def test_build_suffix(
        self,
        reflector: Reflector,
        text,
        expected,
        assert_message,
    ):
        root = next(reflector.nlp(text).sents).root
        func = reflector.builder._build_suffix
        text = func(root)
        assert text == expected, assert_message
