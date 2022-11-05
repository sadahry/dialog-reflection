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
        "tag, will_be_allowed",
        [
            # VERB
            ("動詞-一般", True),
            # NOUN
            ("名詞-普通名詞-一般", True),
            # PROPN
            ("名詞-固有名詞-人名-姓", True),
            # ADJ
            ("形容詞-非自立可能", True),
            # ADJ
            ("形状詞-一般", True),
            # PRON
            ("代名詞", False),
            # AUX
            ("助動詞", False),
            # PART
            ("助詞-終助詞", False),
        ],
    )
    @pytest.mark.filterwarnings("ignore:empty text")
    def test_default_allowed_tag_pattern(
        self,
        builder: JaSpacyReflectionTextBuilder,
        tag,
        will_be_allowed,
    ):
        ptn = builder.allowed_tag_pattern
        if will_be_allowed:
            assert ptn.search(tag)
        else:
            assert not ptn.search(tag)

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
        builder: JaSpacyReflectionTextBuilder,
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
                "どうなんでしょうね。",
                "cannot extract one sentence not in ROOT_POS_SET",
            ),
            (
                "あれはどうでしょうね。あれじゃどうにも。",
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
            builder._extract_root_token(doc)
            assert False, assert_message

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
        ],
    )
    def test_extract_tokens_with_nearest_heads(
        self,
        nlp_ja,
        builder: JaSpacyReflectionTextBuilder,
        text,
        expected,
        assert_message,
    ):
        doc = nlp_ja(text)
        root = builder._extract_root_token(doc)
        tokens = builder._extract_tokens_with_nearest_heads(root)
        result = "".join(map(lambda t: t.text, tokens))
        assert result == expected, assert_message

    @pytest.mark.parametrize(
        "text, expected, assert_message",
        [
            (
                "今日は旅行へ行った。",
                "行っ",
                "sample sentence 動詞",
            ),
            (
                "いくなら学校かな。",
                "学校",
                "sample sentence 名詞-普通名詞",
            ),
            (
                "いくなら首里城かな。",
                "首里",
                "sample sentence 名詞-固有名詞",
            ),
            (
                "今日は楽しかった。",
                "楽しかっ",
                "sample sentence 形容詞",
            ),
            (
                "今日は充実だ。",
                "充実",
                "sample sentence 形状詞",
            ),
            (
                "明日の休日はどうかな。",
                "休日",
                "ignore かな",
            ),
            (
                "そんなの笑っちゃいますもの。",
                "笑っ",
                "ignore もの",
            ),
        ],
    )
    def test_extract_bottom_token(
        self,
        nlp_ja,
        builder: JaSpacyReflectionTextBuilder,
        text,
        expected,
        assert_message,
    ):
        doc = nlp_ja(text)
        sent = next(doc.sents)
        bottom = builder._extract_bottom_token(sent)
        assert bottom.text == expected, assert_message

    def test_extract_bottom_token_error(
        self,
        nlp_ja,
        builder: JaSpacyReflectionTextBuilder,
    ):
        doc = nlp_ja("アレはどうかな。")
        sent = next(doc.sents)
        with pytest.raises(ReflectionTextError):
            builder._extract_bottom_token(sent)

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
            (
                "今日が繁忙期だ。",
                "繁忙期なんですね。",
                "ADJ parse",
            ),
            (
                "今日が繁忙期。",
                "繁忙期なんですね。",
                "NOUN parse",
            ),
            (
                "今年は繁忙期なだけだ。",
                "繁忙期なだけなんですね。",
                "FUKUJOSHI + ADJ parse",
            ),
            (
                "今年は繁忙期だけだ。",
                "繁忙期だけなんですね。",
                "FUKUJOSHI + NOUN parse",
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
