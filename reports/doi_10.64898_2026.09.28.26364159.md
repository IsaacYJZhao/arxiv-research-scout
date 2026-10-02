# Comparing Deep Learning Models for Lung Nodule Detection on Photon-Counting CT Images in a Non-Screening Setting

## Paper Information

- **Source:** europepmc
- **Paper ID:** PPR1331819
- **DOI:** 10.64898/2026.09.28.26364159
- **Venue:** Not reported in the available evidence.
- **Authors:** Thieme L, Petersen E, Geissler K, Müller-Groh L, Oeltze-Jafra S, Shin H, Scharm SC, Wacker F, Ahmadi Z, Schenk A
- **Published:** 2026-09-29
- **Updated:** 2026-09-29
- **Categories:** 
- **Landing URL:** https://doi.org/10.64898/2026.09.28.26364159
- **PDF URL:** Not reported in the available evidence.

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** abstract_only
- **Confidence:** low
- **PDF status:** No full text available; abstract only

## Methodology

本研究未提出新的检测算法，而是对四种已有的基于深度学习的肺结节检测模型进行比较评估。所比较的模型包括公开可用的 TotalSegmentator、nnDetection、RadYOLO，以及一个商用肺部计算机辅助检测（CAD）系统。这些模型最初针对常规 CT 开发，在本研究中被直接用于光子计数 CT（PCCT）图像。评估采用回顾性设计，收集了 2021 至 2024 年在 Hannover Medical School 获取的 1860 例常规 PCCT 扫描。论文证据中未报告对模型的重新训练、微调或针对 PCCT 的特定预处理、推理流程改造等细节。

## Evaluation

研究使用 1860 例回顾性 PCCT 扫描，并在三个不同队列或分析层面进行评估：1）在未标注队列（n=1699）中比较模型间一致性；2）在 25 例人工标注扫描的小型队列中评估敏感性；3）将 136 例报告阴性扫描中的检测结果作为假阳性进行分析。证据中报告了各模型的检测结节数量：商用 CAD 系统 7071 个，TotalSegmentator 4264 个，nnDetection 5254 个，RadYOLO 3122 个。约 1300 个结节被所有模型同时检出，占各模型检测结果的 18.7%–42.8%；各模型检测结果中有 15.4%–37.4% 未与任何其他模型匹配。敏感性范围在 0.71（95%-CI [0.64, 0.77]）至 0.83（95%-CI [0.77, 0.88]）之间。TotalSegmentator 和 RadYOLO 每例扫描的假阳性均为 0.85（95%-CI [0.70, 1.02]）。证据未报告训练/验证/测试划分、交叉验证设置或统计显著性检验的进一步细节。

## Innovation

论文的主要贡献在于对肺结节检测模型在临床常规光子计数 CT（PCCT）数据以及非筛查场景下的系统性比较，尤其是同时纳入学术公开模型和商用 CAD 系统。证据中并未声称提出了新的检测算法或模型架构；其贡献体现为模型基准测试和本地验证方面的实证发现。

## Datasets

- Hannover Medical School 2021-2024 常规 PCCT 扫描（1860 例；其中未标注队列 n=1699，人工标注扫描 25 例，报告阴性扫描 136 例）

## Metrics

- 检测结节数量
- 模型间一致性
- 所有模型共同检出结节比例
- 未与其他模型匹配的检测比例
- 敏感性（sensitivity，含 95% 置信区间）
- 假阳性/扫描（false positives per scan，含 95% 置信区间）

## Key Results

- 商用 CAD 系统检测到 7071 个结节，TotalSegmentator 4264 个，nnDetection 5254 个，RadYOLO 3122 个。
- 模型间总体一致性较低，不同模型产生的候选结节差异显著。
- 约 1300 个结节被所有模型检测到，占各模型检测结果的 18.7%–42.8%。
- 各模型检测结果中有 15.4%–37.4% 未与任何其他模型匹配。
- 敏感性介于 0.71（95%-CI [0.64, 0.77]）和 0.83（95%-CI [0.77, 0.88]）之间，属于中等水平。
- TotalSegmentator 和 RadYOLO 的假阳性为每例扫描 0.85（95%-CI [0.70, 1.02]），数量较少。
- 四种深度学习模型在临床 PCCT 数据上检测到的肺结节存在高度差异且缺乏共识。

## Limitations

论文证据中未明确列出作者自述的局限性。基于现有证据可推断的信息不完整包括：人工标注扫描队列规模较小（n=25）；未报告模型是否针对 PCCT 进行适配、微调或重新训练；未报告训练/验证/测试划分、交叉验证设计；未提供除敏感性、假阳性/扫描和模型间一致性之外的详细评估指标；未报告统计显著性检验。上述内容应视为证据不完整导致的推断，而非论文明确声明的局限性。

## Processing Notes

The PDF could not be fully processed. Analysis used the available arXiv metadata and other recoverable evidence.

- **PDF error:** No downloadable full text is available for this record.
