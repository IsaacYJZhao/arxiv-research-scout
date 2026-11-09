# Deep learning-based detection and classification of airway nodules on CT for early medical intervention

## Paper Information

- **Source:** europepmc
- **Paper ID:** 42986384
- **DOI:** 10.1186/s13244-026-02446-7
- **Venue:** Insights into imaging
- **Authors:** Liu S, Yi P, Fan Y, Hu J, Zheng C, Lei P, Li S, Yang F, Li C, Hou Y, Li Y, Luo G, Fang X, Zheng H, Bai H, Zhou H, Liao W
- **Published:** 2026-11-05
- **Updated:** 2026-11-05
- **Categories:** Classification, computed tomography, Early Detection, Deep Learning, Airway Nodule
- **Landing URL:** https://doi.org/10.1186/s13244-026-02446-7
- **PDF URL:** https://europepmc.org/articles/PMC13740212?pdf=render

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** abstract_only
- **Confidence:** low
- **PDF status:** Download or parsing failed; abstract used instead

## Methodology

该研究开发了基于深度学习的CT气道结节检测与分类系统，用作二次阅片工具。检测模型基于球体中心点匹配网络（sphere-based center-points matching network）构建，该网络最初用于建立肺结节检测模型，后被迁移至气道结节检测任务，并通过引入坐标信息和多尺度注意力机制进行增强。检测模型使用907个近端气道结节进行训练，并在四个医院收集的738个近端气道结节上进行独立测试。分类模型采用基于3D SEResNeXt101的架构，对286个气道结节（121个良性、165个恶性）按6:2:2的比例划分训练集、验证集和测试集进行训练、验证和测试，并额外在独立测试数据集上进行评估。研究还通过人机交互实验评估了AI工具在辅助放射科医生检测方面的临床效用。

## Evaluation

研究数据来源于回顾性收集的1107例低剂量CT（LDCT），涉及1043名参与者，共识别出1813个段级及更近端的气道结节。检测模型在来自四家医院的738个近端气道结节的独立测试集上评估，报告的灵敏度为73.7%。人机交互实验显示，AI辅助使放射科医生的灵敏度从39.5%提升至72.9%，F1分数从49.4%提升至77.2%，诊断时间从83.8秒缩短至61.8秒。分类模型采用286个气道结节（121例良性、165例恶性），按6:2:2划分训练、验证和测试集，并另设独立测试集。分类模型在多中心训练、验证、测试和独立测试集上的灵敏度分别为82.1%、71.4%、94.3%和72.7%，特异度分别为62.7%、73.9%、73.9%和87.5%。证据中未报告基线模型对比、统计检验、消融研究、置信区间或具体的损失函数、优化器、学习率、训练轮数等训练细节。

## Innovation

该研究将原本用于肺结节检测的球体中心点匹配网络迁移到气道结节检测任务，并通过加入坐标信息和多尺度注意力机制进行增强；同时构建了基于3D SEResNeXt101的气道结节分类模型。作者声称该AI系统能够显著提升近端气道结节的检测和分类能力，并作为二次阅片工具辅助早期医疗干预。证据中未将该系统与先前工作直接进行对比以支持其相对新颖性或优越性。

## Datasets

- 1107例低剂量CT（LDCT），来自1043名参与者，包含1813个段级及更近端的气道结节
- 检测模型训练集：907个近端气道结节
- 检测模型独立测试集：738个近端气道结节，来自四家医院
- 分类模型数据集：286个气道结节（121例良性、165例恶性），按6:2:2划分

## Metrics

- 灵敏度（sensitivity）
- 特异度（specificity）
- F1分数（F1-score）
- 诊断时间（diagnosis time）

## Key Results

- 检测模型在独立测试集上的灵敏度为73.7%。
- AI辅助使放射科医生检测气道结节的灵敏度从39.5%提升至72.9%。
- AI辅助使F1分数从49.4%提升至77.2%。
- AI辅助使诊断时间从83.8秒缩短至61.8秒。
- 分类模型在训练、验证、测试和独立测试集上的灵敏度分别为82.1%、71.4%、94.3%和72.7%。
- 分类模型在训练、验证、测试和独立测试集上的特异度分别为62.7%、73.9%、73.9%和87.5%。

## Limitations

作者明确陈述的局限性：在提供的证据中未见作者明确列出的局限性内容。基于现有证据不完整而推测的局限性：证据仅提供了摘要级别的信息，缺乏对检测模型和分类模型的详细网络结构、预处理流程、训练参数、损失函数、优化器、数据增强、基线对照、统计检验、置信区间以及外部验证细节的报告；因此无法评估模型泛化性、稳健性及与其他方法的相对性能。

## Processing Notes

The PDF could not be fully processed. Analysis used the available arXiv metadata and other recoverable evidence.

- **PDF error:** HTTPError: 403 Client Error: Forbidden for url: https://europepmc.org/articles/PMC13740212?pdf=render
