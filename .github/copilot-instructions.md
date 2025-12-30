# GitHub Copilot instructions — fiapmba

This repository is a small data-analysis project composed primarily of Jupyter notebooks and source datasets. The guidance below focuses on actionable, repository-specific conventions so an AI coding agent can be immediately productive.

1) Big picture
- Purpose: EDA and final analysis for a credit-risk exercise (QuantumFinance dataset). Primary work lives in `Python/Trabalho_final_v2.ipynb` and the `stat/` dataset folder.
- Structure: notebooks under `Python/`, raw data under `stat/`, top-level `requirements.txt` and `README.md` with venv instructions.

2) Key files to read before editing
- `Python/Trabalho_final_v2.ipynb` — main notebook; contains EDA code, plotting helpers, and target-detection heuristics.
- `stat/Base_ScoreCredito_QuantumFinance.csv` — local dataset; preserve original file when making changes.
- `requirements.txt` — install dependencies: `pip install -r requirements.txt` (see `README.md`).

3) Developer workflows (explicit)
- To run/notebook edits: create a venv, activate it, then install `requirements.txt` (see `README.md`). Ensure notebook kernel uses the venv Python executable.
- Do not modify raw CSV files in-place. Create derived files under a new `data/` or `outputs/` folder and commit those instead.

4) Project-specific patterns and gotchas
- Notebooks may read the same CSV in different ways (e.g. custom `sep` or `header=None`). When changing data-loading lines, keep encoding and separator considerations in mind.
- The main notebook contains logic that auto-detects the target column using heuristics (checks common names then falls back to low-cardinality columns). Preserve or carefully update this logic – it affects many downstream analyses.
- Visualizations use `matplotlib`, `seaborn` and helper functions in notebook cells; keep plotting changes self-contained to notebook cells to avoid breaking narrative flow.

5) Changes an AI agent should prefer
- Prefer edits that add modular helper functions or new notebook sections (clear Markdown headings) rather than large rewrites of existing analysis steps.
- When adding code files (scripts or modules), place them under a top-level `src/` or `notebook_helpers/` directory and update the notebook to import them.

6) Tests / CI / tooling
- There is no test suite or CI configured. Avoid introducing heavy infra; prefer lightweight, well-documented changes.

7) Committing and PR guidance
- Keep notebook outputs cleared when committing analytical changes unless outputs are intentionally part of results.
- Use descriptive commits like: `notebook: add EDA section for income vs default` or `data: add cleaned dataset derived from Base_ScoreCredito_QuantumFinance.csv`.

8) When in doubt — minimal safe edits
- If unsure about scoring/target logic, add a new notebook cell that computes an explicit `target_col` mapping and documents your choice, rather than changing earlier heuristic code in-place.

If any section is unclear or you want examples showing how to refactor parts of `Python/Trabalho_final_v2.ipynb`, tell me which part and I will update this file or create a small helper module and example notebook cell changes.
