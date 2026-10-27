# 3D-DDN Faster R-CNN: Pulmonary Nodule Detection Through Cross-Slice Feature Fusion and Dynamic Displacement Modeling

## Paper Information

- **Source:** europepmc
- **Paper ID:** 42902040
- **DOI:** 10.1007/s10278-026-02432-x
- **Venue:** Journal of imaging informatics in medicine
- **Authors:** Guan C, Yang D, Leng Z, Liu S, Zu A, Luo D, Chen H, Wang J
- **Published:** 2026-10-20
- **Updated:** 2026-10-20
- **Categories:** Multi-slice Ct, Pulmonary Nodule Detection, Faster R-cnn, Cross-slice Feature Fusion, Dynamic Displacement Constraint
- **Landing URL:** https://doi.org/10.1007/s10278-026-02432-x
- **PDF URL:** Not reported in the available evidence.

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** abstract_only
- **Confidence:** medium
- **PDF status:** No full text available; abstract only

## Methodology

本文提出 3D-DDN Faster R-CNN，一种在二维两阶段检测器中引入局部三维上下文的多切片肺结节检测框架。方法包含三个明确描述的主要组件：1) 五切片交互混合（5-SIB）策略，将五个连续 CT 切片组织为有序的上下文组，并由共享的二维骨干网络提取保留切片特定性的特征流；2) 跨切片特征融合（CSFF）模块，在浅层特征级别使用逐切片空间自注意力，在深层特征和感兴趣区域级别使用可学习的跨切片聚合；3) 动态位移约束（DDC），利用正样本回归损失和基于间隔的负样本对比损失，对相邻切片间的提议位移进行建模。此外，使用类别加权 focal loss 缓解前景-背景类别不平衡。论文摘要未报告具体的骨干网络结构、优化器、学习率、训练轮数、损失函数具体形式、参数规模、推理时间等实现细节。

## Evaluation

模型在三个数据集上使用患者级数据划分进行评估：一个私有医院数据集、LIDC-IDRI 和 LNDb。实验设计包括主要检测性能比较和消融实验。消融实验表明，直接的五个切片堆叠会降低性能，而结构化特征融合与位移监督能够恢复性能损失并改善整体检测表现。摘要中报告了私有医院数据集上的 AP0.5 为 75.80% ± 1.05%，敏感度为 89.33% ± 1.91%，CPM 为 91.20% ± 1.50%；LIDC-IDRI 上 AP0.5 为 66.27% ± 0.45%；LNDb 上 AP0.5 为 48.20% ± 0.30%。摘要未报告各数据集的样本规模、患者数、扫描数、结节数、训练/验证/测试划分比例、基线方法、统计检验及消融实验的具体数值结果。

## Innovation

本文的主要技术创新在于将局部三维上下文以结构化方式整合到二维 Faster R-CNN 检测框架中：通过 5-SIB 有序上下文分组、CSFF 分层跨切片特征融合，以及 DDC 对提议在相邻切片间位移的显式建模，构建多切片肺结节检测方案。摘要指出，这些机制提供了补充性的局部三维上下文信息；消融实验支持位移监督和结构化的特征融合相对于直接切片堆叠具有性能优势。摘要未对该方法作出‘首创’或‘最优’等超出证据的定性声明。

## Datasets

- private hospital dataset
- LIDC-IDRI
- LNDb

## Metrics

- AP0.5
- sensitivity
- CPM

## Key Results

- 在私有医院数据集上，3D-DDN 的 AP0.5 为 75.80% ± 1.05%，敏感度为 89.33% ± 1.91%，CPM 为 91.20% ± 1.50%。
- 在 LIDC-IDRI 上，AP0.5 为 66.27% ± 0.45%。
- 在 LNDb 上，AP0.5 为 48.20% ± 0.30%。
- 消融实验显示，直接的五个切片堆叠会降低性能，而结构化特征融合和位移监督可以恢复该性能损失并改善整体检测表现。
- 作者认为，有序跨切片表示、分层特征融合和提议位移监督为引入局部三维上下文提供了互补机制。

## Limitations

作者明确指出的局限性：肺结节检测在单个轴向切片上具有挑战性，因为小结节和低对比度结节可能与血管及其他解剖结构相似。基于现有证据可推断但作者未明确说明的局限性：摘要未提供三个数据集的具体规模和组成、基线对比方法、统计检验、消融实验的具体数值、模型在更大或外部数据上的泛化性分析，也未报告计算成本、推理时间或临床部署相关限制；这些无法从摘要内容确定。

## Processing Notes

The PDF could not be fully processed. Analysis used the available arXiv metadata and other recoverable evidence.

- **PDF error:** No downloadable full text is available for this record.
