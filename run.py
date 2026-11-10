"""Run in a NEW output directory. All caches, logs and outputs stay in this repository."""
from pathlib import Path
import argparse,datetime,json,os,subprocess,sys,time
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--mode',choices=['baseline','full'],default='baseline');p.add_argument('--output',type=Path);a=p.parse_args()
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
out=(a.output or R/'outputs'/f'{a.mode}-{stamp}').resolve()
if R not in out.parents:raise SystemExit('--output must be inside this project, e.g. outputs/demo-01')
if out.exists() and any(out.iterdir()):raise SystemExit('Output directory is not empty. Choose a new --output; existing runs are preserved.')
out.mkdir(parents=True,exist_ok=True)
for n in ['.tmp','.cache/matplotlib']:(R/n).mkdir(parents=True,exist_ok=True)
env=os.environ.copy();env.update(FYP_OUTPUT_DIR=str(out),FYP_BASELINE_ONLY='1' if a.mode=='baseline' else '0',TEMP=str(R/'.tmp'),TMP=str(R/'.tmp'),MPLCONFIGDIR=str(R/'.cache/matplotlib'),PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
status={'status':'running','mode':a.mode,'started':datetime.datetime.now().isoformat(),'steps':[]}
start=time.monotonic()
try:
 for script in ['run_pilot.py']+(['analyze_pilot.py'] if a.mode=='full' else []):
  with (out/f'{script}.log').open('w',encoding='utf-8') as log:
   proc=subprocess.Popen([sys.executable,'-u',str(R/'src'/script)],cwd=R,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding='utf-8')
   for line in proc.stdout:print(line,end='',flush=True);log.write(line);log.flush()
   code=proc.wait();status['steps'].append({'script':script,'exit_code':code})
   if code:raise RuntimeError(f'{script} failed. See {out/script}.log')
  subprocess.run([sys.executable,str(R/'verify_results.py'),'--results',str(out)],cwd=R,env=env,check=True)
 status['status']='passed';(R/'outputs/latest.json').write_text(json.dumps({'directory':str(out.relative_to(R))},indent=2),encoding='utf-8')
 print(f'ALL CHECKS PASSED. Results: {out}')
except Exception as exc:status['status']='failed';status['error']=str(exc);raise
finally:
 status['elapsed_seconds']=round(time.monotonic()-start,2)
 (out/'run-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
