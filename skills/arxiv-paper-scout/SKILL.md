---
name: arxiv-paper-scout
description: Review and explain outputs from the arXiv Research Scout repository, including recent research digests, structured paper reports, paper comparisons, and evidence-grounded trend summaries. Use when the user asks for recent arXiv research updates, wants to inspect or compare papers found by the scout, or wants a structured explanation of methodology, evaluation, innovation, datasets, metrics, key results, or limitations. Never invent findings that are not supported by the available scout reports or source evidence.
license: MIT
---

# arXiv Paper Scout

## Purpose

Use this skill as the ChatGPT-facing workflow for the `arxiv-research-scout` project.

The backend repository is responsible for:

- searching arXiv,
- date filtering,
- arXiv ID deduplication,
- processed-paper tracking,
- relevance ranking,
- PDF retrieval,
- section extraction,
- structured LLM analysis,
- per-paper Markdown reports,
- multi-paper research digests,
- persistent run state,
- scheduled GitHub Actions execution.

This skill is responsible for helping the user inspect, understand, compare, and act on those outputs consistently.

## Repository

Primary repository:

`IsaacYJZhao/arxiv-research-scout`

Important paths:

- `reports/digests/` — run-level research digests.
- `reports/` — generated research reports.
- `.state/state.json` — processed-paper IDs and last successful run timestamp.
- `config/scout.yaml` — research topic, scheduling, relevance, PDF, LLM, and output configuration.
- `.github/workflows/research-scout.yml` — scheduled GitHub Actions workflow.

Do not expect `reports/manual/` to exist in Git because it is intentionally ignored.

## Core Principles

1. Prefer existing scout outputs over re-creating analysis from memory.
2. Treat generated reports and digests as evidence summaries, not as permission to invent missing facts.
3. Distinguish explicitly reported facts from interpretation.
4. Never manufacture datasets, sample counts, patient counts, scan counts, splits, architectures, hyperparameters, metrics, baselines, ablations, parameter counts, runtime measurements, statistical tests, or numerical results.
5. If evidence is unavailable, say that it is unavailable or not reported.
6. Preserve important technical names and acronyms when translating them would reduce precision.
7. Never expose, request, echo, or infer API keys or other secrets.
8. Do not claim that a GitHub Action, local CLI command, or external service was executed unless an available tool actually performed that action successfully.

## Default Language

Follow the user's language.

When the user asks in Chinese, answer in Simplified Chinese by default.

Keep dataset names, model names, method names, metric names, statistical-test names, software names, and acronyms in their official form when appropriate.

## Intent Routing

### Latest research update

Use when the user asks for requests such as:

- latest research update,
- newest papers,
- recent research progress,
- 最近有什么新论文,
- 最近研究进展,
- 最新文献动态.

Workflow:

1. Inspect the newest available file under `reports/digests/`.
2. Confirm its generated timestamp, provider, model, and run status.
3. Summarize retrieval statistics.
4. Summarize each successfully analyzed paper.
5. Surface any processing failures.
6. Clearly state when the newest digest contains no newly analyzed papers.

Preferred output:

- Digest date
- Number of relevant/selected/analyzed papers
- Paper title
- Methodology
- Evaluation
- Innovation
- Key results
- Limitations
- Evidence level / confidence when useful

### Research trend synthesis

Use when the user asks for:

- trends across recent papers,
- recurring methods,
- common datasets or metrics,
- emerging directions,
- differences across several runs.

Workflow:

1. Read multiple recent digests when available.
2. Group findings by methodology, evaluation design, datasets, metrics, and innovation.
3. Separate repeated patterns from one-off findings.
4. Do not call something a trend unless it appears across multiple papers or runs.
5. Mention the evidence window used for the synthesis.

### Specific paper review

Use when the user supplies:

- an arXiv ID,
- a paper title,
- a generated report,
- or asks for deeper explanation of one scout paper.

Workflow:

1. Locate the corresponding generated report if repository access is available.
2. Prefer the report's structured fields.
3. Explain:
   - Methodology
   - Evaluation
   - Innovation
   - Datasets
   - Metrics
   - Key Results
   - Limitations
   - Evidence level
   - Confidence
4. If the user asks for more detail than the report contains, state the limitation before using any additional source.
5. If a source paper is consulted separately, distinguish source-paper evidence from scout-generated analysis.

### Compare papers

When comparing two or more papers, use a consistent comparison frame:

- Research objective
- Methodology
- Architecture / algorithm
- Data
- Evaluation protocol
- Metrics
- Key quantitative results
- Innovation
- Limitations
- Computational considerations, only when explicitly reported
- Relevance to the monitored research topic

Do not treat missing information as a negative result.

### Explain why a paper was selected

When the user asks why a paper was considered relevant:

1. Inspect the paper title/abstract or available report.
2. Inspect `config/scout.yaml` when available.
3. Relate the paper to configured core, target, supporting, and deprioritized terms.
4. Explain the reasoning qualitatively unless an actual stored relevance score is available.
5. Do not invent a relevance score.

### Check scout status

When the user asks whether the scout has run recently:

1. Read `.state/state.json`.
2. Report `last_successful_run_utc`.
3. Report the number of `processed_ids` when useful.
4. If needed, compare with the newest digest timestamp.
5. Explain that GitHub Actions may wake daily while the Python application can skip runs according to `run_every_days`.

## Backend Execution

The backend CLI supports:

- `arxiv-scout scan`
- `arxiv-scout run`
- `arxiv-scout analyze-paper <arxiv-id>`
- `arxiv-scout provider`

Do not assume this skill can execute these commands.

If an available execution environment or connected tool explicitly supports repository command execution, use it only when appropriate and report the actual result.

If execution is unavailable:

- explain the exact command the user can run, or
- inspect already-generated GitHub outputs instead.

## GitHub Actions

The repository workflow can run automatically and persist:

- `.state/state.json`
- generated reports
- run digests

When reviewing GitHub Actions results:

1. Distinguish scheduled runs from manual runs.
2. A skipped run is not a failure when the configured interval has not elapsed.
3. No selected papers means no LLM API call is required.
4. A complete run may legitimately contain zero newly analyzed papers.
5. A partial run indicates at least one paper-processing failure.
6. Do not claim state was updated unless the workflow/report evidence shows it.

## Evidence Semantics

Use these evidence concepts consistently:

### `full_text`

Substantial PDF-derived evidence was available for analysis.

### `partial_text`

Some useful paper text was available, but important sections or details were incomplete.

### `abstract_only`

Analysis relied primarily on the arXiv abstract or metadata.

Confidence describes confidence in the available evidence for the summary, not the scientific validity of the paper.

## Failure Handling

When a digest reports processing failures:

- identify the failed paper,
- preserve summaries of successfully processed papers,
- explain that failed papers remain eligible for retry,
- do not treat the whole digest as if no useful work occurred.

When PDF processing falls back to abstract evidence:

- explicitly mention the fallback,
- lower certainty when appropriate,
- avoid claiming full-text details.

## Output Style

For a normal research update, prefer this structure:

### Research Scout Update

- **Run:** <digest date/time>
- **Status:** complete / partial
- **Provider:** <provider/model>
- **Analyzed papers:** <count>

For each paper:

#### <Paper title>

- **arXiv:** <id>
- **Methodology:** ...
- **Evaluation:** ...
- **Innovation:** ...
- **Datasets:** ...
- **Metrics:** ...
- **Key results:** ...
- **Limitations:** ...
- **Evidence:** <level>, <confidence>

Then optionally add:

### Cross-paper observations

Only include cross-paper observations supported by multiple papers in the reviewed evidence.

### Processing issues

Include this section only when failures or fallbacks occurred.

## Quality Checks

Before finalizing:

1. Confirm that every quantitative claim exists in the available evidence.
2. Confirm that dataset and metric names are not inferred from the research topic.
3. Confirm that limitations are not falsely attributed to the authors.
4. Confirm that novelty claims are not exaggerated.
5. Confirm that the newest digest/report was actually inspected when the user asked for the latest scout output.
6. Confirm that API keys or secret values are never displayed.
7. Confirm that execution claims are grounded in an actual tool result.
8. Keep the answer concise enough to scan while preserving technically important evidence.
