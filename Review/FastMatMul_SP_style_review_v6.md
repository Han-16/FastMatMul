# FastMatMul S&P-Style Review

검토 대상: `FastMatMul/main.tex` 및 포함 LaTeX 소스, 2026-05-26 현재 수정본  
리뷰 양식: IEEE S&P 공식 양식을 정확히 알 수 없으므로, S&P-style 점수형 security/program-committee review 형식으로 작성함.

## Overall Recommendation

**Recommendation: Borderline Reject / Weak Reject**

**Overall score: 3.0 / 5**

이 수정본은 이전 버전보다 명확히 좋아졌다. 특히 논문 제목과 초록이 “matrix-multiplication checking layer”로 정확히 낮아졌고, IEEE-style template으로 전환되었으며, soundness-budget table, backend-boundary table, knowledge-soundness remark, measurement-coverage table, extended related-work table이 추가되었다. 리뷰에서 지적했던 overclaim과 security-parameter ambiguity는 상당 부분 해소되었다.

그럼에도 현재 상태를 S&P accept 수준으로 보기는 어렵다. 핵심 이유는 여전히 동일하다. 논문의 가장 중요한 asymptotic claim과 주요 실험 결과는 conditional linear-time code-commitment backend model에 의존하지만, 현재 artifact는 standalone `CodeComV`를 구현하거나 독립 측정하지 않는다. 이제 이 한계는 본문에 정직하게 드러나므로 논문 신뢰도는 올라갔지만, S&P 제출 품질 기준에서는 아직 major missing component다.

현재 원고는 “흥미로운 modular checking-layer protocol + layer-level prototype”으로는 강해졌다. 하지만 “완결된 verifiable-computation system” 또는 “실제로 end-to-end 성능을 입증한 security systems paper”로는 아직 부족하다.

## Score Summary

| Category | Score | Rationale |
|---|---:|---|
| Overall merit | 3.0 / 5 | 논문 품질은 개선됐지만 핵심 backend gap이 남아 있음 |
| Novelty | 3.5 / 5 | Freivalds, code proximity, SNARK-friendly local checks의 조합은 흥미롭고 유용함 |
| Technical soundness | 3.5 / 5 | theorem statement, ordering, FS loss, soundness budget이 명확해짐; 단, backend-relative result |
| Significance | 3.0 / 5 | matrix-checking layer로는 의미 있음; full VC system impact는 아직 조건부 |
| Evaluation | 3.0 / 5 | layer-level evidence는 좋아졌지만 standalone backend, memory, variance, key size가 없음 |
| Presentation | 4.0 / 5 | claim framing, limitation disclosure, template, appendix 구조가 크게 개선됨 |
| Reproducibility | 3.0 / 5 | measurement coverage는 명시됐으나 artifact-level 통계와 backend measurement가 부족 |
| Reviewer confidence | 4.0 / 5 | 암호 프로토콜/보안 증명/평가 범위 관점에서 판단 가능 |

## Paper Summary

이 논문은 큰 행렬곱 검증을 SNARK 내부에서 직접 계산하지 않고, Freivalds-style randomized reduction과 error-correcting code proximity check를 결합해 matrix multiplication checking layer를 구성한다. 핵심 비용은

`O(tk + t log n + E_cc(k))`

이고, code-commitment backend verifier 비용 `E_cc(k)`가 linear-time이면 checking relation은 fixed security parameter에서 `O(k)`가 된다.

보안 정리는 certified encoded input commitments와 code-commitment backend에 상대적인 statement soundness를 제공한다. Soundness error는

`epsilon_SNARK + epsilon_cc + epsilon_bind + (k-1)/|F| + 4(1-delta)^t`

이며 Fiat-Shamir variant는 `epsilon_FS(q_H)` 손실을 추가한다. 이번 버전은 이 bound를 concrete soundness-budget table로 분해하고, `t=128` scaling run과 strict 128-bit deployment target을 구분한다.

구현은 Rust 기반 `fmQA` checking layer를 평가한다. 주요 결과는 `k=4096`에서 Freivalds SNARK baseline 대비 constraint `30.29x` 감소, proving time `7.18x` 개선, proof size `104 KB`이며, GPT-2-style workload에서는 constraint `2.30x`, proving time `1.77x` 개선을 보고한다. 다만 이 수치는 standalone `CodeComV`와 raw-input-to-certified-commitment 비용을 포함하지 않는 layer-level measurement다.

## Improvements Since Previous Review

1. **Claim framing이 좋아졌다.**  
   제목, 초록, introduction, evaluation, conclusion이 모두 “checking layer”와 “conditional backend model”을 명시한다. 이전처럼 end-to-end system으로 읽힐 위험이 줄었다.

2. **S&P/IEEE 제출 형식에 가까워졌다.**  
   ACM CCS metadata와 placeholder DOI/ISBN이 제거되고 `IEEEtran` template, anonymous author, IEEE keywords, IEEE bibliography style로 바뀌었다.

3. **보안 파라미터 설명이 명확해졌다.**  
   soundness-budget table은 `t=128`, `2^-126` proximity term, strict 128-bit target, per-term budget, FS loss를 분리해서 보여준다. 이는 매우 중요한 개선이다.

4. **Backend boundary가 명시적으로 정리되었다.**  
   construction에 backend-boundary table이 추가되어 dense encoder check, linear-time committed-codeword backend, algebraic linking backend, current QA artifact의 역할을 구분한다.

5. **Evaluation scope가 더 투명해졌다.**  
   measurement-coverage table이 추가되어 constraint/proving/verification/proof size는 covered, setup은 partial, standalone `CodeComV`, peak memory, variance는 not covered라고 명시한다.

6. **Knowledge soundness가 과도하게 주장되지 않는다.**  
   main theorem은 statement soundness로 유지하고, argument of knowledge는 extractable input-commitment interface와 knowledge-sound SNARK의 composition issue로 분리했다. 이 방향이 맞다.

## Strengths

### Strong modularization

논문은 이제 자신이 증명하는 것과 증명하지 않는 것을 비교적 정확히 구분한다. `CodeComV`, certified input roots, position binding, global codeword binding이 theorem의 precondition임을 숨기지 않는다. S&P 리뷰어에게 중요한 신뢰 요소다.

### Cleaner security proof

Soundness-critical ordering이 잘 정리되어 있다. Input roots는 Freivalds challenge `r` 전에 고정되고, intermediate roots는 query tuple `I` 전에 고정된다. With-replacement sampling, Fiat-Shamir grinding loss, backend bad events, Freivalds error, proximity error가 분리되어 있어 proof structure가 읽기 쉽다.

### Useful empirical signal

Layer-level result만 놓고 보면 수치가 강하다. `k=4096`에서 constraint `1,667,305` vs `50,495,818`, proving time `56.44s` vs `405.04s`는 설득력 있는 scaling evidence다. QA-NIZK proof size도 `104 KB` at `k=4096`, `126 KB` at `k=8192`로 정리되어 이전보다 현실성이 높아졌다.

### Honest limitations

논문이 자신의 약점을 숨기지 않는다. Standalone `CodeComV`, peak memory, variance, setup/key size, end-to-end deployment cost가 없다는 점을 evaluation과 appendix에서 반복적으로 밝힌다. 이 점은 논문을 더 전문적으로 보이게 한다.

## Major Weaknesses

### 1. Standalone `CodeComV` gap remains the main blocker

가장 큰 문제는 여전히 standalone `CodeComV`가 구현/측정되지 않았다는 점이다. 논문은 `E_cc(k)=O(k)` backend가 있으면 checking layer가 `O(k)`가 된다고 주장한다. 그러나 현재 artifact는 그 backend를 닫지 않는다. Table `backend-boundary`와 measurement-coverage table이 이 사실을 명확히 하므로 overclaim은 줄었지만, S&P accept 관점에서는 “핵심 시스템 구성요소가 빠져 있다”는 판단이 남는다.

이 논문이 S&P에서 통과되려면 둘 중 하나가 필요하다.

- concrete linear-time code-commitment backend를 선택하고, `CodeComV`를 실제 relation/circuit/proof component로 구현 및 측정한다.
- 또는 논문을 systems/evaluation paper가 아니라 modular cryptographic protocol paper로 더 강하게 재포지셔닝하고, “실험은 local layer microbenchmark”임을 headline claim에서도 더 제한한다.

현재는 두 방향 사이에 있다. 정직하게 제한을 밝히지만, headline efficiency claim은 여전히 backend assumption에 크게 의존한다.

### 2. Strict security parameter rows are described but not measured

이번 버전은 `t=128` scaling row와 strict 128-bit target을 구분한다. 이는 좋은 수정이다. 하지만 main experiments는 여전히 `t=128`이다. `delta=1/2`에서 proximity term은 `2^-126`이고, strict proximity-only 128-bit는 `t=130`, conservative per-term `2^-131` budget은 `t=133`이라고 되어 있다.

`t`가 128에서 133으로 증가하면 fold/opening/linking cost가 거의 선형으로 늘어날 가능성이 높다. 증가 폭은 작을 수 있지만, S&P 제출용으로는 strict parameter row를 실제 표에 추가하는 것이 낫다. 예를 들어 `k=1024`, `k=4096`, GPT-2 workload에 대해 `t=133` 결과 또는 정확한 extrapolation을 제시하면 이 문제는 거의 해소된다.

### 3. Evaluation is still incomplete for a systems-security venue

평가가 상당히 좋아졌지만, S&P systems/security artifact 관점에서는 아직 빠진 항목이 많다.

- standalone `CodeComV` cost 없음
- raw input에서 certified encoded commitments까지의 end-to-end cost 없음
- peak RSS 없음
- repeated-run variance 또는 confidence interval 없음
- setup/key size 없음
- proof-size breakdown은 설명은 있으나 상세 표는 부족함
- Freivalds `k=8192` 미측정
- baseline이 거의 optimized Freivalds SNARK 하나에 집중됨

이 중 일부는 appendix에서 “not covered”라고 정직하게 밝혔지만, 정직한 disclosure는 acceptability를 자동으로 보장하지 않는다. 특히 `CodeComV`, memory, variance, setup/key size는 S&P 리뷰에서 실험 신뢰도와 직결된다.

### 4. Related-work comparison is still mostly qualitative

Related work와 appendix table은 좋아졌지만, S&P 독자는 sumcheck/GKR, dedicated matrix VC, code-based SNARK 계열과의 tradeoff를 더 구체적으로 보고 싶어 할 것이다. 모든 시스템을 재구현할 필요는 없지만, 최소한 다음 축의 비교가 main body에 있으면 좋다.

- trusted setup 여부
- verifier model
- proof size asymptotics
- prover overhead
- batching support
- whether it verifies raw matrices or committed encoded objects
- whether the result is zero-knowledge, VC-only, or statement-sound checking

현재 appendix의 qualitative table은 좋은 출발점이지만, S&P main paper의 positioning defense로는 조금 약하다.

### 5. Statement soundness vs argument of knowledge remains a subtle point

이번 버전은 knowledge soundness를 remark로 분리한 점이 좋다. 다만 논문이 “verifiable computation”이라는 용어를 계속 쓰기 때문에, 독자는 accepted proof에서 실제 witness/extraction이 무엇인지 궁금해할 수 있다. 현재 theorem은 certified public input commitments에 대한 statement soundness이고, argument of knowledge는 extractable input-commitment interface와 knowledge-sound SNARK를 붙이면 얻어진다고 설명한다.

이 설명은 합리적이지만, S&P 제출용으로는 relation hierarchy를 더 명확히 그림 또는 표로 정리하는 것이 좋다.

- What is public?
- What is committed?
- What is extracted?
- What is assumed certified?
- Which component proves codeword validity?
- Which component proves matrix multiplication?

현재 construction에는 정보가 있지만, 독자가 한 번에 보기에는 아직 복잡하다.

### 6. Zero-knowledge extension paragraph may invite avoidable criticism

논문은 현재 VC/checking layer이고, zero-knowledge를 주장하지 않는다. 그런데 construction의 “Zero-knowledge extension” paragraph는 “straightforwardly”라는 표현을 쓴 뒤, hiding sampled openings, backend material, linking material requires separate simulation argument라고 인정한다.

이 문단은 공격받기 쉽다. S&P submission에서는 다음 중 하나가 더 안전하다.

- ZK paragraph를 future work로 낮춘다.
- “straightforwardly”라는 표현을 제거하고, full ZK construction은 out of scope라고 명확히 한다.
- ZK를 언급하려면 simulation target과 leakage from sampled openings를 더 엄밀히 써야 한다.

## Minor Comments

1. Main evaluation 문장 중 GPT-2 paragraph에 “with sequence length ..., 36 claims, and 5 commitment groups, `fmQA` reduces...” 형태의 문장이 약간 어색하다. 쉼표 앞뒤 구조를 정리하면 좋다.

2. “Negligible encoding overhead” claim은 off-circuit encoding time에는 맞지만, dense backend codeword-validity constraints는 quadratic임을 같은 문단에서 다시 강조하는 편이 안전하다.

3. Appendix의 Reed-Solomon codeword verification section은 흥미롭지만 main construction의 chosen backend와 직접 연결되지 않으면 다소 뜬금없게 보일 수 있다. 이 appendix가 dense/RS fallback backend를 위한 것인지 명확히 연결하라.

4. 현재 PDF는 17 pages이며 references는 page 12에서 시작한다. Appendix 포함 여부와 S&P page limit 규칙을 실제 CFP 기준으로 다시 확인해야 한다.

5. LaTeX build는 fatal error나 undefined reference는 없어 보이나, underfull warnings가 많다. 제출 전 table/figure layout polish가 필요하다.

## Questions for Authors

1. S&P submission에서 실제로 목표로 하는 concrete `CodeComV` backend는 무엇인가?
2. 그 backend의 certified relative distance `delta`, codeword-binding error, position-binding error는 어떻게 증명되는가?
3. Strict 128-bit configuration에서 `t=133`을 쓸 때 main benchmark와 GPT-2 workload 수치는 어떻게 변하는가?
4. Raw matrices에서 certified encoded input commitments까지의 pipeline은 누가 생성하고, verifier는 무엇을 확인하는가?
5. `fmQA` verifier가 GPT-2 workload에서 Freivalds보다 약 `10x` 느린 점은 target deployment에서 허용 가능한가?
6. Peak memory, variance, setup/key sizes를 추가하면 현재 efficiency story가 유지되는가?
7. Freivalds가 `k=8192`에서 측정되지 않은 이유는 time limit인가, memory limit인가, implementation limit인가?

## Required Revisions Before S&P Submission

1. **Close or explicitly downgrade the backend gap.**  
   가장 좋은 수정은 concrete `CodeComV` backend를 구현하고 측정하는 것이다. 어렵다면, 논문을 “conditional modular checking layer”로 더 강하게 포지셔닝하고 systems-level claim을 줄여야 한다.

2. **Add strict-parameter experiments or extrapolations.**  
   `t=133` 또는 backend-certified `delta` 기반 strict deployment row를 main table이나 appendix에 추가하라.

3. **Add artifact-quality measurements.**  
   Peak RSS, repeated-run variance, setup/key sizes, proof breakdown, and end-to-end preprocessing/commitment costs를 추가하라.

4. **Strengthen comparison against non-Freivalds approaches.**  
   최소한 qualitative comparison을 main body로 올리고, 가능하면 representative systems와의 normalized comparison을 제공하라.

5. **Clarify VC/AoK/ZK boundaries.**  
   Statement soundness, argument of knowledge composition, and zero-knowledge extension의 범위를 더 명확히 분리하라.

## Final Assessment

이 버전은 이전보다 훨씬 더 제출 가능한 형태에 가까워졌다. 특히 claim framing, 보안 예산, backend boundary, limitation disclosure, S&P/IEEE-style formatting은 실질적으로 개선되었다.

그러나 현재 상태에서도 S&P에 바로 제출해 accept를 기대하기는 어렵다. 핵심 성능 주장이 standalone `CodeComV` 없는 conditional backend model 위에 있고, 실험도 아직 layer-level이다. 이 점을 감안하면 현재 판정은 **Borderline Reject / Weak Reject, 3.0 / 5**가 적절하다.

한 번 더 revision을 한다면, accept 가능성을 가장 크게 올리는 수정은 논문을 더 예쁘게 다듬는 것이 아니라 `CodeComV` backend gap을 닫는 것이다.
