# Dual-Scale Hybrid Concept Bottleneck Network for Explainable 3D Lung Nodule Malignancy Classification in CT Imaging

## Paper Information

- **Source:** europepmc
- **Paper ID:** 42783879
- **DOI:** 10.3390/jimaging12090455
- **Venue:** Journal of imaging
- **Authors:** Ali A, Iftikhar MA, Farooque G, Sargano AB
- **Published:** 2026-09-20
- **Updated:** 2026-09-20
- **Categories:** computed tomography, External Validation, Transformer, 3D Deep Learning, Explainable Artificial Intelligence, Cross-attention Fusion, Hybrid Concept Bottleneck, Lung Nodule Malignancy Classification
- **Landing URL:** https://doi.org/10.3390/jimaging12090455
- **PDF URL:** Not reported in the available evidence.

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** abstract_only
- **Confidence:** low
- **PDF status:** No full text available; abstract only

## Methodology

本文提出了 Dual-Scale Hybrid Concept Bottleneck Network (DS-HCBN)，用于可解释的 3D 肺结节良恶性分类。根据摘要，该框架处理一个以结节为中心的局部 patch 和一个较大的上下文 patch，并使用共享的 residual 3D 卷积编码器和一个轻量级上下文 Transformer。局部和上下文表示通过 gated cross-attention 进行融合。在混合分类器中，八个放射学属性被作为监督的中间表示进行学习。模型在 LIDC-IDRI 上使用防泄漏的 patient-wise split 进行开发，并在保留的内部测试集上进行评估。外部评估在 LNDb 队列上进行，使用相同的冻结模型，未进行重训练或微调。摘要未提供更详细的预处理、训练策略、优化器、学习率、损失函数或其他具体实现细节。

## Evaluation

评估在 LIDC-IDRI 的保留内部测试集和外部 LNDb 队列上进行。LIDC-IDRI 使用 leakage-controlled patient-wise split。外部 LNDb 评估直接使用相同的冻结模型，未进行重训练或微调。报告的指标包括 accuracy、F1-score 和 ROC-AUC。具体数值为：LIDC-IDRI 内部测试集 accuracy 87.34%、F1-score 80.39%、ROC-AUC 94.35%；LNDb accuracy 80.41%、ROC-AUC 78.65%。摘要未报告数据集的具体样本量、结节数量、训练/验证/测试的具体划分比例、基线模型、统计检验、消融实验或其他评估细节。

## Innovation

本文的技术贡献在于将局部结节形态和更广泛的解剖上下文进行双尺度处理，并通过 gated cross-attention 融合共享 residual 3D 卷积编码器和轻量级上下文 Transformer 的表示。同时，采用八个放射学属性作为监督的中间表示，形成概念瓶颈机制，以增强模型的可解释性。摘要明确指出其目标是解决现有方法只强调结节中心形态或更广泛解剖上下文、且对模型所代表的放射学信息解释有限的问题。需要强调的是，摘要并未声称该方法为首创或达到 state-of-the-art。

## Datasets

- LIDC-IDRI
- LNDb

## Metrics

- accuracy
- F1-score
- ROC-AUC

## Key Results

- 在 LIDC-IDRI 内部测试集上，DS-HCBN 达到 87.34% accuracy、80.39% F1-score 和 94.35% ROC-AUC。
- 在 LNDb 外部数据集上，使用相同的冻结模型且未重训练或微调，DS-HCBN 达到 80.41% accuracy 和 78.65% ROC-AUC。
- 结果显示内部区分能力较强，但跨数据集性能明显下降。
- 摘要指出结果支持使用局部形态、解剖上下文和放射学概念监督进行概念引导的肺结节分类，同时强调在更广泛的临床应用前需要改进域泛化能力。

## Limitations

作者明确指出，模型在跨数据集上表现出明显的性能下降，并强调在更广泛的临床应用前需要改进域泛化能力。除此之外，从所供证据中无法确定其他作者明确陈述的限制。由于仅提供了摘要级别的证据，完整方法细节、实验设置、统计检验、基线比较和消融分析均未报告，这些属于证据不完整导致的推断性限制，不应视为作者明确声明的限制。

## Processing Notes

The PDF could not be fully processed. Analysis used the available arXiv metadata and other recoverable evidence.

- **PDF error:** No downloadable full text is available for this record.
