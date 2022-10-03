import time
import spacy

# TODO パッケージが完成したら消して、以下のように書き換える
import sys
dir = sys.path[0]
sys.path.append(dir + '/../')
from spacy_dialog_reflection.reflector import Reflector
# from spacy_dialog_reflection import Reflector

nlp = spacy.load('ja_ginza')
refactor = Reflector(nlp)

print("Ctrl+C to exit")
print()
print("システム: あなたの言葉に対して、伝え返しをします。")
print("システム: 今日の出来事について教えてください。")
print("システム: たとえば「今日は旅行へ行った」という言葉に対して「旅行へ行ったんですね」と返します。")
while True:
    message = input("あなた: ")
    response = refactor.reflect(message)
    print(f"システム: {response}")
