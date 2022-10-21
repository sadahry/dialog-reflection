import pytest
from spacy_dialog_reflection.reflection_text_builder import ReflectionTextError
from spacy_dialog_reflection.reflector import SpacyReflector
from spacy_dialog_reflection.lang.ja.reflection_text_builder import (
    JaSpacyReflectionTextBuilder,
)


@pytest.fixture(scope="session")
def builder():
    return JaSpacyReflectionTextBuilder()


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
        builder: JaSpacyReflectionTextBuilder,
        text,
        assert_message,
    ):
        doc = nlp_ja(text)
        with pytest.raises(ReflectionTextError):
            builder.build(doc)
            assert False, assert_message

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
        nlp_ja,
        builder: JaSpacyReflectionTextBuilder,
        text,
        expected,
        assert_message,
    ):
        doc = nlp_ja(text)
        sentence = builder._select_sentence(doc)
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
        nlp_ja,
        builder: JaSpacyReflectionTextBuilder,
        text,
        assert_message,
    ):
        doc = nlp_ja(text)
        with pytest.raises(ReflectionTextError):
            builder._select_sentence(doc)
            assert False, assert_message

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
        nlp_ja,
        builder: JaSpacyReflectionTextBuilder,
        text,
        expected,
        assert_message,
    ):
        root = next(nlp_ja(text).sents).root
        func = builder._extract_tokens_with_nearest_root_heads
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
        nlp_ja,
        builder: JaSpacyReflectionTextBuilder,
        text,
        expected,
        assert_message,
    ):
        root = next(nlp_ja(text).sents).root
        func = builder._build_suffix
        text = func(root)
        assert text == expected, assert_message

    @pytest.mark.filterwarnings("ignore:Unsupported Tag")
    def test_build_suffix_error(
        self,
        nlp_ja,
        builder: JaSpacyReflectionTextBuilder,
    ):
        """
        _build_suffixでエラーとなりテキストを返すケース
        """
        # rootが副詞の場合はエラーとなる想定
        text = "どう"
        root = next(nlp_ja(text).sents).root
        assert root.tag_ == "副詞"
        func = builder._build_suffix
        with pytest.raises(ReflectionTextError) as e:
            func(root)

        # エラー時には元rootの文字列を含んだ状態で返す想定
        excepted = text + builder.word_ending_unpersed
        assert e.value.instant_reflection_text == excepted

    @pytest.mark.filterwarnings(r"ignore:.*NO VALID SENTENSES IN DOC")
    def test_safe_build_catch_error(
        self,
        nlp_ja,
        builder: JaSpacyReflectionTextBuilder,
    ):
        """
        safe_buildでエラーとならないでテキストを返すケース
        """
        # rootが副詞の場合はエラーとなる想定
        text = "どう"
        doc = nlp_ja(text)

        root = next(doc.sents).root
        assert root.tag_ == "副詞"

        result = builder.safe_build(doc)

        # rootの選出時にエラーとなるはずなので、エラー用テキストを返す想定
        excepted = builder.message_when_not_valid_doc
        assert result == excepted