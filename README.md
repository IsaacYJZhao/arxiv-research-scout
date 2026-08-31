# arXiv Research Scout

A portable research-monitoring pipeline for discovering relevant arXiv papers, extracting evidence from PDFs, analyzing papers with an LLM, and generating structured literature reports and multi-paper research digests.

The project is designed for both local execution and unattended GitHub Actions workflows.

## Features

* Search arXiv using configurable research topics and categories.
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
.\\.venv\\Scripts\\python.exe -m pip install -e ".\[dev]"
.\\.venv\\Scripts\\python.exe -m pytest
```

### Linux / macOS

```bash
python3.11 -m venv .venv
./.venv/bin/python -m pip install -e ".\[dev]"
./.venv/bin/python -m pytest
```

## API Keys

API keys are read only from environment variables. Do not store real credentials in source code, `config/scout.yaml`, README files, or Git commits.

Supported variables:

```text
DEEPSEEK\_API\_KEY
OPENAI\_API\_KEY
```

The repository includes `.env.example` only as documentation:

```text
OPENAI\_API\_KEY=your\_openai\_api\_key\_here
DEEPSEEK\_API\_KEY=your\_deepseek\_api\_key\_here
```

### PowerShell

```powershell
$env:DEEPSEEK\_API\_KEY = "<your-key>"
$env:OPENAI\_API\_KEY = "<your-key>"
```

### Linux / macOS

```bash
export DEEPSEEK\_API\_KEY="<your-key>"
export OPENAI\_API\_KEY="<your-key>"
```

Only the key for the provider actually used is required.

## LLM Providers

The default provider is configured in `config/scout.yaml`:

```yaml
llm:
  default\_provider: "deepseek"
```

Inspect the active provider:

```powershell
.\\.venv\\Scripts\\arxiv-scout.exe provider
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

`scan` previews retrieval/relevance results. It does not analyze papers and does not update persistent state.

### Run the Complete Pipeline

```bash
arxiv-scout run
```

Pipeline:

```text
arXiv scan
→ filtering
→ relevance ranking
→ PDF processing
→ LLM analysis
→ paper reports
→ research digest
→ state update
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

## Configuration

Main configuration file:

```text
config/scout.yaml
```

Important sections:

```yaml
topic:
  name: "3D CT Lung Nodule Detection"
  arxiv\_query: >
    ...
  categories:
    - "cs.CV"
    - "eess.IV"

schedule:
  run\_every\_days: 3
  lookback\_days: 5

retrieval:
  max\_candidates: 40
  max\_papers: 8

pdf:
  max\_download\_mb: 50
  max\_text\_chars: 70000
  timeout\_seconds: 90
  max\_attempts: 3

llm:
  default\_provider: "deepseek"

output:
  language: "zh-CN"
  reports\_dir: "reports"

state:
  file: ".state/state.json"
```

### Scheduling

`run\_every\_days` controls how often a full research scan is due. GitHub Actions may wake up more frequently, but the Python application checks `.state/state.json` before doing research work.

## Relevance Filtering

The project uses configurable rule-based relevance scoring before sending papers to an LLM. The configuration supports core terms, target terms, supporting terms, deprioritized terms, a minimum score, and a high-relevance score.

This reduces unnecessary PDF processing and LLM API usage.

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
full\_text
partial\_text
abstract\_only
```

Evidence level is determined by local code rather than by the LLM.

## Reports

### Per-paper Reports

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

## State Management

Persistent state is stored in:

```text
.state/state.json
```

Example:

```json
{
  "schema\_version": 1,
  "last\_successful\_run\_utc": null,
  "processed\_ids": \[]
}
```

arXiv version suffixes are normalized for processed-paper identity. For example, `2608.12345v1`, `2608.12345v2`, and `2608.12345v3` are treated as versions of the same paper.

## Transaction Semantics

The project deliberately separates paper-level success from run-level success.

For one paper:

```text
analysis succeeds
→ report succeeds
→ processed ID is persisted
```

For one complete scheduled run:

```text
selected papers processed
→ digest successfully written
→ no unresolved paper failures
→ last\_successful\_run\_utc updated
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

* manual execution through `workflow\_dispatch`
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
  run\_every\_days: 3
```

before performing a full research scan. A daily GitHub Actions wake-up does not imply a daily LLM API call.

### Required GitHub Secret

For the default DeepSeek provider, configure:

```text
DEEPSEEK\_API\_KEY
```

In the GitHub repository:

```text
Settings
→ Secrets and variables
→ Actions
→ New repository secret
```

If scheduled runs are later configured to use OpenAI, also add `OPENAI\_API\_KEY`.

## GitHub Actions Output Persistence

When a scheduled run produces changes, GitHub Actions automatically commits:

```text
.state/state.json
reports/
```

using the GitHub Actions bot account. If no generated files change, no commit is created.

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
│       └── SKILL.md
├── src/
│   └── arxiv\_research\_scout/
│       ├── \_\_init\_\_.py
│       ├── analysis\_context.py
│       ├── analysis\_schema.py
│       ├── analyzer.py
│       ├── arxiv\_client.py
│       ├── batch\_processor.py
│       ├── cli.py
│       ├── config.py
│       ├── digest\_writer.py
│       ├── llm\_provider.py
│       ├── manual\_analysis.py
│       ├── models.py
│       ├── paper\_filters.py
│       ├── paper\_lookup.py
│       ├── paper\_processor.py
│       ├── paper\_transaction.py
│       ├── paths.py
│       ├── pdf\_reader.py
│       ├── relevance.py
│       ├── report\_writer.py
│       ├── runner.py

│       ├── section\_parser.py

│       ├── state\_manager.py

│       └── workflow.py├── tests/
├── .env.example
├── .gitattributes
├── .gitignore
├── LICENSE
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
\_\_pycache\_\_/
.pytest\_cache/
\*.egg-info/
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

## Current Example Research Topic

The repository is currently configured to monitor:

```text
3D CT Lung Nodule Detection
```

This is only the default example configuration. To monitor another field, modify `config/scout.yaml`; the source code does not need to be changed.

## Development Status

Core research-monitoring functionality is operational, including local execution, dual-provider analysis, structured paper analysis, per-paper reports, multi-paper digests, persistent state, GitHub Actions automation, and scheduled unattended execution.

The ChatGPT Skill integration under `skills/arxiv-paper-scout/` is the next integration layer.

## License

This project is distributed under the MIT License.

See [`LICENSE`](LICENSE) for details.
