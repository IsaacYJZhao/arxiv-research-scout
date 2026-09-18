# Multi-view attention-based deep learning for benign-malignant classification of pulmonary nodules

## Paper Information

- **Source:** europepmc
- **Paper ID:** 42743330
- **DOI:** 10.1371/journal.pone.0357963
- **Venue:** PloS one
- **Authors:** Zhang L, Zhuo D, Wu X, He Y, Kang G
- **Published:** 2026-09-15
- **Updated:** 2026-09-15
- **Categories:** 
- **Landing URL:** https://doi.org/10.1371/journal.pone.0357963
- **PDF URL:** https://europepmc.org/articles/PMC13577567?pdf=render

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** abstract_only
- **Confidence:** medium
- **PDF status:** Download or parsing failed; abstract used instead

## Methodology

作者提出了一种基于三视图的肺结节分类框架，结合轴向、冠状和矢状切片提取互补表示。框架包含两个核心组件：一是 Lesion-Guided Attention（LGA），利用病灶掩码作为弱空间先验，在保留上下文信息的同时增强与病灶相关的特征响应；二是 View-Weighted Fusion（VWF），通过学习样本依赖的权重，自适应地聚合三个视图的表示。最终将融合后的表示用于肺结节良恶性分类。文中未提供关于骨干网络结构、分割/掩码生成方式、预处理流程、优化器、学习率、训练轮数、损失函数或推理过程的具体细节。

## Evaluation

该框架在来自公共 LIDC-IDRI 数据集的 869 个结节上进行了评估，其中 448 个为良性、421 个为恶性。评估指标包括准确率、AUC 和 F1-score。结果表明，所提方法取得了 93.08% 的准确率、97.06% 的 AUC 和 92.68% 的 F1-score，并且这三个指标在基线比较所包含的模型中均为最高值。此外，作者进行了消融分析，显示 LGA 和 VWF 的组合在所评估配置中取得了最佳的整体平衡。文中还展示了测试用例的 Gradient-weighted Class Activation Mapping 可视化，表明学习到的响应主要集中在病灶相关区域内部或邻近区域。训练/验证/测试划分方式、交叉验证设置、具体基线模型名称以及统计检验均未在现有证据中报告。

## Innovation

作者声称的主要贡献在于将病灶引导的注意力机制（LGA）与视图加权融合机制（VWF）结合，用于肺结节的三视图分类。LGA 通过引入病灶掩码作为弱空间先验来细化病灶相关特征响应，而 VWF 学习样本依赖的视图权重以自适应聚合轴向、冠状和矢状表示，从而改善传统多视图融合方法未能考虑病灶特异性特征和各视图贡献差异的问题。

## Datasets

- LIDC-IDRI

## Metrics

- accuracy
- AUC
- F1-score

## Key Results

- 在 LIDC-IDRI 的 869 个结节（448 个良性、421 个恶性）上，所提框架达到 93.08% 的准确率。
- AUC 为 97.06%。
- F1-score 为 92.68%。
- 在基线比较所包含的模型中，所提方法的准确率、AUC 和 F1-score 均为最高值。
- 消融分析显示 LGA 与 VWF 的组合在所评估配置中提供了最佳的整体平衡。
- 展示的测试用例中，Gradient-weighted Class Activation Mapping 可视化表明学习到的响应主要集中在病灶相关区域内部或邻近区域。

## Limitations

现有证据中没有明确报告作者自行声明的局限性。基于证据不完整可推断出的限制包括：未提供训练/验证/测试划分、交叉验证或外部验证信息，难以评估泛化性和结果稳健性；未报告具体基线模型详情、统计显著性检验、置信区间或标准差；未提供模型复杂度、计算开销、掩码获取方式等实现细节，因此难以判断方法的可复现性和临床部署可行性。上述限制不应视为作者明确承认的局限性。

## Processing Notes

The PDF could not be fully processed. Analysis used the available arXiv metadata and other recoverable evidence.

- **PDF error:** HTTPError: 403 Client Error: Forbidden for url: https://europepmc.org/articles/PMC13577567?pdf=render
