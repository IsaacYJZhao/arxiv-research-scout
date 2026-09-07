# Benchmarking of AI and Radiologists for Indeterminate Lung Nodule Malignancy Risk Estimation at Screening CT: The LUNA25 Challenge

## Paper Information

- **Source:** europepmc
- **Paper ID:** 42340186
- **DOI:** 10.1148/ryai.260179
- **Venue:** Radiology. Artificial intelligence
- **Authors:** Peeters D, Obreja B, Antonissen N, Saghir Z, Pastorino U, Silva M, de Bock GH, Gietema H, Gleeson F, Heuvelmans MA, Lam S, Litjens G, Hoesein FM, Schaefer-Prokop C, Scholten E, Snoeckx A, van der Heijden EHFM, Vliegenthart R, Prokop M, Jacobs C
- **Published:** 2026-09-01
- **Updated:** 2026-09-01
- **Categories:** Artificial intelligence, Lung, Screening, Thorax, CT, Observer Performance, Supervised Learning, Radiologists, Benchmarking, Lung Cancer Screening, Deep Learning, Pulmonary Nodule Malignancy Risk
- **Landing URL:** https://doi.org/10.1148/ryai.260179
- **PDF URL:** Not reported in the available evidence.

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** abstract_only
- **Confidence:** medium
- **PDF status:** No full text available; abstract only

## Methodology

本研究基于 LUNA25 挑战赛框架，对用于低剂量 CT（LDCT）筛查中不确定大小肺结节（5-15 mm）恶性风险估计的 AI 系统与放射科医生进行了基准比较。AI 开发团队可利用来自 National Lung Screening Trial 的公开数据集（4069 例基线 LDCT 扫描、555 个恶性和 5608 个良性结节）开发 AI 系统。外部测试在来自三个欧洲大型肺癌筛查试验的 463 例基线扫描上进行，包括 156 个恶性和 312 个良性且大小匹配的不确定结节。根据受试者工作特征曲线下面积（AUC）选择表现最佳的 AI 系统。随后开展观察者研究，由放射科医生评估从外部测试集中随机选择的 300 个结节（100 个恶性、200 个良性）。放射科医生将结节分为低、中、高风险，并将中风险或以上（中风险或高风险）作为阳性检测结果的阈值。在随机子集上通过 AUC 将所选 AI 系统与放射科医生进行比较。论文未报告 AI 系统的具体模型架构、预处理、训练策略、优化器、学习率、损失函数、数据增强等详细技术信息。

## Evaluation

评估采用外部测试与观察者研究相结合的方式。外部测试集由 463 例基线扫描组成，包含 156 个恶性和 312 个良性且大小匹配的不确定肺结节，扫描来自三个欧洲大型肺癌筛查试验。根据 AUC 从参赛 AI 系统中选出最佳系统。观察者研究使用从外部测试集中随机选择的 300 个结节（100 个恶性、200 个良性），由 65 名放射科医生进行评估。放射科医生将结节分为低、中、高风险，并将中风险或以上作为阳性阈值。在相同子集上比较所选 AI 系统与放射科医生的 AUC，并报告 95% 置信区间和 P 值。论文未报告训练/验证/测试的具体划分、交叉验证设置、除放射科医生外的其他基线模型、消融实验或其他评估指标。

## Innovation

主要贡献是在标准化和透明的 LUNA25 挑战赛框架内，对用于不确定大小（5-15 mm）肺结节恶性风险估计的 AI 系统与放射科医生进行前瞻性设计的外部基准比较，涵盖来自多个欧洲筛查试验的外部数据，并在同一观察者研究子集上以相同阈值定义直接比较 AI 与放射科医生的性能。

## Datasets

- National Lung Screening Trial 公开数据集
- 三个欧洲大型肺癌筛查试验外部测试集

## Metrics

- AUC
- 95% CI
- P 值
- 灵敏度
- 特异度

## Key Results

- 所选 AI 系统在 300 个结节子集上的 AUC 为 0.78（95% CI: 0.73, 0.84）。
- 65 名放射科医生的平均 AUC 为 0.70（95% CI: 0.65, 0.74）。
- AI 系统 AUC 显著高于放射科医生平均值（P = .001）。
- 在中风险或以上阈值下，AI 系统在匹配特异度时正确分类的恶性结节比例比放射科医生高 12%。
- 在匹配灵敏度时，AI 系统的假阳性结果比放射科医生少 20%。

## Limitations

作者明确报告的局限性在提供的证据中未详细说明。基于现有证据的不完整信息，尚无法判断以下方面：AI 系统的具体技术架构和训练细节未报告；外部测试集与观察者研究子集的详细人口学和结节特征未提供；放射科医生的经验水平和阅片条件未描述；除 AUC 及其比较外，未报告其他统计检验或亚组分析；研究仅使用中风险或以上作为放射科医生阳性阈值进行比较，其他阈值设定下的表现未报告。此外，外部测试集中 156 个恶性和 312 个良性结节与观察者研究使用的 300 个结节（100 个恶性、200 个良性）之间的关系及抽样方式在现有证据中未充分说明。

## Processing Notes

The PDF could not be fully processed. Analysis used the available arXiv metadata and other recoverable evidence.

- **PDF error:** No downloadable full text is available for this record.
