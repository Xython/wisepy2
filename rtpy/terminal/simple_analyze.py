import pprint
from collections import Counter
from . import analyze_len, namespace


def _analyzer(text, ngram):
    tokens = text
    for k in range(1, ngram + 1):
        n = len(tokens) - k
        for i in range(n):
            yield tokens[i: i + k]


def to_vec(s: str, ngram=analyze_len):
    return Counter(_analyzer(s, ngram))


def corr(a: Counter, b: Counter):
    na = len(a)
    nb = len(b)

    def get_score(l, r):
        weights = 0
        score = 0
        for lk, lv in l.items():
            v = r.get(lk)
            weight = len(lk)
            weights += weight
            if v is None:
                continue

            if v > lv:
                v, lv = lv, v
            score += weight * v / lv

        if weights is 0:
            return 0

        return score / weights

    return (get_score(a, b) * na + get_score(b, a) * nb) / (na + nb)
