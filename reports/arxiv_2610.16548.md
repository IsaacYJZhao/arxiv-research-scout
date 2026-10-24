# NoduleFlow: Automatic 3D Lung Nodule Detection and Segmentation

## Paper Information

- **Source:** arxiv
- **Paper ID:** 2610.16548v1
- **DOI:** Not reported in the available evidence.
- **Venue:** Not reported in the available evidence.
- **Authors:** Giulia Romoli, Filippo Ruffini, Francesco Di Feola, Valerio Guarrasi, Matteo Tortora, Paolo Soda
- **Published:** 2026-10-12T10:30:54Z
- **Updated:** 2026-10-12T10:30:54Z
- **Categories:** cs.CV
- **Landing URL:** http://arxiv.org/abs/2610.16548v1
- **PDF URL:** https://arxiv.org/pdf/2610.16548v1

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** partial_text
- **Confidence:** high
- **PDF status:** Available

## Methodology

本文提出 NoduleFlow，一个用于从系列 CT 容积中自动进行肺结节检测、分类和分割的框架。该框架由四个独立预训练模块依次组成：（1）Detection Module（DM），使用 3D RetinaNet，对每个 CT 容积独立处理，生成候选检测框 bi 和检测置信度 si；（2）Classification Module（CM），使用 3D ResNet50-SWS，为每个候选额外生成恶性概率 mi；对空间重叠候选进行合并，并用 si = 1 - ∏(1 - sij)、mi = 1 - ∏(1 - mij) 重算分数；（3）Transfer Module（TM），使用 GradICON 估计成对扫描间的微分同胚配准场 Φ，并将候选框跨时间传播；提出了三种聚合策略：S0 不做时间传播，S1 仅聚合既往时间点，S2 聚合所有可用时间点；（4）Segmentation Module（SM），使用 LesionLocator（一个可提示的 3D UNet），以 TM 提供的精化边界框或边界框几何中心点作为提示，从原始 CT 容积生成结节分割掩膜。所有模块均以作者发布的原始冻结权重使用，没有联合训练、微调或任务特定适配。预处理方面，使用 TotalSegmentator 生成的掩膜将 CT 裁剪到肺区；所有随访 CT Vi>0 被处理以匹配基线 V0 的空间分辨率和图像尺寸。

## Evaluation

评估使用四个独立数据集，共 481 名患者、1266 次扫描和 4593 个标注肺结节作为测试集：NLST-Sybil（146 名患者，398 个结节）、NLST-LongCT（97 名患者，110 个结节）、Longitudinal-CT（169 名患者，2166 个标注肺转移灶）、UniToChest（69 名患者，1919 个结节）。检测使用 Competition Performance Metric（CPM，定义为 1/8、1/4、1/2、1、2、4、8 FP/scan 下的平均敏感度）及 8 FP/scan 时的敏感度；分类使用 ROC AUC；分割在 Longitudinal-CT 和 UniToChest 上使用 Dice Similarity Coefficient（DSC），在 NLST-Sybil 上使用 Intersection over Union（IoU），在 NLST-LongCT 上使用 hit rate。结果与 TotalSegmentator（TS）、NoduleNet（NNet，在 LIDC-IDRI 上重新训练）和 MedSAM2（MS2，以真值标注作为 oracle 提示）比较。检测评估了三个 DM 变体：在 DLCS 上训练的 RetinaNet（D-De）、在 LUNA16 上训练的 RetinaNet（L-De）及其集成（ENS）。后续 CM、TM、SM 模块使用集成输出评估。对于 Longitudinal-CT 和 UniToChest，还报告了限制为每容积少于 6 个病灶（≤6 Ls/scan）子集的结果。

## Innovation

本文提出的主要贡献是构建了一个由四个独立预训练模块组成的全自动 3D 肺结节检测、分类和分割框架，在推理时不依赖先验病灶标注、人工初始化或 ROI 预选。其核心创新在于通过 Transfer Module 利用跨扫描配准场将候选 ROI 沿纵向随访扫描传播，从而将纵向信息引入检测/定位环节，并将纵向聚合候选用于后续分割；文章明确研究这种纵向传播策略（S0、S1、S2）相对于传统逐扫描独立分析是否能改善结节定位。论文声称据其所知，此前没有端到端方案同时结合纵向建模，但这一说法仅作为论文自身陈述的证据呈现。

## Datasets

- NLST-Sybil
- NLST-LongCT
- Longitudinal-CT
- UniToChest
- DLCS (Duke Lung Cancer Screening)
- LUNA16
- LIDC-IDRI

## Metrics

- CPM (Competition Performance Metric)
- Sensitivity at 8 FP/scan
- AUC
- DSC
- IoU
- hit rate

## Key Results

- 在检测上，集成检测器 ENS 在多数数据集上 CPM 最高：NLST-Sybil 70.9%，NLST-LongCT 36.8%，分别优于 NNet 的 44.7% 和 27.0%；但 NNet 在 Longitudinal-CT（38.0% vs 19.0%）和 UniToChest（28.1% vs 25.9%）上仍优于 ENS。
- UniToChest 限制为 ≤6 Ls/scan 时，ENS 的 CPM 从 25.9% 提高到 72.0%；该子集病灶中位直径从 5mm（IQR:3-8mm）增加到 12mm（IQR:6-22mm）。Longitudinal-CT 限制后 CPM 仅从 19.0% 提高到 26.9%。
- 在 8 FP/scan 敏感度上，ENS 在 NLST-Sybil 达到 78.9%，NLST-LongCT 43.6%，UniToChest 30.3%，Longitudinal-CT 26.6%；NNet 对应为 76.9%、48.7%、47.6% 和 66.9%。
- 3D ResNet50-SWS 分类模块的 AUC 分别为：NLST-Sybil 92.1%，NLST-LongCT 95.6%，Longitudinal-CT 90.4%，UniToChest 90.4%。
- 分割中，点提示策略在 Longitudinal-CT 和 UniToChest 上普遍优于框提示。例如 Longitudinal-CT 大结节 S0-P DSC 79.3% 对比 S0-B 60.4%；UniToChest 大结节 S0-P 77.4% 对比 S0-B 66.0%。
- 纵向聚合对大结节有益：Longitudinal-CT 上大结节最高 DSC 为 S2-P 的 80.1%，高于 S0-P 79.3% 和 S1-P 79.9%；NLST-Sybil 大结节最高 IoU 为 S2-B 的 37.2%。对小病灶纵向传播收益有限，例如 Longitudinal-CT 小结节 S0-P DSC 77.6% 优于 S2-P 74.1%。
- 与 TotalSegmentator 相比，本框架在 Longitudinal-CT 小结节上 DSC 更高（S0-P 77.6% vs TS 58.8%），但在 Longitudinal-CT 大结节上 TS 更高（80.2% vs S0-P 79.3%）；在 UniToChest 两个尺寸类别均高于 TS；在 NLST-Sybil IoU 和 NLST-LongCT 小病灶 hit rate 上明显优于 TS。
- 与 NoduleNet 相比，本框架在 Longitudinal-CT 和 UniToChest 两个尺寸类别的 DSC 均大幅更高，例如 Longitudinal-CT 小结节 S0-P 77.6% vs 53.5%，UniToChest 大结节 S0-P 77.4% vs 59.4%。
- MedSAM2 在 oracle 提示设置下在所有数据集和尺寸类别上取得最高分割指标，被作为提示驱动分割性能的近似上界，例如 Longitudinal-CT DSC 87.7%（<1cm）和 89.0%（≥1cm），NLST-Sybil IoU 86.6%（<1cm）和 90.6%（≥1cm）。

## Limitations

作者明确指出的局限包括：检测性能受病灶数量和大小影响很大；小转移灶检测仍然是关键局限；未来可通过针对转移灶和小结节分布微调专门检测模型来改进；研究受限于公开可用的纵向标注数据集数量有限。此外，NLST-LongCT 仅有一个时间点有结节标注，因此 S1 和 S2 聚合策略在该数据集上不适用。另有局限来自证据本身：作者在结论中提到未来改进方向属于作者明确陈述，但具体训练数据量、扫描级样本分布、统计显著性检验等信息在所提供的证据中未报告。
