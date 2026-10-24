# L2GSSL: Label-Efficient Local-to-Global Self-Supervised Learning for Volumetric Healthcare Data

## Paper Information

- **Source:** arxiv
- **Paper ID:** 2610.21356v1
- **DOI:** Not reported in the available evidence.
- **Venue:** Not reported in the available evidence.
- **Authors:** Po-Cheng Cheng, Hung-Hsuan Chen
- **Published:** 2026-10-15T06:37:47Z
- **Updated:** 2026-10-15T06:37:47Z
- **Categories:** cs.CV, cs.LG
- **Landing URL:** http://arxiv.org/abs/2610.21356v1
- **PDF URL:** https://arxiv.org/pdf/2610.21356v1

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** full_text
- **Confidence:** high
- **PDF status:** Available

## Methodology

L2GSSL 是一种面向三维医用容积数据的局部到全局自监督预训练框架。输入 CT 容积被表示为有序切片序列 V=[s1,...,sZ]，局部编码器 fl 对每一切片生成局部嵌入 zl,i，全局编码器 fg 再聚合并建模有序局部 token，得到容积级表示 zg。局部与全局两个表示空间均采用 VICReg 目标，分别优化切片级不变性、方差和协方差项，即 Ll 与 Lg，总体预训练目标为 L=Ll+Lg。关键机制是在局部嵌入进入全局编码器之前施加 stop-gradient，使得局部嵌入在前向传播中参与容积构建，但全局损失不回传更新局部编码器，从而实现局部与全局表示空间的分离优化。为降低 GPU 峰值显存，L2GSSL 采用 slice-wise 执行：切片按小组顺序前向，局部嵌入按解剖顺序累积后再进行全局编码。训练采用三阶段调度：前 30% epoch 仅优化局部目标，随后 40% epoch 联合优化局部和全局目标，最后 30% epoch 冻结局部编码器并仅优化全局目标。文中以 MST（DINOv2 初始化的 ViT 切片编码器加切片 transformer）和 MaxViT（前两阶段作为局部编码器，后两阶段作为全局编码器）两种骨干实现该框架。数据预处理包括将 CT 值裁剪到 [-1000,1000] HU 并缩放到 [-1,1]，必要时重采样，并使用最小容积强度进行 crop-or-pad。自监督视图采用随机 gamma 校正、低频强度失真、高斯模糊、仿射变换和高斯噪声等增强。预训练后丢弃投影头，将预训练容积表示用于下游分类器。

## Evaluation

实验主要围绕 LIDC-IDRI 肺结节恶性分类展开，按照病例/扫描层面划分数据，处理得到 1625 个结节样本；下游微调分别使用 10%、25% 和 100% 的训练标签，对应 104、260 和 1040 个结节。比较方法包括监督 MST-DINOv2、MoCo v2、SimSiam、volume-level VICReg 和 L2GSSL，在相同骨干和流程下评估。评价指标为 AUROC 和 AUPRC。下游评估包括固定 batch size 的线性探测、峰值 VRAM 限制在 47–48 GB 的线性探测、不同标签比例的全微调，以及直接跨数据集 LNDb 评估（仅用 25% LIDC-IDRI 标签微调，不做 LNDb 适应）。另外，L2GSSL 初始化被集成到 RSNA 2023 腹部创伤检测竞赛第二名方案的多专家流程中，使用 AbdomenCT-1K 作为额外无标注腹部 CT 预训练数据；该部分报告 severity-weighted RSNA competition loss。还进行了与完全 3D 参考方法 VoCo 的比较、MaxViT 骨干可移植性实验、 lesion-slice masking 行为分析、radiologist ROC 分析、组件消融和投影头归一化敏感性分析。线性探测使用三个种子，微调使用五次运行。文中报告了多个具体数值结果，例如 L2GSSL 在 LIDC-IDRI 10% 标签时 AUROC 0.9229、AUPRC 0.8769，25% 标签时 AUROC 0.9377、AUPRC 0.9003；直接 LNDb 评估 AUROC 0.8138、AUPRC 0.7589；RSNA 多专家流程 competition loss 从 0.3597 降至 0.3551。在 VoCo 对比中报告 L2GSSL 峰值 VRAM 为 24.37–24.48 GB，低于 VoCo 的 27.57 GB。

## Innovation

作者提出的核心方法是 L2GSSL，其主要技术贡献在于将三维容积自监督预训练显式分解为局部切片表示空间和全局容积表示空间，并分别施加独立的 VICReg 目标。与仅在最终容积表示上附加损失的常规方法不同，L2GSSL 通过 stop-gradient 建立单向依赖：局部嵌入前向输入全局编码器，但全局损失不更新局部编码器，从而防止全局目标覆盖切片级结构。此外，结合 slice-wise 分组执行和三阶段局部/全局优化调度，使层次化预训练能够在受限 GPU 显存下进行。作者声称该方法在标签稀缺时提升最大，且随标签增加增益减小。文中没有使用'首次提出'或'state-of-the-art'等绝对新颖性表述，贡献描述集中于所提出的框架、资源受限训练程序及其在不同任务和骨干下的评估。

## Datasets

- LIDC-IDRI
- LNDb
- RSNA 2023 Abdominal Trauma Detection
- AbdomenCT-1K

## Metrics

- AUROC
- AUPRC
- accuracy-like sensitivity/false-positive pooled operating point
- malignant true-positive rate
- peak VRAM
- severity-weighted RSNA competition loss

## Key Results

- 在 LIDC-IDRI 全微调实验中，L2GSSL 在 10% 标签下 AUROC 为 0.9229±0.0100、AUPRC 为 0.8769±0.0042，25% 标签下 AUROC 为 0.9377±0.0039、AUPRC 为 0.9003±0.0064，均高于 volume-level VICReg；相对 volume-level VICReg 的 AUROC 增益分别为 0.0229 和 0.0294。
- 在 LIDC-IDRI 100% 标签全微调下，监督 MST-DINOv2 取得最高 AUROC 0.9448±0.0070，仅比 L2GSSL 的 0.9404±0.0024 高 0.0044；SimSiam 取得最高 AUPRC 0.9123±0.0055。
- 在 LIDC-IDRI 相同 batch size 线性探测中，L2GSSL 达到 AUROC 0.8875±0.0061、AUPRC 0.8111±0.0118，优于 volume-level VICReg 的 0.8485±0.0092 和 0.7740±0.0109。
- 在直接 LNDb 外部评估中，基于 25% LIDC-IDRI 标签微调的 L2GSSL 获得 AUROC 0.8138±0.0401 和 AUPRC 0.7589±0.0461，比最强自监督基线 volume-level VICReg 分别提高 0.1130 和 0.0954。
- 在 47–48 GB VRAM 约束下，L2GSSL 获得最高线性探测 AUROC 0.8599±0.0038 和 AUPRC 0.7926±0.0039。
- 与完全 3D VoCo 参考相比，L2GSSL 峰值 VRAM 为 24.37–24.48 GB，低于 VoCo 的 27.57 GB，且在线性探测以及 10%、25%、100% 标签微调的所有评估设置中均取得更高 AUROC 和 AUPRC。
- 在 MaxViT 骨干线性探测中，L2GSSL 获得 AUROC 0.8919±0.0051、AUPRC 0.8850±0.0034，为所有比较方法中最高。
- 病变切片 masking 使恶性 TPR 从 87.84% 下降到 14.57%，降低 73.27 个百分点；AUROC 从 0.9404 降至 0.6169，AUPRC 从 0.9043 降至 0.4307。
- 在 RSNA 多专家腹部创伤流程中，原始 competition loss 为 0.3597，整合 L2GSSL 预训练专家的最佳配置为 0.3551。
- 组件消融显示，去除 stop-gradient 在两种初始化下均产生最弱判别结果；去除分阶段调度在 DINOv2 初始化下反而优于完整配置，完整配置在随机初始化下最好，说明分阶段调度的价值依赖初始化。
- 投影头 batch normalization 敏感性实验中，MoCo v2、SimSiam 和 L2GSSL 分别记录 AUROC 0.6497±0.0014、0.5731±0.0008 和 0.7623±0.0071，AUPRC 0.4889±0.0357、0.3195±0.0009 和 0.5615±0.0045，表明投影头归一化不能解释 MoCo v2 和 SimSiam 较弱的结果。

## Limitations

作者明确讨论的局限包括：L2GSSL 的预期用途是表示预训练而非自主诊断；外部 LNDb 评估和 RSNA 腹部创伤转移虽然提供了跨数据源和解剖任务的证据，但不能证明前瞻性临床有效性；站点特定的二次预训练可能吸收扫描仪特征、重建核或人群相关性等与病理无关的捷径，去标识化无法阻止这些捷径，SSL 在预训练期间没有基于标签的机制检测它们；虽然患者级划分防止了数据集内泄漏，未参与训练的 LNDb 提供初步分布偏移检查，但这些不能替代机构治理。作者还指出，slice grouping 可以降低峰值激活存储，但不意味着更低的 wall-clock time 或更高的数据吞吐，顺序分组可能带来额外执行开销；与 VoCo 的比较未控制骨干、输入形式和初始化。组件分析表明分阶段优化并非普遍有益，其价值依赖初始化。从现有证据无法判断的局限还包括：未报告完整的超参数搜索范围和统计显著性检验；未提供除报告数值外的置信区间或不确定性分析；RSNA 腹部创伤转移仅报告 competition loss，未提供该任务上的 AUROC/AUPRC 等判别指标；总体而言证据未能覆盖所有训练细节。
