# Usage Examples

This reference provides example user requests and recommended response patterns
for the `arxiv-paper-scout` Skill.

Use it together with:

- `../SKILL.md`
- `scout-output-schema.md`

## 1. Latest Research Update

### User request

> 最近有什么新的相关论文？

### Recommended behavior

1. Inspect the newest available digest under `reports/digests/`.
2. Report the digest date and run status.
3. State how many papers were selected and successfully analyzed.
4. Summarize each paper using only available scout evidence.
5. Mention failures or evidence fallbacks when relevant.

### Recommended response shape

```text
最近一次 Research Scout 运行时间：<timestamp>
状态：complete / partial
本轮成功分析：<count> 篇

1. <Paper title>
   - Methodology: ...
   - Evaluation: ...
   - Innovation: ...
   - Key Results: ...
   - Limitations: ...
   - Evidence: full_text / partial_text / abstract_only

如果本轮没有新论文，应明确说明：
“最近一次运行没有发现需要进一步分析的新论文。”
```

## 2. Summarize the Latest Digest

### User request

> 总结一下最新的 digest。

### Recommended behavior

- Read the newest digest.
- Preserve the run-level statistics.
- Summarize only successfully analyzed papers.
- Mention processing failures separately.
- Do not invent missing paper details.

### Recommended response shape

```text
最新 digest：<date>

检索概况：
- Candidates retrieved: ...
- Relevant papers: ...
- Selected for analysis: ...
- Successfully analyzed: ...
- Failed: ...

论文摘要：
- <Title>: <1-3 sentence summary>
- <Title>: <1-3 sentence summary>

如存在失败：
Processing issues:
- <arXiv ID>: <error summary>
```

## 3. Explain One Paper

### User request

> 解释一下 arXiv:2608.16855v1 这篇论文。

### Recommended behavior

1. Locate the paper report if available.
2. Prefer structured scout fields.
3. Explain methodology, evaluation, innovation, datasets, metrics, key results,
   limitations, evidence level, and confidence.
4. If evidence is incomplete, say so explicitly.

### Recommended response shape

```text
论文：<Title>

研究目标：
...

Methodology：
...

Evaluation：
...

Innovation：
...

Datasets：
...

Metrics：
...

Key Results：
...

Limitations：
...

Evidence：
<level>, confidence=<value>
```

## 4. Compare Two Papers

### User request

> 比较这两篇论文的方法和实验结果。

### Recommended behavior

Compare using the same dimensions for both papers.

### Recommended comparison dimensions

- Research objective
- Methodology
- Architecture or algorithm
- Dataset
- Evaluation protocol
- Metrics
- Key results
- Innovation
- Limitations
- Computational cost, only if explicitly reported
- Relevance to the monitored topic

### Recommended response shape

```text
| Dimension | Paper A | Paper B |
|---|---|---|
| Objective | ... | ... |
| Methodology | ... | ... |
| Dataset | ... | ... |
| Metrics | ... | ... |
| Key Results | ... | ... |
| Innovation | ... | ... |
| Limitations | ... | ... |

结论：
- Paper A 更适合……
- Paper B 更适合……

仅在 scout 证据支持时给出这种判断。
```

## 5. Research Trends Across Multiple Runs

### User request

> 最近几次运行有什么研究趋势？

### Recommended behavior

1. Inspect multiple recent digests.
2. State the evidence window.
3. Identify recurring methods, datasets, metrics, and research directions.
4. Do not call something a trend if it appears in only one paper.

### Recommended response shape

```text
观察窗口：<date range / number of digests>

主要趋势：

1. <Trend>
   - 出现于：<papers or runs>
   - 共同特征：...
   - 证据：...

2. <Trend>
   - 出现于：...
   - 共同特征：...

尚不能视为趋势的单次现象：
- ...
```

## 6. Why Was This Paper Selected?

### User request

> 为什么这篇论文会被筛选出来？

### Recommended behavior

1. Inspect the paper title, abstract, or report.
2. Inspect `config/scout.yaml` if available.
3. Relate the paper to configured core, target, supporting, and deprioritized
   terms.
4. Use the actual relevance score only if it is available.

### Recommended response shape

```text
这篇论文被选中的主要原因：

- Core relevance: ...
- Target relevance: ...
- Supporting relevance: ...
- Deprioritized aspects: ...

如果实际 relevance score 可用：
Relevance score: <score> (<level>)

如果 score 不可用：
不要编造分数，只做定性解释。
```

## 7. Check Scout Status

### User request

> Research Scout 最近运行了吗？

### Recommended behavior

1. Read `.state/state.json`.
2. Report `last_successful_run_utc`.
3. Optionally report the number of processed IDs.
4. Compare with the newest digest timestamp if useful.

### Recommended response shape

```text
Last successful run: <timestamp>
Processed papers: <count>
Newest digest: <date>

状态判断：
- 正常 / 需要关注

注意：
GitHub Actions 可以每天唤醒，但 Python 会根据 `run_every_days`
决定是否真正执行研究扫描。
```

## 8. No New Papers

### User request

> 为什么这次没有报告新论文？

### Recommended behavior

Use retrieval statistics to explain where papers were filtered out.

Possible causes include:

- no papers in the lookback window;
- papers were already processed;
- papers failed the relevance threshold;
- no papers were selected after ranking.

Do not infer a cause unless the digest statistics support it.

### Recommended response shape

```text
本轮没有新论文进入分析阶段。

从 digest 看：
- Candidates retrieved: ...
- Recent papers: ...
- Unprocessed papers: ...
- Relevant papers: ...
- Selected for analysis: 0

因此最可能的原因是：<supported explanation>.
```

## 9. Partial Run

### User request

> 为什么这次 run 是 partial？

### Recommended behavior

1. Inspect the `Processing Failures` section.
2. Separate successful papers from failed papers.
3. Explain that successful paper reports remain valid.
4. Explain that failed papers can remain eligible for retry.

### Recommended response shape

```text
本轮状态为 partial，因为有 <count> 篇论文处理失败。

成功：
- <Paper A>
- <Paper B>

失败：
- <Paper C>: <error>

成功论文的结果仍然有效。
失败论文不会被当作成功处理，后续运行可重新尝试。
```

## 10. Evidence Is Abstract-Only

### User request

> 这篇报告只有 abstract_only，能相信到什么程度？

### Recommended behavior

Explain the limitation of evidence, not the scientific quality of the paper.

### Recommended response shape

```text
`abstract_only` 表示这次分析主要依赖 arXiv metadata 和 abstract。

因此可以较有把握总结：
- 研究目标
- 作者公开描述的主要方法
- abstract 中明确给出的主要结果

不应据此断言：
- 完整网络结构
- 训练超参数
- 数据划分
- ablation
- 完整 baseline
- abstract 中未出现的数值结果
```

## 11. Ask for Unsupported Details

### User request

> 这篇论文用了多少参数？学习率是多少？

### Recommended behavior

If the scout output does not contain those values, do not guess.

### Recommended response shape

```text
当前 scout 输出中没有明确报告参数量或学习率。

我不会根据常见设置推断这些数值。
如果需要，需要进一步查看论文原文中的 implementation / training details。
```

## 12. Provider Comparison

### User request

> OpenAI 和 DeepSeek 对这篇论文的总结哪个更好？

### Recommended behavior

Compare actual generated reports only.

Evaluate:

- evidence fidelity
- completeness
- numerical accuracy
- hallucination risk
- terminology
- conciseness
- language quality

Do not prefer a provider solely because of provider identity.

## 13. Manual Paper Analysis

### User request

> 我想单独分析一篇 arXiv 论文。

### Recommended behavior

If backend execution is unavailable, provide the exact CLI command.

Default provider:

```bash
arxiv-scout analyze-paper <arxiv-id>
```

OpenAI override:

```bash
arxiv-scout analyze-paper <arxiv-id> --provider openai
```

Explain that manual analysis does not modify scheduled-run state.

## 14. Force a Scan

### User request

> 我现在就想检查一次 arXiv，不等三天。

### Recommended behavior

If backend execution is unavailable, provide:

```bash
arxiv-scout scan --force
```

For the complete research workflow:

```bash
arxiv-scout run --force
```

Mention that `run --force` can trigger LLM usage when papers are selected.

## 15. Change Research Topic

### User request

> 我想把监控方向改成另一个研究主题。

### Recommended behavior

Direct the user to `config/scout.yaml`.

Relevant configuration areas:

- `topic.name`
- `topic.arxiv_query`
- `topic.categories`
- `relevance.core_terms`
- `relevance.target_terms`
- `relevance.supporting_terms`
- `relevance.deprioritize_terms`

Do not require source-code changes unless the requested behavior cannot be
expressed through configuration.

## 16. Safety and Evidence Reminder

For every usage pattern above:

- never expose API keys;
- never invent evidence;
- never claim execution without a real tool result;
- never turn missing information into plausible-looking technical details;
- preserve uncertainty when evidence is incomplete.
