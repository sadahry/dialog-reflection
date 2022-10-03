import spacy
from reflector import Reflector

nlp = spacy.load('ja_ginza')
refactor = Reflector(nlp)

while True:
    print("input message:")
    message = input()

    response = refactor.reflect(message)
    print(response)
