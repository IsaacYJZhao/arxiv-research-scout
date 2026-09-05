# arXiv Research Scout

A portable research-monitoring pipeline for discovering relevant arXiv papers, extracting evidence from PDFs, analyzing papers with an LLM, and generating structured literature reports and multi-paper research digests.

The project is designed for both local execution and unattended GitHub Actions workflows.

## Features

* Search arXiv and Europe PMC from one configurable topic.
* Recognize the same paper arriving from more than one source and analyze it once.
* Prefer papers whose full text can actually be downloaded when slots are limited.
* Filter papers by publication window.
* Deduplicate arXiv versions by normalized paper ID.
* Skip papers that have already been successfully processed.
* Rank papers using configurable relevance rules.
* Download arXiv PDFs directly into memory.
* Extract text from PDFs without storing PDF files in the repository.
* Parse major paper sections: Abstract, Introduction, Related Work, Methodology, Experiments, Results, Discussion, and Conclusion.
* Fall back to the arXiv abstract when PDF processing fails.
* Generate structured analyses with Methodology, Evaluation, Innovation, Datasets, Metrics, Key Results, Limitations, Evidence Level, and Confidence.
* Support DeepSeek and OpenAI at runtime.
* Use DeepSeek as the default provider, with runtime provider/model override support.
* Generate one Markdown report per successfully analyzed paper.
* Generate one multi-paper Markdown digest for each completed research run.
* Persist processed arXiv IDs and successful-run timestamps.
* Run automatically through GitHub Actions.
* Sync GitHub Actions results back to the local machine and raise a desktop notification (`notify_bridge.py`).
* Avoid unnecessary LLM calls when no paper requires analysis.

## Architecture

```text
arXiv
  |
  v
Retrieval
  |
  v
Date filtering
  |
  v
ID deduplication
  |
  v
Processed-paper filtering
  |
  v
Relevance ranking
  |
  v
Selected papers
  |
  +-----------------------------+
  |                             |
  v                             v
PDF available                PDF unavailable
  |                             |
  v                             v
PDF extraction              arXiv abstract
  |                             |
  v                             |
Section parsing                 |
  |                             |
  +-------------+---------------+
                |
                v
        Analysis Context
                |
                v
        DeepSeek / OpenAI
                |
                v
      Structured Analysis
                |
                v
       Per-paper Markdown
                |
                v
          Batch Processing
                |
                v
        Research Digest
                |
                v
        Run-level State
```

## Requirements

* Python 3.11
* Git
* Internet access for arXiv retrieval
* An API key for the selected LLM provider when papers require analysis

The project is tested on Windows and Ubuntu through GitHub Actions.

## Installation

Clone the repository:

```bash
git clone https://github.com/IsaacYJZhao/arxiv-research-scout.git
cd arxiv-research-scout
```

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest
```

### Linux / macOS

```bash
python3.11 -m venv .venv
./.venv/bin/python -m pip install -e ".[dev]"
./.venv/bin/python -m pytest
```

## API Keys

API keys are read only from environment variables. Do not store real credentials in source code, `config/scout.yaml`, README files, or Git commits.

Supported variables:

```text
DEEPSEEK_API_KEY
OPENAI_API_KEY
```

The repository includes `.env.example` only as documentation:

```text
OPENAI_API_KEY=your_openai_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### PowerShell

```powershell
$env:DEEPSEEK_API_KEY = "<your-key>"
$env:OPENAI_API_KEY = "<your-key>"
```

### Linux / macOS

```bash
export DEEPSEEK_API_KEY="<your-key>"
export OPENAI_API_KEY="<your-key>"
```

Only the key for the provider actually used is required.

## LLM Providers

The default provider is configured in `config/scout.yaml`:

```yaml
llm:
  default_provider: "deepseek"
```

Inspect the active provider:

```powershell
.\.venv\Scripts\arxiv-scout.exe provider
```

Temporarily switch to OpenAI:

```bash
arxiv-scout provider --provider openai
```

A command-line override affects only the current execution and does not modify `config/scout.yaml`.

## Commands

The primary CLI is `arxiv-scout` with four commands:

```text
scan
run
analyze-paper
provider
```

### Scan arXiv

```bash
arxiv-scout scan
arxiv-scout scan --force
```

`scan` previews retrieval/relevance results. It does not analyze papers, does not consume API credits, and does not update persistent state. Use it after changing `config/scout.yaml` to confirm that the query and the relevance rules select the papers you expect.

### Run the Complete Pipeline

```bash
arxiv-scout run
```

Pipeline:

```text
arXiv scan
-> filtering
-> relevance ranking
-> PDF processing
-> LLM analysis
-> paper reports
-> research digest
-> state update
```

Force a run even when the configured interval has not elapsed:

```bash
arxiv-scout run --force
```

Use OpenAI for one run:

```bash
arxiv-scout run --provider openai
```

Override provider and model:

```bash
arxiv-scout run --provider openai --model <model-id>
```

### Analyze One Specific Paper

Analyze one paper without modifying scheduled-run state:

```bash
arxiv-scout analyze-paper 2608.16855v1
```

Use OpenAI for that paper:

```bash
arxiv-scout analyze-paper 2608.16855v1 --provider openai
```

Manual reports are written under:

```text
reports/manual/<provider>/
```

`reports/manual/` is ignored by Git because it is intended for local testing and provider comparison.

## Retrieval Sources

Two sources are queried per run, in this order:

```text
arXiv        preprints, mostly cs.CV / eess.IV / cs.LG
Europe PMC   journal articles, PubMed records, preprints
```

Order matters. Results are concatenated and then deduplicated keeping the first occurrence, and an arXiv preprint usually has a downloadable PDF while the journal record of the same work often does not. A full text produces a far stronger analysis than an abstract, so the preprint should win.

Europe PMC is what makes the scout usable for a medical imaging topic. For 3D CT lung nodule detection over the same two-week window, arXiv returned one candidate and Europe PMC returned ten, including work published in imaging journals that never appears on arXiv at all.

### Why each source keeps its own query

The query languages differ, and translating between them loses precision, so `config/scout.yaml` holds one query per source:

```yaml
topic:
  arxiv_query: >
    (all:"lung nodule" OR all:"pulmonary nodule") AND ...

sources:
  europepmc:
    enabled: true
    max_candidates: 50
    query: >
      (TITLE_ABS:"lung nodule" OR TITLE_ABS:"pulmonary nodule")
      AND (TITLE_ABS:"deep learning" OR TITLE_ABS:"computed tomography")
```

The publication window is added to the Europe PMC query automatically from `schedule.lookback_days`. It has to be applied server-side: Europe PMC sorts by relevance by default and holds tens of millions of records, so filtering by date only after retrieval would return mostly old work.

Setting `enabled: false`, or removing the `sources` block entirely, falls back to arXiv alone.

### Cross-source identity

Papers are identified by a key rather than by an arXiv ID:

```text
doi:10.1007/s10278-026-02237-y
arxiv:2608.16855
europepmc:42675277
```

A DOI wins when one exists, because that is what an arXiv preprint and its published journal version have in common. Europe PMC reports the DataCite DOI of arXiv preprints (`10.48550/arXiv.2608.16855`); those map back to the `arxiv:` key, so a preprint indexed by both sources is one paper, not two.

### Closed-access articles

Most journal articles indexed by Europe PMC are paywalled. They are still retrieved, ranked and analyzed, but only from their abstract, and their report says so:

```text
- **PDF status:** No full text available; abstract only
- **Evidence level:** abstract_only
```

Knowing that a paper exists is what matters for a literature review; the full text can be obtained separately. When more papers pass relevance than `retrieval.max_papers` allows, full-text-available papers take the slots first.

### Adding another source

Each source is one module under `src/arxiv_research_scout/sources/` that returns `PaperRecord` objects. Nothing downstream knows which database a paper came from. To add one:

1. Write the adapter module and its query translation.
2. Register it in `runner.collect_candidates()`.
3. Add its block to `sources:` in `config/scout.yaml`.

A source that fails is recorded in the digest and skipped, not raised. Losing one source degrades a run; aborting the run loses the papers every other source found.

## Where Results Live

This is the part that most often causes confusion, so it is worth stating explicitly.

**GitHub Actions runs do not write to your local disk.** A scheduled run happens on GitHub's runner and commits its output back to the repository:

```text
.state/state.json
reports/<arxiv-id>.md
reports/digests/<date>.md
```

Those files exist on GitHub immediately. They appear on your own machine only after the repository is pulled:

```bash
git pull --rebase origin main
```

Until you pull, your local `reports/` and `.state/state.json` reflect the last time *you* synced, not the last time the pipeline ran. If a digest is missing locally but visible on GitHub, this is the reason.

`notify_bridge.py` (below) automates that pull, so in normal use you never have to remember it.

## Desktop Notifications (`notify_bridge.py`)

`notify_bridge.py` sits at the repository root and bridges research results into a desktop-pet notification inbox. It reads only public artifacts (`.state/state.json` and `reports/`) and does not import project internals, so it survives most upgrades of this project.

### Sync mode (default, recommended)

```bash
python notify_bridge.py
```

1. `git fetch` and check whether the remote has new bot commits.
2. If not, exit quietly without notifying.
3. If yes, fast-forward merge — this is what brings the reports and digests onto local disk.
4. Diff `processed_ids` before and after the merge; the difference is the set of papers analyzed in that run.
5. Emit one notification pointing at the first new report, falling back to the newest digest.

Retrieval itself runs in GitHub Actions. Your machine can be switched off in the meantime; the first run after boot catches up. Because only one scheduler owns `.state/state.json`, local and remote state cannot diverge.

By default no notification is sent when a cloud run selected no papers. Pass `--notify-empty` if you would rather receive a heartbeat:

```bash
python notify_bridge.py --notify-empty
```

If the working tree has uncommitted changes, the fast-forward cannot proceed. Rather than failing silently, the script sends a "sync blocked" notification so an unsynced state is never mistaken for "no new papers".

### Local mode (fallback / offline)

```bash
python notify_bridge.py --local
python notify_bridge.py --local --force
```

Runs the full pipeline locally, exactly as older versions of this script did. It requires a local API key and it writes local `.state/state.json`. Commit and push afterwards, otherwise the next GitHub Actions run will hit a rebase conflict on the state file.

### Windows Task Scheduler

Point the scheduled task at `notify_bridge.py` rather than at `arxiv-scout run`. Sync mode is cheap — a `git fetch` with no new commits costs nothing — so scheduling it daily, or at logon, is reasonable regardless of `run_every_days`.

## Configuration

Main configuration file:

```text
config/scout.yaml
```

Important sections:

```yaml
topic:
  name: "3D CT Lung Nodule Detection"
  arxiv_query: >
    ...
  categories:
    - "cs.CV"
    - "eess.IV"
    - "cs.LG"

sources:
  arxiv:
    enabled: true
  europepmc:
    enabled: true
    max_candidates: 50
    query: >
      ...

schedule:
  run_every_days: 3
  lookback_days: 14

retrieval:
  # arXiv only; Europe PMC has its own max_candidates.
  max_candidates: 100
  max_papers: 8

pdf:
  max_download_mb: 50
  max_text_chars: 70000
  timeout_seconds: 90
  max_attempts: 3

llm:
  default_provider: "deepseek"

relevance:
  min_score: 4
  high_score: 8
  require_core: true

output:
  language: "zh-CN"
  reports_dir: "reports"

state:
  file: ".state/state.json"
```

### Scheduling

`run_every_days` controls how often a full research scan is due. GitHub Actions wakes up more frequently than that; the Python application checks `.state/state.json` before doing any research work, so a daily wake-up does not imply a daily LLM API call.

### Choosing `lookback_days`

`lookback_days` is the publication window applied after retrieval. It must be large enough that a topic actually produces papers inside it.

For a narrow topic this matters more than it looks. The default configuration monitors 3D CT lung nodule detection, which publishes roughly two to three matching preprints per month — a five-day window returns nothing on most runs. `lookback_days` is therefore set well above `run_every_days`; papers already analyzed are filtered out by `processed_ids`, so an overlapping window costs nothing.

`retrieval.max_candidates` must be raised alongside it. The arXiv response is truncated at that value *before* date filtering, so too small a value can silently cut off the window.

## Relevance Filtering

Rule-based scoring runs before any PDF download or LLM call, which is what keeps API usage low.

Term groups and their weights:

```text
core_terms          title +4   abstract +2
target_terms        title +5   abstract +3
supporting_terms    title +2   abstract +1
deprioritize_terms  title -1   abstract  0
```

Admission uses two independent gates:

* `require_core` — when true, a paper must match at least one core term. This is the topic gate: it decides whether the paper is about the subject at all.
* `min_score` — removes papers that only mention the subject in passing.

`deprioritize_terms` take part in neither gate. They express a reading preference and only push a paper down the ranking; the total score is clamped at zero so that stacked penalties cannot drive a paper below the threshold.

This separation is deliberate. Treating deprioritized terms as a veto is what makes a scout silently return nothing: in this field almost every recent title contains "segmentation", so a large title penalty combined with a high `min_score` rejects on-topic work — including papers built on LUNA16, LNDb, and LIDC-IDRI.

Note that term matching is word-boundary aware and treats `-` as a boundary, so `LIDC` also matches `LIDC-IDRI`, and `CAD` does not match `cascade`.

## Evidence-Grounded Analysis

The analyzer is designed to reduce hallucination. It is instructed to use only evidence supplied from arXiv metadata, extracted PDF text, and parsed paper sections.

It must not invent unsupported:

* datasets
* sample sizes
* patient/scan/nodule counts
* train/validation/test splits
* architecture details
* preprocessing procedures
* training strategies
* optimizers
* learning rates
* epochs
* loss functions
* parameter counts
* inference times
* baselines
* ablation studies
* metrics
* statistical tests
* numerical results

When evidence is unavailable, the analysis should explicitly state that the information was not reported or could not be determined from the available evidence.

## Evidence Levels

Typical values:

```text
full_text
partial_text
abstract_only
```

Evidence level is determined by local code rather than by the LLM.

## Reports

### Per-paper Reports

Reports are named after the record key, so papers from different databases cannot collide:

```text
reports/arxiv_2608.14766.md
reports/europepmc_42675277.md
```

Successfully processed papers produce Markdown reports containing:

```text
Paper Information
Analysis Information
Methodology
Evaluation
Innovation
Datasets
Metrics
Key Results
Limitations
```

### Research Digests

Completed runs generate a digest under:

```text
reports/digests/
```

Example:

```text
reports/digests/2026-08-31.md
```

A digest contains provider/model information, run status, retrieval statistics, successful/failed counts, and structured summaries for each successfully analyzed paper.

Digest generation is performed locally from already structured analyses and does not require an additional LLM call.

A digest is written even when no paper was selected. Its retrieval statistics are the fastest way to tell *why* a run was empty — whether the query returned nothing, the date window rejected everything, or the relevance rules did.

## State Management

Persistent state is stored in:

```text
.state/state.json
```

Example:

```json
{
  "schema_version": 2,
  "last_successful_run_utc": null,
  "processed_ids": ["arxiv:2608.12345", "doi:10.1007/s10278-1"]
}
```

`processed_ids` holds the cross-source keys described under Retrieval Sources. arXiv version suffixes are normalized, so `2608.12345v1`, `2608.12345v2`, and `2608.12345v3` are the same paper.

Schema 1 stored bare arXiv IDs. `load_state()` migrates those to `arxiv:` keys automatically and idempotently, so an existing state file keeps working and already-analyzed papers are not analyzed again.

This file must have exactly one writer. Running the pipeline both locally and in GitHub Actions makes the two copies diverge, which surfaces later as a rebase conflict on `state.json` or as papers analyzed twice. Pick one scheduler; see the `notify_bridge.py` section above.

## Transaction Semantics

The project deliberately separates paper-level success from run-level success.

For one paper:

```text
analysis succeeds
-> report succeeds
-> processed ID is persisted
```

For one complete scheduled run:

```text
selected papers processed
-> digest successfully written
-> no unresolved paper failures
-> last_successful_run_utc updated
```

If one paper fails:

```text
successful papers remain processed
failed paper remains unprocessed
partial digest may still be generated
run timestamp is not updated
```

If digest generation fails:

```text
successfully processed paper IDs remain valid
run timestamp is not updated
```

This allows failed work to be retried without unnecessarily repeating successful analyses.

## GitHub Actions

Workflow file:

```text
.github/workflows/research-scout.yml
```

The workflow supports:

* manual execution through `workflow_dispatch`
* scheduled execution through GitHub Actions cron
* Python 3.11 setup
* dependency installation
* full test-suite execution
* automatic research-scout execution
* automatic commit/push of generated state and reports
* concurrency protection

The workflow wakes up once per day. The application itself checks:

```yaml
schedule:
  run_every_days: 3
```

before performing a full research scan.

### Required GitHub Secret

For the default DeepSeek provider, configure:

```text
DEEPSEEK_API_KEY
```

In the GitHub repository:

```text
Settings
-> Secrets and variables
-> Actions
-> New repository secret
```

If scheduled runs are later configured to use OpenAI, also add `OPENAI_API_KEY`.

### Output Persistence

When a scheduled run produces changes, GitHub Actions automatically commits:

```text
.state/state.json
reports/
```

using the GitHub Actions bot account. If no generated files change, no commit is created.

### Operational Notes

* GitHub Actions cron fires late under load, sometimes by hours. Because `last_successful_run_utc` records the completion time, that delay carries into the next interval, so the observed cadence can drift from three days toward four.
* GitHub disables scheduled workflows in repositories with no activity for 60 days, and commits made by `github-actions[bot]` do not reset that clock. Trigger a `workflow_dispatch` run or push a commit occasionally to keep the schedule alive.
* The test suite runs before the scout step. A test failure therefore also skips that day's retrieval.

## Project Structure

```text
arxiv-research-scout/
├── .github/
│   └── workflows/
│       └── research-scout.yml
├── .state/
│   └── state.json
├── config/
│   └── scout.yaml
├── reports/
│   ├── .gitkeep
│   └── digests/
├── skills/
│   └── arxiv-paper-scout/
│       ├── SKILL.md
│       └── references/
├── src/
│   └── arxiv_research_scout/
│       ├── __init__.py
│       ├── analysis_context.py
│       ├── analysis_schema.py
│       ├── analyzer.py
│       ├── arxiv_client.py
│       ├── batch_processor.py
│       ├── cli.py
│       ├── config.py
│       ├── digest_writer.py
│       ├── llm_provider.py
│       ├── manual_analysis.py
│       ├── models.py
│       ├── paper_filters.py
│       ├── paper_lookup.py
│       ├── paper_processor.py
│       ├── paper_transaction.py
│       ├── paths.py
│       ├── pdf_reader.py
│       ├── relevance.py
│       ├── report_writer.py
│       ├── runner.py
│       ├── section_parser.py
│       ├── sources/
│       │   ├── __init__.py
│       │   └── europepmc.py
│       ├── state_manager.py
│       └── workflow.py
├── tests/
├── .env.example
├── .gitattributes
├── .gitignore
├── LICENSE
├── notify_bridge.py
├── README.md
└── pyproject.toml
```

## Portability

The project avoids hard-coded local filesystem paths. Runtime paths are derived from the repository root using `pathlib`, so the same source tree can run on Windows, Linux, and GitHub Actions without changing source-code paths.

## Security

Ignored local artifacts include:

```text
.env
.venv/
__pycache__/
.pytest_cache/
*.egg-info/
reports/manual/
```

Do not store credentials directly in Python source files, YAML configuration, README files, Git commits, or generated reports.

## Testing

Run all tests:

```bash
python -m pytest
```

The offline test suite covers path portability, configuration, arXiv parsing, retry behavior, date filtering, ID normalization, state management, relevance scoring, PDF extraction, section parsing, analysis context, structured-output schemas, LLM provider selection, analyzer behavior, report writing, paper processing, paper transactions, batch processing, research digests, complete workflows, and CLI behavior.

Network services are mocked in unit tests, so the normal test suite does not consume LLM API credits.

## Troubleshooting

**A digest exists on GitHub but not on my machine.** The repository has not been pulled. Run `git pull --rebase origin main`, or let `notify_bridge.py` do it.

**Every digest reports zero papers.** Read the retrieval statistics in the digest. `Candidates retrieved` at zero means the query matched nothing; a non-zero value collapsing to `Recent papers: 0` means `lookback_days` is narrower than the topic's publication rate; `Relevant papers: 0` with a non-zero `Unprocessed papers` means the relevance rules rejected everything. `arxiv-scout scan --force` reproduces all of this without spending API credits.

**`notify_bridge.py` reports that sync is blocked.** The working tree has uncommitted changes and cannot fast-forward. Commit or stash them, then run the script again.

**One source returned nothing.** The digest lists candidates per source, and a failed source appears there with its error. A source that fails does not stop the run, so an empty digest with a `europepmc FAILED` line means the other sources still ran.

**A scheduled run turned red on GitHub.** Exit code 1 means at least one paper failed during analysis. The digest for that run was still written and lists the failures; `last_successful_run_utc` was deliberately left unchanged so the failed papers are retried on the next wake-up.

## Current Example Research Topic

The repository is currently configured to monitor:

```text
3D CT Lung Nodule Detection
```

This is only the default example configuration. To monitor another field, modify `config/scout.yaml`; the source code does not need to be changed.

## Development Status

Core research-monitoring functionality is operational, including local execution, dual-provider analysis, structured paper analysis, per-paper reports, multi-paper digests, persistent state, GitHub Actions automation, scheduled unattended execution, and desktop notification of cloud results.

The Skill integration under `skills/arxiv-paper-scout/` is the next integration layer.

## License

This project is distributed under the MIT License.

See [`LICENSE`](LICENSE) for details.
