"""
文本工具模块：演示同一包内的第二个模块。
"""


def count_words(text):
    """统计英文单词数量（按空白切分）。

    注意：这只是教学示例，不适合统计中文；
    中文分词需要额外工具，W1 不展开。
    """
    return len(text.split())


def normalize(text):
    """去掉首尾空白，并把连续空白压成一个空格。"""
    return " ".join(text.split())


if __name__ == "__main__":
    sample = "  hello   ai   infra  "
    print("count_words:", count_words(sample))
    print("normalize:", repr(normalize(sample)))
