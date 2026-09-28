# An end-to-end deep learning approach for lung nodule segmentation and classification using LN-DETR and deep sequential convolutional harmonic networks

## Paper Information

- **Source:** europepmc
- **Paper ID:** 42777593
- **DOI:** 10.1016/j.compbiomed.2026.111923
- **Venue:** Computers in biology and medicine
- **Authors:** Ramani S, Rajeshkannan S, Sivakumar J
- **Published:** 2026-09-23
- **Updated:** 2026-09-23
- **Categories:** Deep Belief Network, Lung Cancer Classification, Lung Nodule Segmentation, Lung Nodule Detection Transformer, Sequential Convolutional Neural Network
- **Landing URL:** https://doi.org/10.1016/j.compbiomed.2026.111923
- **PDF URL:** Not reported in the available evidence.

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** abstract_only
- **Confidence:** low
- **PDF status:** No full text available; abstract only

## Methodology

本文提出一个面向CT图像肺结节分割与分类的端到端流程。首先对肺CT图像进行自适应中值滤波以去除噪声。增强后的图像进入分割阶段，由 Lung Nodule Detection Transformer (LN-DETR) 提取肺结节区域，并使用提出的 FusionLoss-LFC 损失函数，该损失由 Lovász-Softmax、Cross-Entropy 和 Focal 损失组合而成。分割后的图像通过旋转、翻转和缩放进行数据增强。随后进行特征提取，获得最具判别力的图像特征，并由 Sequential Convolutional Neural Network (SCNN) 用于肺癌检测。最后，采用 Deep Sequential Convolutional Neural Harmonic Network (DSeqCH-Net) 完成肺癌分类。

## Evaluation

摘要报告了 DSeqCH-Net 的定量评价结果，包括 True Negative Rate (TNR)、accuracy 和 True Positive Rate (TPR)，分别为 95.813%、96.745% 和 97.643%。摘要未报告所用数据集名称、样本量、训练/验证/测试划分、对比基线、统计检验或其他评价协议细节，因此无法从现有证据中确认实验设计或结果的可比性背景。

## Innovation

本文的核心方法贡献包括：提出 Lung Nodule Detection Transformer (LN-DETR) 用于肺结节分割；设计 FusionLoss-LFC 损失函数，将 Lovász-Softmax、Cross-Entropy 和 Focal 损失结合；提出 Deep Sequential Convolutional Neural Harmonic Network (DSeqCH-Net) 用于肺癌分类。整体流程将滤波、分割、增强、SCNN 检测与 DSeqCH-Net 分类整合为端到端方式。

## Datasets

- Not reported in the available evidence.

## Metrics

- True Negative Rate (TNR)
- accuracy
- True Positive Rate (TPR)

## Key Results

- DSeqCH-Net 达到 95.813% 的 True Negative Rate (TNR)。
- DSeqCH-Net 达到 96.745% 的 accuracy。
- DSeqCH-Net 达到 97.643% 的 True Positive Rate (TPR)。

## Limitations

作者明确陈述的限制未在现有证据中报告。从证据不完整角度推断：摘要未提供数据集信息、样本量、实验划分、基线方法、消融研究、统计检验以及除 TNR、accuracy、TPR 之外的详细评价，因此无法判断方法的泛化性、比较优势和潜在局限性。

## Processing Notes

The PDF could not be fully processed. Analysis used the available arXiv metadata and other recoverable evidence.

- **PDF error:** No downloadable full text is available for this record.
