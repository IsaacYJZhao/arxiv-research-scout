# Integration of closed-loop fully-automated AI model with clinician assessment for lung nodule stratification: A multi-reader study

## Paper Information

- **Source:** europepmc
- **Paper ID:** 42659915
- **DOI:** 10.1016/j.resinv.2026.101507
- **Venue:** Respiratory investigation
- **Authors:** Taha A, Kheir F
- **Published:** 2026-08-27
- **Updated:** 2026-08-27
- **Categories:** Artificial intelligence, Lung cancer, Lung Nodule, Bronchosolve
- **Landing URL:** https://doi.org/10.1016/j.resinv.2026.101507
- **PDF URL:** Not reported in the available evidence.

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** abstract_only
- **Confidence:** low
- **PDF status:** No full text available; abstract only

## Methodology

该研究评估了一种闭环、全自动AI模型 Bronchosolve 与临床医生评估的序贯整合方法，用于肺结节风险分层。研究设计为完全交叉的多阅片者、多病例回顾性研究，纳入296例筛查或偶然发现的肺结节胸部CT扫描。实验比较了三种解读条件：仅临床医生、仅 Bronchosolve（AI）、以及AI辅助的临床医生解读（即序贯应用AI对临床医生评估进行整合或再分类）。主要结局为受试者工作特征曲线下面积（AUC）和准确性；次要结局包括敏感性、特异性及净重分类改善指数（NRI），并预设了对中等风险结节的亚组分析。论文证据中未报告模型的具体架构、训练策略、预处理、数据划分或推理流程等细节。

## Evaluation

研究使用296例胸部CT扫描进行回顾性、完全交叉的多阅片者多病例评估，比较三种条件：临床医生、Bronchosolve（AI）和AI辅助的临床医生解读。报告了AUC、准确性、敏感性、特异性和NRI。中等风险亚组为预设分析。证据中未报告阅片者人数、数据集划分方式、基线模型、统计检验方法的具体类型、置信区间计算方法或样本的良恶性构成。

## Innovation

作者提出的贡献在于评估 Bronchosolve 这一闭环全自动AI模型在临床工作流中的增量价值，特别是其序贯应用在中等风险肺结节重分类和风险消解中的作用。研究强调AI辅助临床医生解读相比单独临床医生或AI的判别能力和再分类改善，但论文证据中未提供该模型在技术架构层面的创新描述。

## Datasets

- 296 chest CT scans from screening and incidentally detected lung nodules

## Metrics

- AUC
- accuracy
- sensitivity
- specificity
- NRI

## Key Results

- 平均AUC从临床医生的0.84（95% CI，0.83-0.86）提高至Bronchosolve的0.87（95% CI，0.86-0.88），AI辅助临床医生解读为0.88（95% CI，0.86-0.89）。
- 整体阅片者准确性从74.7%提高至77.7%（p < 0.01）。
- 在中等风险亚组中，序贯AI辅助工作流达到88.2%的敏感性和52.3%的特异性，而单独Bronchosolve的敏感性为84.8%。
- 全队列NRI为0.19，主要由恶性结节被正确向上重分类驱动（事件NRI = 0.10）。
- 在全队列中，初始Low-Risk和High-Risk病例的重分类变化极小；Bronchosolve主要将Intermediate-Risk结节重分类为二元的Low-Risk或High-Risk最终类别。
- 在969次Intermediate-Risk阅片病例评估中，47.8%被重新分为Low-Risk（其中71.1%为良性），52.2%被重新分为High-Risk（其中59.7%为恶性），表明具有临床意义的风险消解。

## Limitations

作者在提供的论文证据中未明确陈述研究局限性。因此，以下仅为基于证据不完整性的推断限制，而非作者明确声明的局限性：未报告阅片者人数、数据集训练/验证/测试划分、模型技术细节、基线比较方法、统计检验具体方法，也未说明研究是否包含外部验证或前瞻性数据。

## Processing Notes

The PDF could not be fully processed. Analysis used the available arXiv metadata and other recoverable evidence.

- **PDF error:** No downloadable full text is available for this record.
