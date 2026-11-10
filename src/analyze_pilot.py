"""Pool-only Cleanlab audit, plots and protocol checks after a full run."""
from pathlib import Path
import os,json, numpy as np,pandas as pd
from sklearn.model_selection import StratifiedKFold,cross_val_predict
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from cleanlab.filter import find_label_issues
from threadpoolctl import threadpool_limits
import joblib,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];O=Path(os.environ['FYP_OUTPUT_DIR'])
splits=pd.read_csv(O/'split/split-manifest.csv');pool=splits[splits.split=='pool'];val=splits[splits.split=='validation']
enc=LabelEncoder();y=enc.fit_transform(pool.category)
clf=make_pipeline(TfidfVectorizer(ngram_range=(1,2),min_df=2,sublinear_tf=True,max_features=20000),LogisticRegression(C=1,max_iter=1000,random_state=20261027))
with threadpool_limits(limits=2):
 probs=cross_val_predict(clf,pool.text,y,cv=StratifiedKFold(5,shuffle=True,random_state=20261027),method='predict_proba',n_jobs=1)
 ids=find_label_issues(y,probs,return_indices_ranked_by='self_confidence',n_jobs=1)
 reviewed=pool.iloc[ids[:50]].copy();reviewed['oof_prediction']=enc.inverse_transform(probs[ids[:50]].argmax(axis=1));reviewed['given_label_probability']=probs[ids[:50],y[ids[:50]]];reviewed['human_decision']='pending';reviewed.to_csv(O/'label-review-queue.csv',index=False)
 (O/'cleanlab-audit.json').write_text(json.dumps({'folds':5,'training_pool_n':len(pool),'flagged_candidates':len(ids),'exported_for_review':len(reviewed),'confirmed_label_errors':None,'labels_modified':0,'purpose':'diagnostic ranking only; low scores can reflect weak classifier or ambiguity','uses':'pool only; validation/calibration/test excluded'},indent=2),encoding='utf-8')
 print('Cleanlab audit:',len(ids),'candidates; 50 exported; no labels changed')
 model=joblib.load(O/'baseline-model.joblib');cp=joblib.load(O/'conformal-model.joblib');_,sets=cp.predict_set(val.text.to_numpy());sets=sets[:,:,0];truth=val.category.to_numpy();lookup={c:i for i,c in enumerate(model.classes_)};covered=sets[np.arange(len(val)),[lookup[c] for c in truth]]
 report=pd.DataFrame({'class':truth,'covered':covered}).groupby('class').agg(n=('covered','size'),coverage=('covered','mean')).sort_values('coverage');report.to_csv(O/'conformal-per-class.csv')
 print(report.head(5).to_string())
 frame=pd.read_csv(O/'active-learning-runs.csv');fig,ax=plt.subplots(figsize=(7,3.8))
 for method,color in [('random','#6d7783'),('margin','#126978')]:
  s=frame[frame.method==method].groupby('budget').macro_f1.agg(['mean','std']);ax.errorbar(s.index,s['mean'],yerr=s['std'],label=method.capitalize(),color=color,marker='o',capsize=3)
 ax.set(xlabel='Observed training labels (fixed holdout labels additional)',ylabel='Validation macro-F1',ylim=(0,1));ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(O/'learning-curve.png',dpi=180);plt.close(fig)
 tasks=[('Literature + scope','2026-10-27','2026-11-06'),('Pilot + proposal revision','2026-10-27','2026-11-13'),('Supervisor feedback + submit','2026-11-09','2026-11-20'),('Stronger baseline + repeat splits','2026-11-23','2026-12-18'),('Calibration + review policies','2026-12-14','2027-01-22'),('Prototype + optional label audit','2027-01-18','2027-02-19'),('Freeze protocol + final test','2027-02-22','2027-03-12'),('Analysis + dissertation draft','2027-03-08','2027-04-09'),('Revision + submission buffer','2027-04-12','2027-04-30')]
 pd.DataFrame(tasks,columns=['task','start','finish']).to_csv(O/'work-plan.csv',index=False)
 import matplotlib.dates as mdates
 fig,ax=plt.subplots(figsize=(7.4,4.3))
 for i,(label,a,b) in enumerate(tasks):
  a=pd.Timestamp(a);b=pd.Timestamp(b);ax.barh(i,(b-a).days,left=mdates.date2num(a),color='#20677b')
 ax.set_yticks(range(len(tasks)),[x[0] for x in tasks],fontsize=8);ax.invert_yaxis();ax.xaxis.set_major_locator(mdates.MonthLocator());ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'));ax.grid(axis='x',alpha=.2)
 for deadline in ['2026-11-20','2027-04-30']: ax.axvline(mdates.date2num(pd.Timestamp(deadline)),color='#aa3e3e',linestyle='--',linewidth=1)
 fig.tight_layout();fig.savefig(O/'gantt.png',dpi=180);plt.close(fig)
 for seed,g in frame.groupby('seed'):
  assert len(g)==8
  assert g[g.budget==308].macro_f1.nunique()==1
  for method in ['random','margin']:
   selections=json.loads((O/f'selection-{seed}-{method}.json').read_text());previous=set()
   for s in selections:
    ids=set(s['row_ids']);assert len(ids)==s['budget'] and previous<=ids and ids<=set(pool.row_id);previous=ids
 assert len(frame)==40
 (O/'verification.json').write_text(json.dumps({'status':'passed','checks':['40 planned active-learning fits present','paired arms share initial metric per seed','all selected IDs belong only to training pool','selection nested, unique and budget-correct','split overlap assertions passed during pilot','convergence warnings treated as errors during pilot'],'limitations':['no near-duplicate semantic audit','one split only','no official test evaluation']},indent=2),encoding='utf-8')
 print('VERIFY_COMPLETE')
