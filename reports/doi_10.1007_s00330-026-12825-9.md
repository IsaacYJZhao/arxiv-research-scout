# Automated artificial intelligence performance for longitudinal pulmonary nodule matching in lung cancer screening

## Paper Information

- **Source:** europepmc
- **Paper ID:** 42668303
- **DOI:** 10.1007/s00330-026-12825-9
- **Venue:** European radiology
- **Authors:** Jiang B, Lancaster HL, Davies MPA, Gratama JC, Silva M, Han D, Yi J, van der Aalst CM, Devaraj A, Heuvelmans MA, Field JK, Oudkerk M
- **Published:** 2026-08-29
- **Updated:** 2026-08-29
- **Categories:** Artificial intelligence, Tomography, X-ray computed, Image processing, computer-assisted, Early Detection Of Cancer, Solitary Pulmonary Nodule
- **Landing URL:** https://doi.org/10.1007/s00330-026-12825-9
- **PDF URL:** Not reported in the available evidence.

## Analysis Information

- **Provider:** deepseek
- **Model:** deepseek-v4-pro
- **Evidence level:** abstract_only
- **Confidence:** medium
- **PDF status:** No full text available; abstract only

## Methodology

本研究评估一种人工智能（AI）肺结节分析系统在肺癌筛查纵向结节匹配中的自动性能。方法上，对所有接受3个月随访低剂量CT（LDCT）的UKLS试验参与者，由肺AI独立评估其基线扫描，并采用更新的体积阈值（实性成分≥100 mm³，依据NELSON 2.0/EUPS方案）来确定需要3个月随访的病例。为检验算法的真正稳健性，所有AI检测到的基线候选结节（≥100 mm³）均直接进入全自动纵向匹配，未进行任何人工选择。随后将基线候选结节与随访扫描中的持续存在结节进行匹配，并对未匹配结果进行专家复核和分类。具体网络架构、预处理、训练策略、推理过程等详细信息在所提供的证据中未报告。

## Evaluation

研究在UKLS试验中361名接受3个月随访LDCT的参与者上进行评估。肺AI在181名参与者中识别出378个≥100 mm³的基线结节；其中39个结节在随访时自然消退，剩余339个持续存在结节被用于匹配性能评估。主要评价指标为匹配成功率及其95%置信区间，并进一步按单结节与多于5个结节的参与者分层分析。未匹配发现由专家复核，并按非结节结构（如胸膜斑块）和离散实性结节进行分类。未报告与其它基线方法或AI系统的比较、消融研究或统计显著性检验。

## Innovation

本研究的贡献在于对肺AI在无人工选择条件下的全自动纵向结节匹配可靠性进行评估，并采用NELSON 2.0/EUPS更新体积阈值（实性成分≥100 mm³）作为3个月随访候选结节标准。研究用证据表明，该自动流程在大多数持续存在结节上可实现稳健匹配，且大部分失败来源于非结节结构而非算法对真实结节的漏配，从而提示可减少随访中的人工跟踪工作量。所提供的证据未明确声称该方法为首创或达到最优水平。

## Datasets

- UK Lung Cancer Screening (UKLS) trial

## Metrics

- matching success rate
- 95% confidence interval

## Key Results

- 在361名接受3个月随访LDCT的UKLS参与者中，肺AI识别出181名参与者共378个≥100 mm³的基线结节。
- 39个结节在随访时自然消退，339个持续存在结节被纳入匹配评估。
- 肺AI对339个持续存在结节的匹配成功率为83.5%（283/339；95% CI: 79.2-87.1%）。
- 对于只有单个基线候选结节的参与者（占队列59.7%），匹配性能为91.8%（89/97）。
- 对于超过5个结节的参与者（占队列6.6%），匹配性能为72.8%（75/103）。
- 56/339（16.5%）个未匹配发现中，91.1%（51/56）为非结节结构，其中胸膜斑块占46.4%（26/56）。
- 仅有5个未匹配的离散实性结节（占339个持续存在发现的1.5%；95% CI: 0.6-3.5%）需要人工干预。
- 高结节负担的扫描中匹配性能下降。

## Limitations

作者在证据中明确指出的局限性包括：在高结节负担的扫描中匹配性能下降，以及需要在多样化人群中进行前瞻性验证。此外，根据所提供的证据，无法确定其他潜在局限性，因为未报告算法架构、训练细节、外部数据集验证、与其它方法的比较或长期随访结果。上述缺失不应被视为作者明确说明的局限性。

## Processing Notes

The PDF could not be fully processed. Analysis used the available arXiv metadata and other recoverable evidence.

- **PDF error:** No downloadable full text is available for this record.
