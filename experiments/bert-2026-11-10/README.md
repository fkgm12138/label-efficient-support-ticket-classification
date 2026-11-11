# BERT comparison on BANKING77

The 10 November 2026 experiment compares fine-tuned BERT with the existing TF-IDF and logistic regression baseline. Both models use the repository's [fixed data split](../../data/processed/split-manifest.csv), with 6,994 training-pool queries, 1,499 validation queries and 1,499 calibration queries. The official test set is reserved for final evaluation.

## Full training pool

| Metric | TF-IDF + logistic regression | BERT-base |
|---|---:|---:|
| Validation accuracy | 84.86% | 90.93% |
| Validation macro-F1 | 0.8388 | 0.9035 |
| Conformal set coverage | 89.66% | 88.46% |
| Simulated referral rate | 42.90% | 5.94% |
| Error among singleton sets | 5.61% | 5.96% |

Each model is calibrated separately on the same calibration queries at a nominal 90% coverage level. The simulated policy flags empty sets and sets with multiple candidate intents. BERT flags fewer cases and has lower empirical coverage and slightly higher singleton error. The two policies operate at different error rates. Measuring review time would require a human study.

## Low training-label budgets

| Training labels | TF-IDF + LR random | TF-IDF + LR margin | BERT random | BERT margin |
|---:|---:|---:|---:|---:|
| 308 | 0.1805 | 0.1805 | 0.0260 | 0.0260 |
| 616 | 0.3413 | 0.3613 | 0.0934 | 0.0907 |
| 1,232 | 0.5327 | 0.5679 | 0.3542 | 0.3814 |
| 2,464 | 0.7025 | 0.7163 | 0.6736 | 0.6663 |

Values are mean validation macro-F1 over five paired acquisition seeds on one fixed partition. Within each seed, both models start with the same 308 labelled queries and use the same random selections. Margin selections can diverge because they depend on the model's probabilities. The table counts training labels. Validation and calibration use an additional 2,998 labels. Under the recorded training settings, TF-IDF + logistic regression has higher mean macro-F1 at all four low-label budgets. Margin sampling improves BERT at 1,232 labels and performs worse than random sampling at 616 and 2,464 labels.

## Training and verification

BERT was fine-tuned from [google-bert/bert-base-uncased](https://huggingface.co/google-bert/bert-base-uncased/tree/86b5e0934494bd15c9632b12f734a8a67f723594), with 5 epochs per fit, a learning rate of 0.00004, a batch size of 16, 2 accumulation steps and a maximum input length of 128 tokens. The recorded full-pool fit took 147.50 seconds on an NVIDIA GeForce RTX 4070 Laptop GPU using BF16. The saved-output checks covered 41 distinct training jobs, including 35 acquisition fits underlying 40 BERT records. A fit at the initial budget is shared by both sampling strategies in each seed.

The BERT Cleanlab audit flagged 159 training labels for review and exported 50 candidates locally. Confirming label errors requires adjudication. The labels were kept unchanged. Planned work includes repeated partitions, calibration of the low-budget models and a comparison with a confidence-threshold policy.

## Saved results

- [Full-pool model comparison](model-comparison.csv)
- [Active learning summary](all-model-active-learning-summary.csv) and [results by seed](all-model-active-learning-runs.csv)
- BERT [baseline](baseline.json), [conformal results](conformal.json) and [coverage by intent](conformal-per-class.csv)
- [BERT label audit summary](cleanlab-audit.json)
- [Training configuration](config.json) and [saved-output verification](independent-verification.json)

The repository's CPU quick start runs the lexical baseline and demo. This directory documents the separate GPU experiment and publishes its saved results.
