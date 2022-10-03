import pytest
from spacy_dialog_reflection.reflector import Reflector


@pytest.fixture(scope="session")
def reflector(nlp_ja):
    return Reflector(nlp_ja)


def test_no_sentence(reflector):
    response = reflector.reflect("")
    assert response is None
