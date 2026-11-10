# Label-Efficient Customer Support Ticket Classification with Artificial Intelligence

Reproducible, CPU-based research experiments on **BANKING77**: TF-IDF + logistic regression, pool-based active learning with **scikit-activeml**, split conformal prediction with **MAPIE**, and training-label diagnostics with **Cleanlab**.

**中文使用说明：[安装与演示手册](docs/DEMO_zh.md) · [代码逐项说明](docs/CODE_MAP_zh.md) · [实验方法](docs/METHODS.md) · [结果与局限](docs/RESULTS.md)**

This repository contains research code and a local illustrative interface. The current experiments classify banking intents. Deployment routing to real service departments is outside the implemented scope. No external AI API or GPU is required.

## Quick start (Windows PowerShell, Python 3.12 x64)

Place the clone on drive D:. These examples use a new project folder; preserve any existing folder before cloning.

```powershell
Set-Location D:\CodexWork
 git clone https://github.com/fkgm12138/label-efficient-support-ticket-classification.git
Set-Location .\label-efficient-support-ticket-classification
& D:\anaconda\python.exe bootstrap.py
& .\.venv\Scripts\python.exe verify_results.py
& .\.venv\Scripts\python.exe run.py --mode baseline --output outputs/demo-01
& .\.venv\Scripts\python.exe demo.py --models outputs/demo-01 --web
```

Open **http://127.0.0.1:8765**. Stop the server with `Ctrl+C`. If your Python 3.12 is elsewhere, replace only the bootstrap interpreter path; all later commands explicitly use `.venv`. `py -3.12 bootstrap.py` is another option if Python Launcher is installed. The online installer needs PyPI access. An offline wheelhouse is supported, but wheels and Python itself are not committed.

## Three ways to run

| Purpose | Command using the project Python | What happens |
|---|---|---|
| Check saved evidence | `python verify_results.py` | Checks raw hashes, split separation, saved baseline metrics and query IDs; no training |
| Prepare an interactive demo | `python run.py --mode baseline --output outputs/demo-01` | Rebuilds the fixed split, fits 6,994-label baseline, calibrates on 1,499 labels, validates on 1,499; skips acquisition/Cleanlab |
| Reproduce all pilot experiments | `python run.py --mode full --output outputs/full-01` | Baseline, conformal prediction, 40 acquisition fits, 5-fold Cleanlab audit, plots and checks |

In this table, `python` means **`.venv/Scripts/python.exe` on Windows**, not a random system Python. Choose a **new output folder** each time: the runner refuses non-empty output folders. Runtimes depend on the machine; use baseline mode for a meeting rather than waiting for the full experiment.

CLI prediction:

```powershell
& .\.venv\Scripts\python.exe demo.py --models outputs/demo-01 --text "I lost my bank card. How can I freeze it?"
```

The browser demo and CLI load only locally generated model files. Do not load untrusted `joblib`/pickle files. The web server binds to localhost, does not persist entered ticket text, and has no production authentication, department mapping or out-of-domain detection.

## Repository contents

- `src/run_pilot.py`: deduplication, split, baseline, conformal calibration and active-learning loops.
- `src/analyze_pilot.py`: training-only out-of-fold label audit, plots and acquisition checks.
- `run.py`, `bootstrap.py`: safe output handling and local installation.
- `verify_results.py`: consistency checks against actual saved records.
- `demo.py`, `demo/index.html`: CLI and local web demonstration.
- `data/raw/`: source data, original README and CC BY 4.0 licence.
- `data/processed/split-manifest.csv`: fixed reference partition, not a second dataset.
- `reference_results/`: historical pilot evidence, including all 40 scores, query IDs and review queue; trained models are regenerated locally.
- `tests/`: demo-contract and HTTP integration checks.
- `docs/`: demonstration script, methods, evidence boundaries and file guide.
- `evidence/`: release validation and file hashes.

## Evidence boundary

On the single fixed validation split, the existing full-pool baseline reached **84.86% accuracy / 0.8388 macro-F1**. At 1,232 **training** labels, mean margin acquisition macro-F1 was **0.5679**, compared with **0.5327** for random acquisition across five seeds. The 2,998 validation/calibration labels are additional. This does not establish a reduction in total annotation cost. Active learning did not win in every seed.

The full-pool conformal pilot had **89.66% marginal coverage**, **42.90% referral**, and **5.61% error among singleton sets**. The low-budget active-learning models have not been integrated with this policy. The official test set has not been scored. Cleanlab flagged **322 candidates**, of which **50 are pending review**; none is a confirmed label error.

## Data, software and assistance

BANKING77 is redistributed unchanged from PolyAI-LDN/task-specific-datasets commit `57ec275d8078af65b7731c2a98be812d844a6d6b`, under **CC BY 4.0**. See [data attribution](data/README.md), original licence and SHA-256 manifest. Derived splits/prediction records retain BANKING77 text. This repository does not apply a new open-source licence to the project code; public visibility alone grants no additional reuse licence. Third-party libraries retain their own licences and are installed as dependencies.

Code, packaging and documentation were prepared with AI assistance. This is not evidence that a student independently implemented or understood every component. The installed scikit-learn procedural Skill supported pipeline and evaluation checks; its source is acknowledged in [references](docs/REFERENCES.md). Publication of this repository is not supervisor approval or a novelty claim.
