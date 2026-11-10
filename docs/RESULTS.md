# Existing pilot evidence and unresolved questions

These are the saved pilot results on one fixed validation partition, not new external validation. See `evidence/release-validation.json` for what was rerun during packaging.

| Quantity | Existing result | Interpretation |
|---|---:|---|
| Full-pool validation accuracy |0.8485657105|1,272/1,499 correct;227 errors|
| Full-pool validation macro-F1 |0.8387990495|77-class mean, validation only|
| Most-frequent baseline accuracy |0.0186791194|Weak reference baseline|
| Nominal conformal level |0.90|Marginal target under assumptions|
| Empirical validation coverage |0.8965977318|1,344/1,499 true labels in sets|
| Singletons |856/1,499 (57.10%)|48 incorrect singleton suggestions|
| Singleton error |48/856 (5.61%)|Not guaranteed by nominal90% coverage|
| Referrals |643/1,499 (42.90%)|Empty or multi-label sets|
| Empty sets |70/1,499|No candidate under current threshold|
| Cleanlab candidates |322|Not confirmed errors|
| Review queue |50 pending|Labels modified:0|

| Training-label count | Random mean macro-F1 | Margin mean macro-F1 | Paired mean difference | Seeds where margin is worse |
|---:|---:|---:|---:|---:|
|308|0.1805|0.1805|0|0|
|616|0.3413|0.3613|+0.0200|2|
|1,232|0.5327|0.5679|+0.0352|1|
|2,464|0.7025|0.7163|+0.0137|1|

Error bars on `learning-curve.png` are **standard deviations across five seeds**, not confidence intervals or variation across independent data partitions. One seed's gain at1,232 labels was negative. The full-pool and low-budget models use different amounts of training data; the figure does not establish equal performance at lower total cost.

## What still needs experiments

- Repeat the acquisition comparison across predeclared data partitions, add justified stronger baselines and uncertainty estimates.
- Account for all labels:1,232 training+1,499 validation+1,499 calibration=4,230 development labels, before any new label-review work. Real annotation time/cost has not been measured.
- Rebuild low-budget checkpoints from query IDs, handle probability alignment/unseen classes, calibrate independently and compare confidence and conformal referral policies at comparable acceptance rates.
- Check class imbalance, sparse per-class coverage and sensitivity to noise/overlap. The observed worst class coverage1/5 is unstable.
- Adjudicate label-review candidates with recorded decisions before making correction claims; keep this separate from validation misclassification analysis.
- Define any real service-department mapping, human handling process and evaluation before claiming deployment routing.
- Freeze the final protocol before a one-off official test evaluation.

The local web interface added for demonstration is not evidence that these research questions are solved. Code execution establishes operational reproducibility, not originality, supervisor endorsement or a guaranteed assessment result.
