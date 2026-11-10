# BANKING77 attribution and provenance

Source: PolyAI, `task-specific-datasets`, `banking_data/`, pinned commit [57ec275d8078af65b7731c2a98be812d844a6d6b](https://github.com/PolyAI-LDN/task-specific-datasets/tree/57ec275d8078af65b7731c2a98be812d844a6d6b/banking_data).

Original dataset: I. Casanueva, T. Temčinas, D. Gerz, M. Henderson and I. Vulić, “Efficient Intent Detection with Dual Sentence Encoders,” NLP for Conversational AI, 2020, pp. 38–45. [Paper and citation](https://aclanthology.org/2020.nlp4convai-1.5/).

Licence: **Creative Commons Attribution 4.0 International**, full original text at `raw/LICENSE`. The repository-root source README is preserved as `raw/README.md`; BANKING77 is its banking-data subset. Raw CSV/JSON files are byte-identical to the pinned upstream download. SHA-256 values and source URLs are in `source-manifest.json`.

- Raw: 10,003 training rows, 3,080 official test rows, 77 intents.
- Derived: NFKC + casefold + whitespace normalisation for overlap/duplicate auditing; four duplicate training rows and seven training-side cross-split overlaps excluded, giving 9,992 usable training rows.
- Derived split: seed 20261027; 6,994 training-pool, 1,499 validation and 1,499 calibration rows. `processed/split-manifest.csv` includes original text, labels, row IDs and split membership.
- `reference_results/` and generated outputs contain derived predictions/selection records and, in some CSVs, source text. Transformations are project-specific, not modifications to the upstream raw files.

The official test texts are used only to audit exact normalised overlap; test performance is deliberately not reported. No private customer records are included.
