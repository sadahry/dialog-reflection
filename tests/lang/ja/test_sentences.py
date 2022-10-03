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
