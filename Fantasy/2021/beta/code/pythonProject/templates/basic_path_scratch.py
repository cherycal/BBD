import sys

sys.path.append('../modules')
import tools
from pathlib import Path

plat = tools.get_platform()
print(plat)

p = Path.cwd()
data_dir = p / 'data'
data_dir.mkdir(mode=0o755,exist_ok=True)
