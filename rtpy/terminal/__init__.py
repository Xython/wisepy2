from rtpy.cmd.talking import Talking
from Redy.Tools.PathLib import Path

root = Path('~/.rtpy')
if not root.exists():
    root.mkdir()

config = root.into('.rtpyrc.py')

namespace = {}
if not config.exists():
    with config.open('w') as fw, Path(__file__).parent().into('default_config.py').open('r') as fr:
        fw.write(fr.read())

with config.open('r') as fr:
    exec(fr.read(), namespace)

analyze_len = namespace['analyze_len']
bash_history_paths: list = [each for each in [Path(each) for each in namespace['bash_history_paths']] if each.exists()]
talking = Talking()
