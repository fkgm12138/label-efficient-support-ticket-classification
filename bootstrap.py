"""Install pinned dependencies into a local environment; never use a global pip."""
from pathlib import Path
import argparse,os,subprocess,sys,venv
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--wheelhouse',type=Path);a=p.parse_args()
if sys.version_info[:2]!=(3,12):raise SystemExit('Please run this installer with Python 3.12 (64-bit).')
for n in ['.tmp','.cache']:(R/n).mkdir(exist_ok=True)
os.environ.update(TEMP=str(R/'.tmp'),TMP=str(R/'.tmp'),PIP_CACHE_DIR=str(R/'.cache'),PYTHONDONTWRITEBYTECODE='1')
exe=R/'.venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
if not exe.exists():venv.EnvBuilder(with_pip=True).create(R/'.venv')
cmd=[str(exe),'-m','pip','install','--disable-pip-version-check','-r',str(R/'requirements-lock.txt')]
if a.wheelhouse:cmd+=['--no-index','--find-links',str(a.wheelhouse.resolve())]
subprocess.run(cmd,cwd=R,check=True);subprocess.run([str(exe),'-m','pip','check'],cwd=R,check=True)
print('Ready. Use the project .venv interpreter. See docs/DEMO_zh.md.')
