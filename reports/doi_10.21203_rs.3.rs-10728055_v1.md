# FZ-VLM: A Two Stage Florence-Zephyr Vision Language Model Framework for Pulmonary Nodule Characterization and Clinical Decision Making

## Paper Information

- **Source:** europepmc
- **Paper ID:** PPR1313465
- **DOI:** 10.21203/rs.3.rs-10728055/v1
- **Venue:** Not reported in the available evidence.
- **Authors:** Dutta P, Manokaran J, Mittal R, Appleby R, Ukwatta E
- **Published:** 2026-09-07
- **Updated:** 2026-09-07
- **Categories:** 
- **Landing URL:** https://doi.org/10.21203/rs.3.rs-10728055/v1
- **PDF URL:** Not reported in the available evidence.

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** abstract_only
- **Confidence:** low
- **PDF status:** No full text available; abstract only

## Methodology

本研究提出 FZ-VLM，一种两阶段的 Florence-Zephyr 视觉语言模型框架，用于肺结节的结构化表征和临床决策支持。第一阶段使用经过微调的 Florence-2 模型，从专家标注的 2D 轴向 CT 切片中提取放射学属性，包括解剖位置、直径、边缘特征和衰减类型。第二阶段使用 Zephyr-7B 模型，基于第一阶段提取的属性生成结节描述、随访建议和纵向分析。论文摘要中未报告具体的微调方法、训练策略、优化器、学习率、损失函数、预处理或数据增强细节。

## Evaluation

研究构建了一个结构化视觉问答数据集，包含 8,540 个图像-提示-答案三元组，来自 National Lung Screening Trial 中的 745 例患者病例。第一阶段模型在解剖位置、边缘特征、衰减类型和直径估计上进行了评估；将结果与基于 GPT-4 的基线以及人类基线进行比较。第二阶段由专家放射科医生评估准确性、完整性、临床相关性和总体评分，并进行了安全性分析。摘要中未报告训练/验证/测试划分、交叉验证设置、统计学检验、参数数量或推理时间。

## Innovation

作者提出了一种两阶段的视觉语言模型框架 FZ-VLM，将 Florence-2 的属性提取能力与 Zephyr-7B 的文本生成能力结合，用于统一的肺结节结构化表征和临床决策支持，涵盖结节描述、随访建议和纵向分析。作者声称这是首个用于结构化结节表征和临床决策支持系统的两阶段视觉语言模型框架。

## Datasets

- National Lung Screening Trial

## Metrics

- accuracy
- Mean Absolute Error
- completeness score
- clinical relevance
- overall score

## Key Results

- Stage 1 model 在解剖位置上的准确率为 77.18%。
- Stage 1 model 在边缘特征上的准确率为 67.96%。
- Stage 1 model 在衰减类型上的准确率为 79.13%。
- Stage 1 model 在直径估计上的平均绝对误差为 2.58 mm。
- Stage 1 model 在这些任务上优于所评估的 GPT-4 基线和人类基线。
- Stage 2 的专家放射科医生评估显示 93.9% 的准确率、98.6% 的完整性评分、76.1% 的临床相关性，以及 89.5% 的总体评分。
- 安全性分析显示大多数输出在临床上是安全的，但部分随访建议仍需专家审查。

## Limitations

作者明确指出的局限性：在安全性分析中，部分随访建议仍需要专家审查，表明系统输出并未完全达到可直接临床使用的标准。此外，由于仅提供摘要证据，无法判断作者是否报告了其他局限性；论文证据中未提供关于数据划分、泛化验证、样本偏倚、模型鲁棒性或外部验证等限制的具体说明。

## Processing Notes

The PDF could not be fully processed. Analysis used the available arXiv metadata and other recoverable evidence.

- **PDF error:** No downloadable full text is available for this record.
