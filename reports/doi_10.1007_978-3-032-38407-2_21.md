# Uncertainty-driven training for three-dimensional calibrated lung nodule classification

## Paper Information

- **Source:** arxiv
- **Paper ID:** 2609.20905v1
- **DOI:** 10.1007/978-3-032-38407-2_21
- **Venue:** Artificial Neural Networks and Machine Learning ICANN 2026
- **Authors:** Giuseppe Tripodi, Alessandro De Rosis, Saleh Rezaeiravesh
- **Published:** 2026-09-17T15:25:07Z
- **Updated:** 2026-09-17T15:25:07Z
- **Categories:** eess.IV, cs.CV
- **Landing URL:** http://arxiv.org/abs/2609.20905v1
- **PDF URL:** https://arxiv.org/pdf/2609.20905v1

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** full_text
- **Confidence:** high
- **PDF status:** Available

## Methodology

该论文提出一种面向三维CT肺结节分类的“不确定性驱动训练框架”。核心做法是：利用验证集上的逐类不确定性估计来动态调整各类别的损失权重，从而在训练中同时处理类别不平衡和概率校准问题。框架具体包含两条不确定性量化路径：其一为Monte Carlo Dropout（MCD），在分类头前加入p=0.5的dropout层，推理时保持dropout激活，通过K=20次随机前向传播估计逐类认知不确定性；其二为Evidential Deep Learning（EDL），将分类头替换为ReLU激活的证据头，基于Dirichlet分布（α_c=e_c+1）通过单次前向传播得到认知与偶然不确定性，损失由Bayesian risk项和KL正则项组成。权重更新公式为：¯w_c=¯u_c+μ/(a_c+λ)，并经过归一化、缩放和裁剪；权重在预热期后从验证集周期性更新，以避免与训练目标形成循环依赖。实验中还引入Calibration-aware training（CA）作为对比，即在focal loss基础上加入可微ECE代理项。训练完成后使用a posteriori温度缩放进一步校准概率。实验采用ResNet、DenseNet、EfficientNet、ViT3D和SwinViT3D五类3D骨干网络，使用AdamW、cosine annealing学习率、batch size 16、最多300 epoch和早停。输入方面，LIDC-IDRI结节约为48×48×48体素，NoduleMNIST3D被调整到64×64×64体素，均进行min-max归一化和3D数据增强（随机裁剪、旋转、翻转及强度调整）。

## Evaluation

评估在两个3D肺结节数据集上进行：LIDC-IDRI（经过筛选后共有809个结节，其中428例良性、381例恶性）和NoduleMNIST3D（1633个结节，1232良性、401恶性）。所有模型使用固定的分层70:15:15训练/测试/验证划分，且在患者级别进行划分以防止数据泄漏。训练策略包括focal loss基线（FL）、MCD、EDL和CA四种。性能指标包括ACC、precision、recall、F1和AUC；校准指标包括ECE、MCE和Brier Score；错误检测能力使用AUROC-ED。此外还报告了温度缩放前后的ECE对比、相对改善、训练时间开销和推理时间比较。定量结果显示：在LIDC-IDRI上AUC大致在0.62到0.96之间，多数配置高于0.90；MCD在ResNet18上ECE从0.106降至0.043（相对改善+59%），在DenseNet121上从0.119降至0.052（相对改善+56%）；EDL在DenseNet169上温度缩放后ECE为0.027。在NoduleMNIST3D上，EDL在ViT3D上AUC降至0.50、F1降至0.70，而baseline分别为0.83和0.83。关于统计检验，证据中未报告任何统计显著性检验。

## Innovation

论文的核心方法贡献在于将基于验证集的逐类不确定性估计整合进训练损失重加权过程，形成不确定性驱动训练框架。与常见的事后不确定性分析或像素级不确定性图不同，该框架利用验证集上计算得到的类别级不确定性作为代价信号，动态提高欠拟合且高不确定类别的损失权重；框架可适配MCD和EDL两种UQ方法，并共享相同的骨干网络结构。论文还考察了不确定性驱动训练与校准感知训练（CA）以及事后温度缩放的组合效果。需要说明的是，这些创新点均来自论文自身表述，所提供证据并未包含与先前工作的系统性对比以证明其新颖性或优先级。

## Datasets

- LIDC-IDRI
- NoduleMNIST3D

## Metrics

- Accuracy (ACC)
- Precision (PRE)
- Recall (REC)
- F1 score
- AUC
- Expected Calibration Error (ECE)
- Maximum Calibration Error (MCE)
- Brier Score (BS)
- AUROC-ED
- Risk-coverage curves
- Relative ECE improvement after temperature scaling

## Key Results

- 在LIDC-IDRI上，不确定性驱动训练的分类性能与常规训练相近，同时显著改善校准；ECE相对降幅最高可达约65%（摘要表述）。
- MCD在卷积骨干上校准提升最明显：DenseNet121的ECE相对改善约56%，ResNet18约59%，同时AUC分别保持在0.94和0.95以上。
- EDL在DenseNet169上取得温度缩放后最佳ECE=0.027；在ResNet50和注意力架构上表现不够稳定。
- 在LIDC-IDRI上多数配置AUC高于0.90，范围约为0.62至0.96；AUC最高0.95、F1最高0.91（按结论部分表述）。
- 在NoduleMNIST3D上，EDL在ViT3D上出现明显退化，AUC降至0.50、F1为0.70，而baseline分别为0.83和0.83。
- 温度缩放在几乎所有配置下都显著降低ECE，相对改善通常在约25%至60%之间；baseline模型也从温度缩放中获益最大。
- 在LIDC-IDRI上，CA训练获得最高AUROC-ED（0.696）和接近最高的post-calibration accuracy（0.833）；FL准确率类似（0.835），AUROC-ED为0.668。
- 在NoduleMNIST3D上，FL获得最佳AUROC-ED（0.697），CA获得最高准确率（0.847）但AUROC-ED最低（0.581），表明直接最小化校准误差不自动产生有用的错误检测信号。
- EDL的训练时间开销较小（DenseNet约20-30%，ResNet低于15%），推理比MCD快约70-80%；MCD训练时间比baseline高约100-150%（DenseNet）或50-70%（ResNet）。

## Limitations

作者明确指出的局限性包括：（1）评估仅限于二分类任务，即LIDC-IDRI的良恶性分类和NoduleMNIST3D的二类结节检测，尚未在多类别或多标签任务中验证校准收益的泛化性；（2）不确定性重加权只在数据集层面的类别级别进行，没有对单个样本或图像内空间区域进行自适应加权，可能对具有细粒度类间结构的任务不够有效；（3）EDL在transformer架构（如NoduleMNIST3D上的ViT3D）上的性能退化原因尚不清楚；（4）MCD推理需要K=20次随机前向传播，可能限制实时部署。此外，从现有证据来看，部分评估细节未被完整报告：例如未提供重复实验次数或交叉验证设置、未报告统计显著性检验、未给出除总体描述外的确定性误差范围。这些属于证据不完整导致的推断性局限，而非作者明确声明的局限。
