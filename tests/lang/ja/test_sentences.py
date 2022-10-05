import pytest
from spacy_dialog_reflection.reflector import Reflector


@pytest.fixture(scope="session")
def reflector(nlp_ja):
    return Reflector(nlp_ja)


@pytest.mark.parametrize(
    "message, assert_message",
    [
        ("", "empty message"),
        (" ", "half-width space"),
        ("　", "full-width space"),
    ],
)
def test_no_sentence(reflector, message, assert_message):
    response = reflector.reflect(message)
    assert response is None, assert_message


class TestReflectionBuilder:
    """Test of ReflectionBuilder private methods"""

    @pytest.mark.parametrize(
        "message, expected, assert_message",
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
        message,
        expected,
        assert_message,
    ):
        doc = reflector.nlp(message)
        sentence = reflector.builder._select_sentence(doc)
        assert sentence.text == expected, assert_message

    @pytest.mark.parametrize(
        "message, assert_message",
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
    def test_select_no_entence(
        self,
        reflector: Reflector,
        message,
        assert_message,
    ):
        doc = reflector.nlp(message)
        sentence = reflector.builder._select_sentence(doc)
        assert sentence is None, assert_message

    @pytest.mark.parametrize(
        "message, expected, assert_message",
        [
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
                "する。",
                "",
                "no dependencies",
            ),
        ],
    )
    def test_extract_tokens_with_nearest_root_deps(
        self,
        reflector: Reflector,
        message,
        expected,
        assert_message,
    ):
        sent = next(reflector.nlp(message).sents)
        func = reflector.builder._extract_tokens_with_nearest_root_deps
        tokens = func(sent)
        text = "".join([token.text for token in tokens])
        assert text == expected, assert_message
