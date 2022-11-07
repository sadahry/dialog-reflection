import time

# fmt: off
# TODO パッケージが完成したら消して、以下のように書き換える
import sys
dir = sys.path[0]
sys.path.append(dir + "/../")
from dialog_reflection.lang.ja.reflection_text_builder import JaSpacyReflector # noqa: E402,E261
# from dialog_reflection import SpacyReflector
# fmt: on

refactor = JaSpacyReflector(model="ja_ginza")

print("Ctrl+C to exit")
print()
print("システム: あなたの言葉に対して、おうむ返しをします。")
print("システム: 今日の出来事について、教えてください。")
print("システム: たとえば「今日は旅行へ行った」という言葉に対して、私は「旅行へ行ったんですね」と返します。")
while True:
    message = input("あなた: ")
    start = time.time()
    response = refactor.reflect(message)
    end = time.time()
    print(f"システム: {refactor.reflect(message)} ({end - start:.3f} sec)")
