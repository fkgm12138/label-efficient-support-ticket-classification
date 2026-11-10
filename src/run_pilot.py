"""Original pilot protocol; output path supplied by run.py. See docs/METHODS.md."""
from pathlib import Path
import os,json,time,hashlib,unicodedata,warnings,platform
import numpy as np,pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,f1_score,classification_report
from sklearn.dummy import DummyClassifier
from sklearn.exceptions import ConvergenceWarning
from skactiveml.pool import uncertainty_scores
from mapie.classification import SplitConformalClassifier
from threadpoolctl import threadpool_limits
import joblib
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ['FYP_OUTPUT_DIR']);OUT.mkdir(parents=True,exist_ok=True)
(OUT/'split').mkdir(exist_ok=True)
def save(name,obj): (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding='utf-8')
def norm(x): return ' '.join(unicodedata.normalize('NFKC',str(x)).casefold().split())
def model(): return Pipeline([('tfidf',TfidfVectorizer(ngram_range=(1,2),min_df=2,sublinear_tf=True,max_features=20000)),('classifier',LogisticRegression(C=1.0,max_iter=1000,random_state=20261027))])
def metrics(y,p): return {'accuracy':float(accuracy_score(y,p)),'macro_f1':float(f1_score(y,p,labels=classes,average='macro',zero_division=0))}
start=time.time();save('status.json',{'status':'running','date':time.strftime('%Y-%m-%d'),'protocol_date':'2026-10-27'})
train=pd.read_csv(ROOT/'data/raw/train.csv');test=pd.read_csv(ROOT/'data/raw/test.csv')
classes=sorted(json.loads((ROOT/'data/raw/categories.json').read_text()))
assert len(classes)==77 and set(train.category)==set(classes)
train['row_id']=['train:'+str(i) for i in range(len(train))];train['norm']=train.text.map(norm)
test['norm']=test.text.map(norm)
invalid=train.text.isna()|train.category.isna()|train.norm.eq('')
conflict=set(train.groupby('norm').category.nunique().loc[lambda x:x>1].index)
overlap=set(train.norm)&set(test.norm)
clean=train.loc[~invalid & ~train.norm.isin(conflict) & ~train.norm.isin(overlap)].drop_duplicates('norm').copy()
pool,hold=train_test_split(clean,test_size=.3,stratify=clean.category,random_state=20261027)
val,cal=train_test_split(hold,test_size=.5,stratify=hold.category,random_state=20261027)
for a,b in [(pool,val),(pool,cal),(cal,val)]: assert not set(a.norm)&set(b.norm)
assert not set(clean.norm)&set(test.norm)
audit={'raw_train':len(train),'official_test':len(test),'classes':len(classes),'invalid_train_rows':int(invalid.sum()),'duplicate_train_rows_normalized':int(train.norm.duplicated().sum()),'conflicting_train_texts':len(conflict),'train_test_shared_texts':len(overlap),'clean_train':len(clean),'pool':len(pool),'validation':len(val),'calibration':len(cal),'test_evaluation':'not performed; only text overlap audited','near_duplicate_audit':'not yet performed','normalization':'NFKC + casefold + whitespace collapse','split_seed':20261027}
save('data-audit.json',audit)
pd.concat([part.assign(split=name) for name,part in [('pool',pool),('validation',val),('calibration',cal)]]).to_csv(OUT/'split/split-manifest.csv',index=False)
train.loc[~train.row_id.isin(clean.row_id)].to_csv(OUT/'excluded-train-rows.csv',index=False)
print('AUDIT',audit,flush=True)
X=pool.text.to_numpy();y=pool.category.to_numpy();xv=val.text.to_numpy();yv=val.category.to_numpy()
with threadpool_limits(limits=2):
 warnings.simplefilter('error',ConvergenceWarning)
 full=model().fit(X,y);pred=full.predict(xv);baseline=metrics(yv,pred)
 dummy=DummyClassifier(strategy='most_frequent').fit(np.zeros((len(y),1)),y)
 save('baseline.json',{'tfidf_logistic_regression':baseline,'most_frequent':metrics(yv,dummy.predict(np.zeros((len(yv),1)))),'evaluation_split':'validation','n_training':len(y),'features':len(full['tfidf'].vocabulary_)})
 pd.DataFrame(classification_report(yv,pred,labels=classes,output_dict=True,zero_division=0)).T.to_csv(OUT/'baseline-per-class.csv')
 val.assign(prediction=pred).to_csv(OUT/'validation-predictions.csv',index=False)
 joblib.dump(full,OUT/'baseline-model.joblib')
 print('BASELINE',baseline,flush=True)
 # Calibration is separate from the pool, validation and official test.
 conformal=SplitConformalClassifier(full,confidence_level=.9,conformity_score='lac',prefit=True).conformalize(cal.text.to_numpy(),cal.category.to_numpy())
 _,sets=conformal.predict_set(xv);sets=sets[:,:,0];labels=full.classes_;true_index=np.array([list(labels).index(v) for v in yv]);covered=sets[np.arange(len(yv)),true_index];sizes=sets.sum(axis=1);single=sizes==1
 c={'confidence_level':.9,'empirical_validation_coverage':float(covered.mean()),'mean_set_size':float(sizes.mean()),'singleton_rate':float(single.mean()),'singleton_error_rate':float((labels[sets[single].argmax(axis=1)]!=yv[single]).mean()) if single.any() else None,'empty_set_rate':float((sizes==0).mean()),'review_rate':float((sizes!=1).mean()),'minimum_class_coverage':float(min(covered[yv==c].mean() for c in classes)),'calibration_n':len(cal),'validation_n':len(val)}
 save('conformal.json',c);joblib.dump(conformal,OUT/'conformal-model.joblib');print('CONFORMAL',c,flush=True)
 if os.environ.get('FYP_BASELINE_ONLY')=='1':
  save('status.json',{'status':'complete','mode':'baseline-only','elapsed_seconds':round(time.time()-start,2),'fits_al':0,'official_test_evaluated':False})
  print('BASELINE_DEMO_READY',flush=True)
  raise SystemExit(0)
 rows=[];seeds=[17,29,43,53,71];budgets=[308,616,1232,2464]
 for seed in seeds:
  initial=np.random.default_rng(seed).choice(len(y),size=budgets[0],replace=False)
  for method in ['random','margin']:
   rng=np.random.default_rng(seed+1000);selected=list(initial);selection=[]
   for j,budget in enumerate(budgets):
    m=model().fit(X[selected],y[selected]);p=m.predict(xv);r={'seed':seed,'method':method,'budget':budget,'observed_classes':len(set(y[selected])),**metrics(yv,p)};rows.append(r)
    pd.DataFrame(rows).to_csv(OUT/'active-learning-runs.csv',index=False)
    selection.append({'budget':budget,'row_ids':pool.iloc[selected].row_id.tolist()})
    print('AL',r,flush=True)
    if j<len(budgets)-1:
     candidates=np.setdiff1d(np.arange(len(y)),selected);batch=budgets[j+1]-budget
     if method=='random':chosen=rng.choice(candidates,size=batch,replace=False)
     else:
      prob=m.predict_proba(X[candidates]);score=uncertainty_scores(prob,method='margin_sampling');order=np.lexsort((rng.random(len(score)),-score));chosen=candidates[order[:batch]]
     selected.extend(chosen.tolist())
   save(f'selection-{seed}-{method}.json',selection)
 frame=pd.DataFrame(rows);summary=frame.groupby(['method','budget'])[['accuracy','macro_f1']].agg(['mean','std']);summary.to_csv(OUT/'active-learning-summary.csv')
 pivot=frame.pivot(index=['seed','budget'],columns='method',values='macro_f1');delta=(pivot['margin']-pivot['random']).groupby('budget').agg(['mean','std','min','max']);delta.to_csv(OUT/'paired-differences.csv')
 save('design.json',{'seeds':seeds,'budgets':budgets,'initial_selection':'uniform random; shared by both arms within seed','query_batch_sizes':np.diff(budgets).tolist(),'features':'TF-IDF (1,2), min_df=2, sublinear_tf=True, max_features=20000; refitted on observed labels/text only at each step','classifier':'LogisticRegression C=1 max_iter=1000','query':'scikit-activeml uncertainty_scores margin_sampling; random tie-breaking','evaluation':'single fixed validation split; no official test metrics','annotation_cost':'budgets count training labels only; validation and calibration have additional fixed labels','scope':'offline pool-based simulation, not a human annotation study','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
 import importlib.metadata as im
 save('environment.json',{'python':platform.python_version(),'executable':os.sys.executable,'packages':{p:im.version(p) for p in ['numpy','pandas','scikit-learn','scikit-activeml','mapie','cleanlab']}})
 save('status.json',{'status':'complete','date':time.strftime('%Y-%m-%d'),'protocol_date':'2026-10-27','elapsed_seconds':round(time.time()-start,2),'fits_al':len(rows),'official_test_evaluated':False})
print('PILOT_COMPLETE',round(time.time()-start,2),flush=True)
