import sys
import os
from Redy.Tools.PathLib import Path

rtpy_config_dir = Path('~/.rtpy')

if not rtpy_config_dir.exists():
    rtpy_config_dir.mkdir()
    src_dir = Path(__file__).parent().into('_terminal')
    src_dir.move_to(rtpy_config_dir)
    os.rename(str(rtpy_config_dir.into('_terminal')), str(rtpy_config_dir.into('rtpy_terminal')))

sys.path.append(str(rtpy_config_dir))

from rtpy_terminal.path import talking
