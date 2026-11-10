# Experimental protocol

## Data and isolation

BANKING77 has 10,003 released training examples, 3,080 official test examples and 77 intent classes. Normalisation for duplicate auditing is NFKC, casefold and whitespace collapse; punctuation is retained. Four normalised duplicate training rows and seven training-side overlaps with test text are removed. No conflicting training labels were found. The remaining 9,992 examples are split using stratified `train_test_split` with seed 20261027: first 70/30, then the held-out 30% in half, yielding pool 6,994 / validation 1,499 / calibration 1,499. The official test text is checked for overlap but not scored. Semantic near-duplicate analysis remains unimplemented.

## Baseline

A scikit-learn Pipeline fits word TF-IDF (unigrams/bigrams, `min_df=2`, `sublinear_tf=True`, maximum20,000 features) and logistic regression (`C=1`, `max_iter=1000`, seed20261027). TF-IDF is refitted using only the labelled training text at each acquisition checkpoint. The full-pool model has 8,096 features. Validation macro-F1 uses all77 class names, including absent training classes; no official test score is computed.

## Active learning

Five seeds:17,29,43,53,71. Budgets:308,616,1232,2464. Each seed uses one identical uniform random308-example initial set for both arms. Random acquisition samples uniformly without replacement. Margin acquisition calls the public scikit-activeml `uncertainty_scores(..., method='margin_sampling')`, selecting the most uncertain scores with random tie-breaking. Each checkpoint refits the Pipeline. Released benchmark labels are revealed to simulate annotation; no humans are timed. Some initial subsets miss classes. Probabilities are over the model's observed classes; the existing full-pool conformal pilot is separate, not a low-budget policy.

## Prediction sets

The full-pool classifier is calibrated on the independent1,499-example calibration split using MAPIE SplitConformalClassifier, LAC, `prefit=True`, confidence level0.9. Report marginal validation coverage, mean set size, empty/singleton rates, singleton error and per-class coverage. The illustrative policy accepts a singleton suggestion and refers empty or multi-label sets. Marginal coverage is not singleton accuracy or a per-class guarantee. The local demo follows this rule but does not create a human task or send a ticket to a service department.

## Label-quality audit

Within the6,994-example training pool only, a five-fold shuffled stratified cross-validation (seed20261027) produces out-of-fold probabilities. TF-IDF is inside the Pipeline, so each held-out fold is excluded from feature fitting. Cleanlab ranks candidate issues by self-confidence; top50 are exported as pending. No labels are corrected. A candidate may reflect classifier weakness or ambiguity rather than a true annotation mistake.

## Verification and provenance

The release preserves the original experiment settings. Refactoring is limited to project-local caches, new output directories, orchestration, independent consistency checks and the demonstration interface. `reference_results` contains historical records. Reproduction creates a separate `outputs/<run>` folder; state and step exit codes are logged. Selection records are retained, but active-learning checkpoint weights are not all persisted. The browser examples are illustrative inputs, not a newly labelled evaluation set.
