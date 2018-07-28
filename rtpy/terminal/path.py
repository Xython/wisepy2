from . import talking, bash_history_paths, namespace
from Redy.Tools.PathLib import Path
from .simple_analyze import to_vec, corr
import os


@talking
def ls(suffix: ' a filename suffix to apply filtering. default to perform no filtering.' = None, *,
       r: 'is recursive' = False):
    filter_fn = None
    app = Path.collect if r else Path.list_dir

    if suffix:
        def filter_fn(_: str):
            return _.endswith(suffix)
    listed = [str(each) for each in app(Path('.'), filter_fn)]
    return listed


@ls.completer
def ls(partial: str):
    partial = partial[2:].strip()
    if not partial or '--r'.startswith(partial):
        return '--r',
    return ()


@talking
def cd(pattern: str):
    return os.chdir(str(Path(pattern)))


@cd.completer
def cd(partial: str):
    partial = partial[2:].strip()

    path = Path(partial if partial else './')
    try:
        return (each.relative() for each in path.list_dir() if each.is_dir())
    except FileNotFoundError:
        pat = path.relative()

        def stream():
            for each in path.parent().list_dir():
                if not each.is_dir():
                    continue
                rel = each.relative()
                if rel.startswith(pat):
                    yield rel

        return stream()


@talking
def echo(*pattern):
    return ' '.join(map(str, pattern))
