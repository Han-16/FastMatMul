# FastMatMul Critical S&P-Style Review

검토 대상: `FastMatMul/main.tex` 및 포함 LaTeX 소스, 2026-05-26 현재 수정본  
리뷰 원칙: S&P 제출 전 의사결정에 필요한 **critical issue만** 평가함. 문장 polish, 사소한 formatting, minor wording은 제외함.

## Overall Recommendation

**Recommendation: Weak Reject / Not ready for S&P submission**

**Overall score: 3.0 / 5**

현재 원고는 이전 버전보다 훨씬 정직하고 명확해졌다. 제목, 초록, introduction, evaluation, conclusion 모두 이 논문이 end-to-end VC system이 아니라 **matrix-multiplication checking layer**라는 점을 반복해서 밝힌다. Security scope, soundness budget, backend boundary, strict-parameter extrapolation, ZK non-claim도 잘 정리되었다.

그럼에도 S&P에 바로 제출하기에는 아직 위험하다. 핵심 문제는 더 이상 presentation이 아니라 **논문의 central technical claim이 concrete backend 없이 conditional model 위에 서 있다는 점**이다. 이 한계를 본문이 정직하게 인정하므로 논문 신뢰도는 올랐지만, S&P 심사에서는 여전히 reject 사유가 될 가능성이 높다.

## Critical Issues Only

### 1. The main theorem and evaluation still rely on an uninstantiated `CodeComV`

이 논문의 핵심 claim은

`O(tk + t log n + E_cc(k))`, and `O(tk)` when `E_cc(k)=O(k)`

이다. 그러나 현재 원고는 `E_cc(k)=O(k)`를 만족하는 concrete `CodeComV`를 구현하지 않고, 독립적으로 측정하지도 않는다. Construction의 backend-boundary table과 evaluation summary가 이 사실을 명확히 밝히지만, S&P 관점에서는 이것이 가장 큰 blocker다.

현재 결과는 다음을 보인다.

- fold/opening/linking layer는 Freivalds SNARK보다 작고 빠르다.
- QA-NIZK/Merkle artifact는 proof size를 현실적인 수준으로 줄였다.
- 단, theorem이 요구하는 global codeword binding backend는 아직 실제 artifact에 닫혀 있지 않다.

즉, 현재 논문은 **complete system result가 아니라 conditional layer result**다. 이 포지셔닝 자체는 가능하지만, 그 경우 S&P accept를 설득하려면 theory contribution이 그만큼 강해야 한다. 현재 논문은 systems-style evaluation number를 강하게 내세우기 때문에, 구현되지 않은 backend가 더 크게 보인다.

**Required before submission:** concrete backend 하나를 선택해서 `CodeComV` relation/circuit/proof component를 구현하고, constraint/proving/verification/proof-size cost를 main evaluation에 포함하라. 이것이 불가능하다면 제목, abstract, contribution, evaluation headline을 더 낮춰 “conditional microbenchmark”임을 전면화해야 한다.

### 2. The evaluated artifact may not correspond to the security theorem

보안 정리는 intermediate roots가 query tuple `I` 전에 **full codeword에 globally bound**된다는 사실에 의존한다. 이 역할을 `CodeComV(cm_v, v, sigma_v)`가 한다. 하지만 current QA artifact는 sampled fold/opening/linking layer를 측정하고, standalone `CodeComV`는 modeled로 둔다.

따라서 현재 evaluation table의 수치는 theorem이 요구하는 full relation의 cost가 아니다. 더 강하게 말하면, 평가된 artifact만 놓고는 theorem의 soundness precondition이 충족되는지 확인할 수 없다. 논문은 이 점을 여러 번 disclosure하지만, S&P 리뷰에서는 disclosure만으로 충분하지 않을 수 있다.

이 문제는 단순한 “missing benchmark”가 아니다. Security theorem과 implementation 사이의 correspondence 문제다.

**Required before submission:** main relation을 세 부분으로 분해해 실제로 무엇이 구현되었는지 명시하라.

| Component | Required by theorem? | Implemented? | Measured? |
|---|---:|---:|---:|
| fold checks | yes | yes | yes |
| position openings / linking | yes | yes | yes |
| global codeword binding `CodeComV` | yes | no/modelled | no |
| certified input commitment interface | yes | assumed | no |

그리고 가능하면 마지막 두 항목을 실제 구현/측정으로 닫아야 한다. 닫지 못하면 현재 성능 claim은 “soundness theorem의 full relation”이 아니라 “the implemented local subrelation”에 대한 것이라고 더 강하게 써야 한다.

### 3. End-to-end VC story remains incomplete

논문은 이제 committed-input model을 명확히 설명한다. 그러나 S&P 독자가 볼 핵심 질문은 여전히 남는다.

> Raw matrices or ML tensors가 주어졌을 때, verifier는 어떤 절차로 certified encoded commitments를 신뢰하는가?

현재 답은 “surrounding committed-codeword system, public generation process, or separate input-opening proof” 수준이다. 이는 modular paper로는 허용될 수 있지만, verifiable computation paper로 제출하면 약하다. 특히 GPT-2 workload를 내세우는 순간, 독자는 raw model weights, activations, layer chaining, commitment reuse, batching, verifier trust boundary를 묻는다.

지금 논문은 matrix-checking layer의 성능은 보여주지만, 실제 VC pipeline에서 다음 비용이 어떻게 붙는지 닫지 않는다.

- raw input to encoded commitment
- input commitment certification
- backend codeword binding
- commitment reuse across many matrix multiplications
- verifier-visible public input size
- setup/key size
- memory and repeated-run variance

이 중 일부는 appendix에서 “not covered”로 밝히지만, S&P systems paper라면 이 항목들은 critical evaluation surface다.

**Required before submission:** end-to-end path를 하나 정하라. 완전 구현이 어렵다면 최소한 one concrete deployment model을 잡고, prover/verifier가 각각 무엇을 생성/검증하는지와 비용을 표로 제시하라. 현재처럼 여러 가능성을 열어두면 claim이 모듈러하다는 장점은 있지만, 실제 시스템으로서의 설득력은 낮다.

### 4. Comparison baseline is still too narrow for the claimed significance

현재 정량 평가는 사실상 optimized Freivalds SNARK baseline 하나에 집중한다. 이 baseline은 중요하지만, S&P에서 “large matrix multiplication for VC/zkML”을 주장하려면 reviewer는 sumcheck/GKR 계열, dedicated matrix VC, code-based SNARK approaches와의 tradeoff를 요구할 가능성이 높다.

Appendix의 qualitative table은 개선이다. 하지만 main claim이 “S&P-worthy significance”를 가지려면 다음 중 적어도 하나가 필요하다.

- representative non-Freivalds system과의 정량 비교
- 같은 workload에서 sumcheck/GKR-style verifier/prover tradeoff와의 normalized comparison
- dedicated matrix VC와 비교한 proof size/verifier/prover/setup tradeoff table
- 왜 Freivalds-in-SNARK가 target application의 strongest relevant baseline인지에 대한 명확한 방어

현재 논문은 Freivalds 대비로는 강하지만, broader landscape에서 왜 이 접근이 top-tier contribution인지가 아직 충분히 방어되지 않는다.

**Required before submission:** main body에 critical comparison table을 넣어라. 단순 related-work 요약이 아니라, verifier model, input model, setup, prover cost, verifier cost, proof size, batching, ZK 여부, implementation status를 비교해야 한다. 가능하면 최소 하나의 non-Freivalds representative와 정량 비교를 추가하라.

## What Would Change the Decision

가장 중요한 것은 `CodeComV` gap을 닫는 것이다. 다음 중 하나가 충족되면 판정은 borderline accept까지 올라갈 수 있다.

1. Concrete linear-time backend를 구현하고, `fmQA + CodeComV` end-to-end cost를 보여준다.
2. Backend를 닫지는 않더라도, 논문을 완전히 modular/theoretical checking-layer paper로 재포지셔닝하고, evaluation headline을 “local subrelation only”로 낮춘다.
3. End-to-end deployment model과 non-Freivalds comparison을 추가해, 조건부임에도 contribution이 충분히 크다는 점을 방어한다.

## Final Assessment

현재 원고는 제출 가능한 형태에 가까워졌지만, 아직 S&P에 바로 내기에는 위험하다. 사소한 문제가 아니라 central artifact/theorem correspondence와 end-to-end instantiation 문제가 남아 있다.

내 판정은 **Weak Reject, 3.0 / 5**다. 지금 상태로 제출하면 정직한 limitation disclosure 덕분에 신뢰는 얻겠지만, “핵심 backend가 구현되지 않았다”는 이유로 reject될 가능성이 높다. 다음 revision의 우선순위는 글 다듬기가 아니라 **concrete `CodeComV` closure 또는 claim downgrade**다.
