from rtpy.cmd.talking import Talking
from Redy.Tools.PathLib import Path

root = Path(__file__).parent()


class AutoJump:
    max_cache = 20
    word_analyze_len = 3


class CacheIO:

    def __init__(self, file_path: Path, cache_size_getter):
        self.file_path = file_path
        self._max_cache_getter = cache_size_getter
        self._cached_size = 0
        if not file_path.exists():
            with file_path.open('w'):
                pass
            self._histories = []
        else:
            with file_path.open('r') as fr:
                self._histories = list(each[:-1] for each in fr)

    def __getitem__(self, item):
        return self._histories[item]

    def __len__(self):
        return len(self._histories)

    def __iter__(self):
        yield from self._histories

    def writeline(self, text):
        cached = self._histories
        cached.append(text)
        if self._cached_size >= self._max_cache_getter():
            with self.file_path.open('a+') as fw:
                fw.write('\n'.join(cached[-self._cached_size:]) + '\n')

            self._cached_size = 0
        self._cached_size += 1

    def cut(self, n: int):
        histories = self._histories = self._histories[-n:]
        with self.file_path.open('w') as fw:
            fw.write('\n'.join(histories) + '\n')

    def dump(self):
        if self._histories:
            with self.file_path.open('w') as fw:
                fw.write('\n'.join(self._histories) + '\n')


talking = Talking()
