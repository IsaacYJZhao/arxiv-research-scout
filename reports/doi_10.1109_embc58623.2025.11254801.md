# Exploring Attention-Driven Deep Learning for Accurate Lung Nodule Segmentation

## Paper Information

- **Source:** arxiv
- **Paper ID:** 2611.29450v1
- **DOI:** 10.1109/EMBC58623.2025.11254801
- **Venue:** 2025 47th Annual International Conference of the IEEE Engineering in Medicine and Biology Society (EMBC), 2025
- **Authors:** Nima Shafiei Rezvani Nezhad, Meysam Mansouri, Saeid Ghayour, Ruhollah Abolhasani, Shahla Azizi
- **Published:** 2026-11-22T12:50:30Z
- **Updated:** 2026-11-22T12:50:30Z
- **Categories:** cs.CV
- **Landing URL:** http://arxiv.org/abs/2611.29450v1
- **PDF URL:** https://arxiv.org/pdf/2611.29450v1

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** full_text
- **Confidence:** medium
- **PDF status:** Available

## Methodology

本研究提出了一套用于肺结节分割的深度学习流程。预处理阶段包括：使用K-means聚类（k=2）提取肺组织区域，通过腐蚀和膨胀等形态学操作细化肺部掩膜，应用中值滤波和各向异性扩散进行降噪，将像素强度归一化到[0,1]，并基于细化后的肺部掩膜边界框进行裁剪。分割模型均采用编码器-解码器框架，评估了多种架构，包括DPLinkNet50 + Channel Attention Bridge（CAB）、LinkNet、DPLink、U-Net + CAB、U-Net + VPM + CAB、ResDense with Channel Attention、Dilated U-Net、EfficientUNet、AAU-Net和U-Net3Plus。其中，DPLinkNet50以ResNet-50作为编码器，结合LinkNet轻量解码器，并加入CAB模块，通过全局平均池化和可学习权重对特征图进行动态加权。训练采用监督学习，使用二元交叉熵（BCE）损失函数，Adam优化器，学习率为1e-5，批量大小为4，训练150个epoch，并对卷积层应用权重归一化。数据增强包括随机旋转、翻转和强度变化。

## Evaluation

实验使用LIDC-IDRI数据集的一个筛选子集，包含356个样本。评估指标为Dice相似系数（DSC）。具体报告的分割性能（Dice score）为：DPLinkNet50 + Channel Attention Bridge为0.86，LinkNet为0.84，DPLink为0.78，U-Net + Channel Attention Bridge为0.68，U-Net + VPM + Channel Attention Bridge为0.66，ResDense with Channel Attention为0.65，Dilated U-Net为0.5773。文中未报告训练/验证/测试划分方式、交叉验证设置或统计检验。方法部分提到EfficientUNet、AAU-Net和U-Net3Plus也进行了评估，但结果表中未提供这些模型的定量Dice分数。

## Innovation

作者强调的核心贡献是在LIDC-IDRI数据集的一个筛选子集（356个样本）上，利用数据高效策略和定制架构实现肺结节分割。主要技术创新是在DPLinkNet50编码器-解码器结构中引入Channel Attention Bridge（CAB），通过通道注意力机制动态加权特征图，以强调关键区域。此外，还结合了包括K-means聚类、形态学操作、中值滤波和各向异性扩散在内的预处理流程。

## Datasets

- LIDC-IDRI

## Metrics

- Dice Similarity Coefficient (DSC)

## Key Results

- DPLinkNet50 + Channel Attention Bridge在肺结节分割中取得了最高的Dice score，为0.86。
- LinkNet的Dice score为0.84。
- DPLink的Dice score为0.78。
- U-Net + Channel Attention Bridge的Dice score为0.68。
- U-Net + VPM + Channel Attention Bridge的Dice score为0.66。
- ResDense with Channel Attention的Dice score为0.65。
- Dilated U-Net的Dice score为0.5773。
- 结果显示DPLinkNet50 + Channel Attention Bridge优于所比较的其他架构。

## Limitations

作者明确指出的局限性包括：依赖较小的数据集（356个样本的筛选子集）以及某些模型的计算需求较高，这对更广泛的适用性构成挑战；此外，需要外部数据集进行进一步验证以确保鲁棒性和泛化性。基于现有证据无法确定的内容包括：具体的数据筛选标准、训练/验证/测试划分方式、EfficientUNet、AAU-Net和U-Net3Plus的定量结果，以及统计显著性检验。
