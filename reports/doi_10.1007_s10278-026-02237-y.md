# Resolution-Aware Evidential Fusion for Scale-Invariant Attribution in 3D Lung Nodule Detection

## Paper Information

- **Source:** europepmc
- **Paper ID:** 42675277
- **DOI:** 10.1007/s10278-026-02237-y
- **Venue:** Journal of imaging informatics in medicine
- **Authors:** Haddar B, Elleuch MA
- **Published:** 2026-08-31
- **Updated:** 2026-08-31
- **Categories:** Computer-aided Diagnosis, Imaging Informatics, Explainable Artificial Intelligence, 3D Convolutional Neural Networks, Dempster–shafer Fusion, Scale-invariant Explainability
- **Landing URL:** https://doi.org/10.1007/s10278-026-02237-y
- **PDF URL:** Not reported in the available evidence.

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** abstract_only
- **Confidence:** low
- **PDF status:** No full text available; abstract only

## Methodology

作者提出 Evidential Dempster-Shafer Fusion (EDSF) 框架，用于将两类事后归因证据结合到信念函数形式中：一是基于激活的空间先验，二是体素级路径积分归因。该框架被实例化应用于 3D 肺结节分析，使用在 LUNA16 上训练的 3D ResNet-18 作为基础模型。EDSF 通过非线性组合这两个来源地图来生成归因。文中还提到在同样的两个来源地图上进行了消融实验，以检验尺度不变性是否来自非线性组合而非来源地图的选择。提供的证据未包含更详细的预处理、训练策略、优化器、损失函数、推理流程或具体信念组合公式。

## Evaluation

评估使用在 LUNA16 上训练的 3D ResNet-18，报告了 97.2% 的准确率和 0.991 的平均 ROC-AUC，采用患者级交叉验证。在包含 200 个候选的冻结队列上，将 EDSF 与 Grad-CAM、GradCAM++、Integrated Gradients、Shapley additive explanations 和 Occlusion Sensitivity 五种基线进行比较，涉及忠实性、定位性、稳定性和紧凑性七项指标。评估还分析了定位质量与结节直径的依赖关系，并使用等价性检验而非非显著性 p 值来支持无依赖性的零结果。此外进行了消融实验，以及基于权重的敏感性分析的复合指数。提供的证据未报告数据集划分比例、样本数、统计检验细节、各指标对各方法的具体数值或基线完整性能表。

## Innovation

作者提出的核心贡献是 Evidential Dempster-Shafer Fusion (EDSF)，将基于激活的空间先验与体素级路径积分归因在信念函数形式下进行融合，以解决激活图空间粗糙而梯度归因不稳定、以及梯度加权激活图定位质量随病灶尺寸变化的问题。其创新点在于通过非线性组合实现尺度不变的归因，并用等价性检验支持定位质量对结节直径无依赖这一零结果。证据未包含对其相对于以往方法的普遍优越性或首创性的明确声明。

## Datasets

- LUNA16

## Metrics

- accuracy
- ROC-AUC
- faithfulness
- localisation
- stability
- compactness
- composite index
- equivalence test margin

## Key Results

- 3D ResNet-18 在 LUNA16 上达到 97.2% 准确率和 0.991 平均 ROC-AUC（患者级交叉验证）。
- 在 200 个候选的冻结队列上，所有五种基线的定位质量都随结节直径变化。
- EDSF 的定位质量对结节直径没有可检测的依赖。
- 等价性检验显示，EDSF 的数据支持的最小边界为 0.298，而基线为 0.738 至 0.937，因此实际独立性在中等边界下成立，但在更紧的边界下不成立。
- 消融实验表明，尺度不变性来自非线性组合，而非来源地图的选择。
- 复合指数敏感性分析显示，在大多数权重设置下 Occlusion Sensitivity 更受青睐，EDSF 仅在稳定性和紧凑性权重较大时更受青睐。

## Limitations

作者在提供的证据中通过等价性检验结果说明了 EDSF 的实际独立性仅在中等边界下成立，而在更紧的边界下不成立；同时复合指数敏感性分析表明，EDSF 在大多数权重设置下并非最优，仅在稳定性和紧凑性权重较大时优于其他方法。因证据仅限于摘要，未报告更多方法学或实验细节，因此无法评估训练协议、数据集划分、统计检验具体设置、各指标具体数值或泛化性等方面的局限。

## Processing Notes

The PDF could not be fully processed. Analysis used the available arXiv metadata and other recoverable evidence.

- **PDF error:** No downloadable full text is available for this record.
