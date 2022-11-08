from dialog_reflection.reflector import SpacyReflector
from dialog_reflection.lang.ja.reflection_text_builder import (
    JaPlainReflectionTextBuilder,
)
import pytest


@pytest.fixture(scope="session")
def builder():
    return JaPlainReflectionTextBuilder()


@pytest.fixture(scope="session")
def reflector(nlp_ja, builder):
    return SpacyReflector(nlp_ja, builder)
