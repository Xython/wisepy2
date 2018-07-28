import warnings
from Redy.Tools.PathLib import Path
from . import talking
from .auto_jump_analyze import rtpy_history_cached_file, rtpy_history_rank_file
# noinspection PyPackageRequirements
from linq import Flow as seq
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
    path_str = str(Path(pattern))
    rtpy_history_cached_file.writeline(path_str)
    rtpy_history_rank_file.writeline(path_str)

    return os.chdir(path_str)


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


# noinspection PyProtectedMember
@talking.alias('j')
def jump(*pattern):
    text = ' '.join(pattern)
    correlation_asoc_lst = tuple(rtpy_history_cached_file.corr_with(text).items())
    the_best_ten = seq(correlation_asoc_lst).sorted(lambda _: -_[1]).take(10).map(lambda _: _[0])._

    for line in the_best_ten:
        if line in rtpy_history_rank_file:
            return line
    warnings.warn("Not enough information to jump!")
    return str(Path('./'))


@jump.exiter
def jump():
    print('dumping')
    rtpy_history_cached_file.dump()
    rtpy_history_rank_file.dump()
