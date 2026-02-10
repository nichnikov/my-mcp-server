import re
from pymystem3 import Mystem
from itertools import chain
from itertools import groupby
import operator

class TextsTokenizer:
    """Tokenizer wrapper using pymystem3 for lemmatization."""

    def __init__(self, mystem_path=None):
        self.stopwords = []
        self.synonyms = []
        self.stop_words_patterns = re.compile("")
        if mystem_path:
            self.m = Mystem(mystem_bin=mystem_path)
        else:
            self.m = Mystem()

    def texts2tokens(self, texts: list[str]) -> list[str]:
        """Lemmatization for texts in list."""
        try:
            text_ = "\n".join(texts)
            text_ = re.sub(r"[^\w\n\s]", " ", text_)
            lm_texts = "".join(self.m.lemmatize(text_.lower()))
            return [lm_tx.split() for lm_tx in lm_texts.split("\n")][:-1]
        except TypeError:
            return []

    def __call__(self, texts: list[str]):
        # Simplified call for the project needs
        return self.texts2tokens(texts)
