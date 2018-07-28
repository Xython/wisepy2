from collections import Counter
from . import AutoJump, CacheIO, root


class _CacheVectorGatherIO:

    def __init__(self, cache_io: CacheIO):
        self._cache_io = cache_io
        self._vectors = list(map(to_vec, cache_io))

    def __len__(self):
        return len(self._vectors)

    def cut(self, n: int):
        self._cache_io.cut(n)
        self._vectors = self._vectors[-n:]

    def writeline(self, line: str):
        self._cache_io.writeline(line)
        self._vectors.append(to_vec(line))

    def corr_with(self, line: str):
        line_vec = to_vec(line)

        ret = {}
        for key, vec in zip(self._cache_io, self._vectors):
            if key not in ret:
                ret[key] = corr(vec, line_vec)

        return ret

    def index_vec(self, idx):
        return self._vectors[idx]

    def index_line(self, idx):
        return self._cache_io[idx]

    def dump(self):
        self._cache_io.dump()


def _analyzer(text, ngram):
    tokens = text
    for k in range(1, ngram + 1):
        n = len(tokens) - k
        for i in range(n):
            yield tokens[i: i + k]


def to_vec(s: str):
    return Counter(_analyzer(s, AutoJump.word_analyze_len))


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


rtpy_history_cached_file = _CacheVectorGatherIO(CacheIO(root.into('wd_history'), lambda: AutoJump.max_cache))
rtpy_history_rank_file = CacheIO(root.into('wd_ranks'), lambda: AutoJump.max_cache)
