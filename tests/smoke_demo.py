"""Exercise the actual localhost demo including invalid requests."""
from pathlib import Path
import argparse,json,os,socket,subprocess,sys,time,urllib.request,urllib.error
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--models',type=Path,required=True);a=p.parse_args()
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
proc=subprocess.Popen([sys.executable,str(R/'demo.py'),'--models',str(a.models.resolve()),'--web','--port',str(port)],cwd=R,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
base=f'http://127.0.0.1:{port}'
try:
 for _ in range(120):
  if proc.poll() is not None:raise RuntimeError(proc.stdout.read().decode())
  try:
   with urllib.request.urlopen(base,timeout=1) as res:assert b'Customer Support Ticket Classification' in res.read()
   break
  except (OSError,urllib.error.URLError):time.sleep(.25)
 else:raise RuntimeError('Server did not start')
 with urllib.request.urlopen(base+'/api/metrics') as res:assert 'baseline' in json.load(res)
 for text in ['I lost my bank card. How can I freeze it?','The cash machine did not give me my money.','I have a problem with my card and a payment.']:
  req=urllib.request.Request(base+'/api/predict',data=json.dumps({'text':text}).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req) as res:d=json.load(res)
  assert len(d['top_three'])==3 and d['predicted_intent']==d['top_three'][0]['intent']
  assert d['candidate_count']==len(d['candidate_set'])
  assert (d['suggested_action']=='accept_single_intent')==(d['candidate_count']==1)
  print(json.dumps({'input':text,'intent':d['predicted_intent'],'candidate_count':d['candidate_count'],'action':d['suggested_action']}))
 req=urllib.request.Request(base+'/api/predict',data=b'{"text":""}',headers={'Content-Type':'application/json'})
 try:urllib.request.urlopen(req);raise AssertionError('Empty text accepted')
 except urllib.error.HTTPError as e:assert e.code==400
 try:urllib.request.urlopen(base+'/missing');raise AssertionError('Unknown path accepted')
 except urllib.error.HTTPError as e:assert e.code==404
 print('DEMO_HTTP_CHECKS_PASSED')
finally:
 proc.terminate()
 try:proc.wait(timeout=10)
 except subprocess.TimeoutExpired:proc.kill();proc.wait()
