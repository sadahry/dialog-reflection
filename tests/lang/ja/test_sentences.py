import pytest
from spacy_dialog_reflection.reflector import Reflector


@pytest.fixture(scope="session")
def reflector(nlp_ja):
    return Reflector(nlp_ja)


@pytest.mark.parametrize(
    "message",
    [
        "",
        " ",  # 半角スペース
        "　",  # 全角スペース
    ],
)
def test_no_sentence(reflector, message):
    response = reflector.reflect(message)
    assert response is None
