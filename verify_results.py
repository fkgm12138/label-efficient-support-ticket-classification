"""Recalculate saved metrics and check split/query invariants; no model training."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np,pandas as pd
from sklearn.metrics import accuracy_score,f1_score
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--results',type=Path,default=R/'reference_results');a=p.parse_args();O=a.results.resolve()
def load(n):return json.loads((O/n).read_text(encoding='utf-8'))
checks=[]
for f in json.loads((R/'data/source-manifest.json').read_text())['files']:
 path=R/Path(f['file'].replace('\\','/'))
 assert hashlib.sha256(path.read_bytes()).hexdigest()==f['sha256'],str(path)
checks.append('raw data SHA-256 matches pinned source')
split=O/'split/split-manifest.csv'
if not split.exists():split=R/'data/processed/split-manifest.csv'
df=pd.read_csv(split);groups={k:set(v.norm) for k,v in df.groupby('split')}
assert df.groupby('split').size().to_dict()=={'calibration':1499,'pool':6994,'validation':1499}
assert all(not groups[a]&groups[b] for a,b in [('pool','validation'),('pool','calibration'),('validation','calibration')])
checks.append('fixed split sizes and normalised-text disjointness')
pred=pd.read_csv(O/'validation-predictions.csv');base=load('baseline.json')['tfidf_logistic_regression'];labels=sorted(json.loads((R/'data/raw/categories.json').read_text()))
assert len(pred)==1499 and set(pred.row_id)==set(df[df.split=='validation'].row_id)
assert abs(accuracy_score(pred.category,pred.prediction)-base['accuracy'])<1e-12
assert abs(f1_score(pred.category,pred.prediction,labels=labels,average='macro',zero_division=0)-base['macro_f1'])<1e-12
checks.append('accuracy and macro-F1 recalculated from 1499 predictions')
# A saved CSV is insufficient to independently verify prediction sets. When local
# models are present, recalculate sets from those trusted, freshly trained models.
if (O/'conformal-model.joblib').exists():
 import joblib
 model=joblib.load(O/'baseline-model.joblib');cp=joblib.load(O/'conformal-model.joblib')
 val=df[df.split=='validation'];_,sets=cp.predict_set(val.text.to_numpy());sets=sets[:,:,0];sizes=sets.sum(1);truth=val.category.to_numpy();index={c:i for i,c in enumerate(model.classes_)};cov=sets[np.arange(len(val)),[index[c] for c in truth]];single=sizes==1
 c=load('conformal.json')
 for key,value in {'empirical_validation_coverage':cov.mean(),'singleton_rate':single.mean(),'review_rate':(sizes!=1).mean(),'singleton_error_rate':(model.classes_[sets[single].argmax(1)]!=truth[single]).mean()}.items():assert abs(float(value)-c[key])<1e-12,key
 checks.append('fresh conformal prediction sets match coverage/referral/singleton-error metrics')
if (O/'active-learning-runs.csv').exists():
 frame=pd.read_csv(O/'active-learning-runs.csv');assert len(frame)==40
 pool=set(df[df.split=='pool'].row_id)
 for seed in [17,29,43,53,71]:
  initial=[]
  for method in ['random','margin']:
   selections=load(f'selection-{seed}-{method}.json');prior=set();assert [s['budget'] for s in selections]==[308,616,1232,2464]
   initial.append(selections[0]['row_ids'])
   for s in selections:
    ids=set(s['row_ids']);assert len(ids)==s['budget'] and prior<=ids<=pool;prior=ids
  assert initial[0]==initial[1]
 checks.append('40 acquisition fits, nested unique pool IDs, identical initial arms')
 if (O/'cleanlab-audit.json').exists():
  audit=load('cleanlab-audit.json');q=pd.read_csv(O/'label-review-queue.csv');assert audit['labels_modified']==0 and audit['confirmed_label_errors'] is None and len(q)==50 and set(q.human_decision)=={'pending'} and set(q.row_id)<=pool
  checks.append('Cleanlab queue is pool-only, pending, and unmodified')
report={'status':'passed','checks':checks,'scope':'saved-result consistency; fresh model checks only when model files exist','official_test_evaluated':False}
print(json.dumps(report,indent=2))
if O!=R/'reference_results':(O/'independent-verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
