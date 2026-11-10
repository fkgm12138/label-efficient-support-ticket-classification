"""Local CLI or web demonstration; no external API, no department routing."""
from pathlib import Path
import argparse,json,os,sys,threading
R=Path(__file__).resolve().parent
for n in ['.tmp','.cache']:(R/n).mkdir(exist_ok=True)
os.environ.update(TEMP=str(R/'.tmp'),TMP=str(R/'.tmp'),PYTHONDONTWRITEBYTECODE='1')
import joblib,numpy as np
from threadpoolctl import threadpool_limits
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
class Predictor:
 def __init__(self,folder):
  self.folder=Path(folder).resolve()
  if not (self.folder/'baseline-model.joblib').exists():raise ValueError('Train first: python run.py --mode baseline --output outputs/demo-01')
  # Load only models created by this project; joblib/pickle is executable input.
  self.model=joblib.load(self.folder/'baseline-model.joblib');self.cp=joblib.load(self.folder/'conformal-model.joblib');self.lock=threading.Lock()
 def predict(self,text):
  if not isinstance(text,str) or not text.strip() or len(text)>4000:raise ValueError('Enter 1-4000 characters of English ticket text.')
  with self.lock,threadpool_limits(limits=2):
   p=self.model.predict_proba([text])[0];_,s=self.cp.predict_set(np.array([text]));mask=s[0,:,0]
  labels=self.model.classes_;top=np.argsort(-p)[:3];candidates=labels[mask].tolist()
  return {'text':text,'predicted_intent':str(labels[top[0]]),'top_three':[{'intent':str(labels[i]),'score':float(p[i])} for i in top],'candidate_set':candidates,'candidate_count':len(candidates),'suggested_action':'accept_single_intent' if len(candidates)==1 else 'refer_for_review','note':'Model probabilities are not correctness guarantees. This is an illustrative full-pool BANKING77 demo, not a production routing system or an out-of-domain detector.'}
 def metrics(self):return {k:json.loads((self.folder/f'{k}.json').read_text()) for k in ['baseline','conformal','data-audit']}
def main():
 p=argparse.ArgumentParser();p.add_argument('--models',type=Path);p.add_argument('--text');p.add_argument('--web',action='store_true');p.add_argument('--port',type=int,default=8765);a=p.parse_args()
 folder=a.models
 if folder is None:
  latest=R/'outputs/latest.json'
  if not latest.exists():p.error('Train a baseline first, or supply --models outputs/demo-01')
  folder=R/json.loads(latest.read_text())['directory']
 try:engine=Predictor(folder)
 except ValueError as e:p.error(str(e))
 if a.text:print(json.dumps(engine.predict(a.text),ensure_ascii=False,indent=2));return
 if not a.web:p.error('Use --text "..." or --web')
 class Handler(BaseHTTPRequestHandler):
  def send(self,code,payload,ctype='application/json; charset=utf-8'):
   body=payload if isinstance(payload,bytes) else json.dumps(payload,ensure_ascii=False).encode();self.send_response(code);self.send_header('Content-Type',ctype);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
  def do_GET(self):
   if self.path=='/':self.send(200,(R/'demo/index.html').read_bytes(),'text/html; charset=utf-8')
   elif self.path=='/api/metrics':self.send(200,engine.metrics())
   else:self.send(404,{'error':'Not found'})
  def do_POST(self):
   if self.path!='/api/predict':self.send(404,{'error':'Not found'});return
   try:
    size=int(self.headers.get('Content-Length','0'))
    if size<1 or size>20000:raise ValueError('Invalid request size')
    self.send(200,engine.predict(json.loads(self.rfile.read(size)).get('text')))
   except (ValueError,TypeError,AttributeError) as e:self.send(400,{'error':str(e)})
  def log_message(self,*args):pass
 server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler);print(f'Open http://127.0.0.1:{a.port} (Ctrl+C to stop). Localhost only; input is not saved.',flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
if __name__=='__main__':main()
