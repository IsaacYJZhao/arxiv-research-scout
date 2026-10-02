# Evaluating Multi-Task Morphological Concept Learning for Pulmonary Nodule Malignancy Assessment in 3D CT

## Paper Information

- **Source:** arxiv
- **Paper ID:** 2609.38271v1
- **DOI:** Not reported in the available evidence.
- **Venue:** Not reported in the available evidence.
- **Authors:** Namitha Narayanan
- **Published:** 2026-09-29T14:36:41Z
- **Updated:** 2026-09-29T14:36:41Z
- **Categories:** cs.CV
- **Landing URL:** http://arxiv.org/abs/2609.38271v1
- **PDF URL:** https://arxiv.org/pdf/2609.38271v1

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** partial_text
- **Confidence:** high
- **PDF status:** Available

## Methodology

本研究使用 LIDC-IDRI 数据集的 lesion-centred 3D CT 体积，比较单任务与多任务 3D CNN 对肺结节恶性风险进行分类的效果。作者将 malignancy ratings 1、2 定义为低风险（负类），4、5 定义为高风险（正类），排除 rating 3。实验单位为 reader-level nodule annotation，而非 consensus lesion，并采用 patient-level splitting 防止数据泄漏。CT 预处理包括：从 DICOM 重建 3D 体积、按 SOP UID 对齐 XML 轮廓、根据 ROI 轮廓点估计病灶中心、提取 spacing-aware 3D crop、重采样至 1 mm 各向同性并固定为 64×64×64 体素，区域外以 -1000 HU 填充，HU 裁剪至 [-1000, 400] 并进行 min-max 归一化到 [0,1]。单任务模型使用紧凑 3D CNN，包含三个 3D 卷积层（16、32、64 通道，3×3×3 kernel，stride 1，padding 1，ReLU），前两层后接 2×2×2 max pooling，最后使用 adaptive average pooling 得到 64 维特征，并由一个线性层输出单一 logit；未使用 dropout 或归一化层，训练参数为 69,729。多任务模型使用相同 encoder，并增加三个独立线性输出头，分别预测 malignancy risk、spiculation 和 lobulation；训练参数为 69,859。每个任务使用 binary cross-entropy with logits loss 和基于负/正训练样本比例的正类权重；总体训练损失为每个 batch 中可用任务损失的均值。辅助标签 rating 为 3、缺失或不可用时从对应 auxiliary loss 中掩蔽排除，但样本仍保留用于 malignancy risk 预测。模型使用 PyTorch 实现，固定随机种子 42，batch size 为 2，训练时不 shuffle，Adam 优化器学习率 0.001，训练 5 个 epoch，不使用学习率调度或 early stopping；根据 validation malignancy loss 保留 checkpoint。决策阈值通过 validation set 上最大化 balanced accuracy 获得；多任务模型的三个任务分别独立计算阈值。

## Evaluation

数据来自 LIDC-IDRI，共 3,918 个 reader-level nodule annotations，来自 742 名患者。patient-level splitting 后训练集为 519 名患者/2,754 条标注，验证集为 111 名患者/536 条标注，测试集为 112 名患者/628 条标注。恶性风险分布为训练集负/正 1,754/1,000，验证集 294/242，测试集 375/253。评估指标包括 accuracy、balanced accuracy、sensitivity、specificity、PPV、NPV、F1 score、ROC-AUC 和 average precision，并分析 confusion matrix。单任务模型在测试集上 ROC-AUC 为 0.552，average precision 为 0.431，balanced accuracy 为 0.548，accuracy 为 0.490，sensitivity 为 0.842，specificity 为 0.253，PPV 为 0.432，NPV 为 0.704，F1 为 0.571；决策阈值为 0.492，混淆矩阵为 95 true negatives、280 false positives、40 false negatives、213 true positives。多任务模型 malignancy head ROC-AUC 为 0.558，average precision 为 0.443，balanced accuracy 为 0.539，accuracy 为 0.484，sensitivity 为 0.822，specificity 为 0.256，PPV 为 0.427，NPV 为 0.681，F1 为 0.562；决策阈值为 0.503，混淆矩阵为 96 true negatives、279 false positives、45 false negatives、208 true positives。辅助任务上，spiculation 有 584 条有效记录，其中 67 条阳性，ROC-AUC 为 0.546，average precision 为 0.137，balanced accuracy 为 0.499，sensitivity 为 0.030，specificity 为 0.969，F1 为 0.047；lobulation 有 557 条有效记录，其中 50 条阳性，ROC-AUC 为 0.480，average precision 为 0.088，balanced accuracy 为 0.464，sensitivity 为 0.560，specificity 为 0.369，F1 为 0.141。两者比较显示多任务相对单任务在 ROC-AUC 上差异为 +0.005，average precision 差异为 +0.012，balanced accuracy 差异为 -0.009，accuracy 差异为 -0.006，sensitivity 差异为 -0.020，specificity 差异为 +0.003，PPV 差异为 -0.005，NPV 差异为 -0.023，F1 差异为 -0.009。使用 2,000 次 paired patient-level bootstrap 分析，ROC-AUC 差异 95% CI 为 -0.087 至 0.090，average precision 差异 95% CI 为 -0.071 至 0.093，balanced accuracy 差异 95% CI 为 -0.067 至 0.043；三个置信区间均包含零。此外按 CT slice thickness 进行 subgroup 分析：≤2 mm 组 68 名患者/366 条记录，单任务 ROC-AUC/balanced accuracy 为 0.555/0.555，多任务为 0.536/0.539；>2 mm 组 44 名患者/262 条记录，单任务为 0.539/0.531，多任务为 0.586/0.519。未进行额外假设检验或 p 值计算。

## Innovation

作者的主要技术贡献是通过一个受控比较评估多任务形态学概念学习对肺结节恶性风险分类的影响：单任务和多任务模型共享完全相同的 3D CNN encoder，多任务模型仅额外增加 spiculation 和 lobulation 两个独立预测头。该设计旨在直接检验在保持底层特征提取器不变的情况下，学习 radiologist-annotated 形态学特征是否能改善主要恶性风险预测，而不引入其他架构或特征融合变化。

## Datasets

- LIDC-IDRI

## Metrics

- accuracy
- balanced accuracy
- sensitivity
- specificity
- positive predictive value (PPV)
- negative predictive value (NPV)
- F1 score
- ROC-AUC
- average precision
- 95% confidence interval

## Key Results

- 多任务模型未能在主恶性风险分类任务上产生明确且一致的改善。
- 单任务模型在测试集 ROC-AUC 为 0.552，balanced accuracy 为 0.548；多任务模型 ROC-AUC 为 0.558，balanced accuracy 为 0.539。
- 多任务相对单任务的 ROC-AUC 差异为 +0.005，average precision 差异为 +0.012，balanced accuracy 差异为 -0.009。
- 患者水平 bootstrap 分析显示 ROC-AUC 差异的 95% CI 为 -0.087 至 0.090，balanced accuracy 差异的 95% CI 为 -0.067 至 0.043，置信区间均包含零。
- 辅助形态学任务的预测性能有限：spiculation ROC-AUC 为 0.546、balanced accuracy 为 0.499、F1 为 0.047；lobulation ROC-AUC 为 0.480、balanced accuracy 为 0.464、F1 为 0.141。
- 辅助标签强烈不平衡：spiculation 有 67/584 条阳性记录，lobulation 有 50/557 条阳性记录。
- 按 CT 层厚分析，在 ≤2 mm 组，单任务 ROC-AUC/balanced accuracy 为 0.555/0.555，多任务为 0.536/0.539；在 >2 mm 组，单任务为 0.539/0.531，多任务为 0.586/0.519。该亚组分析是探索性的，不足以证明层厚效应。

## Limitations

作者明确指出的局限性包括：1）预测目标基于 reader-assessed malignancy ratings，而非 histopathologically confirmed diagnosis，标注本身存在 reader-level 变异性和不确定性；多个 reader 标注可能对应同一底层病灶，因此模型应被解释为预测放射科医生评估的恶性风险，而非确认患者是否患癌。2）二分类实验排除了 malignancy rating 3 的 indeterminate cases，简化了分类问题，但可能移除临床上重要的不确定病例并影响性能。3）辅助形态学任务受标签限制，spiculation 和 lobulation 阳性样本相对较少，部分标注不可用或被排除，导致难以判断多任务学习改善有限是任务设计本身所致，还是辅助目标中的不确定性和不平衡所致。4）所有实验仅在单个公开数据集上进行，未在来自其他机构或采集环境的数据上外部验证；扫描仪特性、重建协议、人群特征或标注实践的差异可能影响模型行为，结果不应被假定可推广到其他数据集或临床环境。另有可从证据中推断但作者未明确作为局限列出的信息：亚组分析样本量较小且为探索性，未进行假设检验或 p 值计算。
