import subprocess
from Redy.Tools.PathLib import Path

bash_history_paths = ['~/.bash_history']

cmder_history_path: bytes = subprocess.Popen(['where', 'cmder'], stdout=subprocess.PIPE).stdout.read()
if cmder_history_path:
    bash_history_paths.append(str(Path(cmder_history_path.decode()).parent().into('config').into('.history')))

analyze_len = 3

cache_times = 15
