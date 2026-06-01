# FastMatMul Critical S&P-Style Review

검토 대상: `FastMatMul/main.tex` 및 포함 LaTeX 소스, 2026-05-26 현재 수정본  
리뷰 원칙: 논문 제출 판단에 영향을 주는 **critical issue만** 평가함. 문장 polish, 사소한 formatting, minor wording은 제외함.

## Overall Recommendation

**Recommendation: Borderline Reject**

**Overall score: 3.5 / 5**

이번 수정본은 실질적으로 개선되었다. 이전 버전의 가장 큰 blocker였던 “standalone `CodeComV`가 모델로만 존재한다”는 문제는 상당 부분 해소되었다. 논문은 이제 intermediate vectors에 대해 full-codeword backend를 요구하지 않고, pre-query message commitments와 sampled CP-link checks로 필요한 지점만 묶는 구조로 바뀌었다. 이 방향은 더 설득력 있다.

그럼에도 S&P 제출 기준으로는 아직 안전하지 않다. 이제 핵심 문제는 `CodeComV` 미구현이 아니라, **새로운 CP-linked backend가 논문의 central primitive가 되었는데 그 primitive의 concrete construction, security assumptions, and measured cost breakdown이 충분히 닫혀 있지 않다**는 점이다. Raw input certification도 여전히 end-to-end VC claim을 제한한다.

## Critical Issues Only

### 1. The new CP-link/message-commitment backend is central but under-specified

이 버전의 핵심 수정은 다음 구조다.

- message commitment `mu_v` fixes `v` before `I`;
- the SNARK computes sampled `Enc(v)_j`;
- Merkle openings authenticate external leaves;
- CP-link checks connect the in-circuit value to the external opened value.

이 구조는 이전 `CodeComV` gap을 줄이는 좋은 방향이다. 하지만 이제 `Msg.Verify`와 `CPLink.Verify`가 논문의 핵심 보안 primitive가 되었다. 현재 원고는 이들을 abstract predicate처럼 정의하지만, S&P 제출 수준에서는 부족하다.

특히 다음이 명확해야 한다.

- `mu_v`의 concrete commitment scheme은 무엇인가?
- `Msg.Verify(mu_v, v, omega_v)`는 SNARK circuit 안에서 검증되는가, 바깥에서 검증되는가?
- Pedersen-style vector commitment라면 in-circuit verification cost가 실제 constraint count에 포함되는가?
- `CPLink.Verify(tau, e_hat, e)`의 statement, witness, assumption, soundness error는 무엇인가?
- CP-link proof가 SNARK 내부에 포함되는지, 별도 auxiliary proof인지, verifier가 무엇을 검증하는지 명확한가?
- `epsilon_cc`가 message binding과 CP-link consistency를 동시에 포함하는데, 두 항의 concrete security reduction은 무엇인가?

현재 본문은 “QA-NIZK/CP-link checks”라고 말하지만, CP-link itself가 충분히 formalized되어 있지 않다. 이 상태에서는 보안 정리의 핵심 bad event가 실제 primitive로 닫혔다고 보기 어렵다.

**Required before submission:** `Msg`와 `CPLink`를 별도 subsection에서 concrete protocol로 명세하라. Security game, assumptions, error bound, in-circuit/out-of-circuit placement, proof size, verifier cost, constraint contribution을 표로 제시해야 한다. 이 부분이 닫히지 않으면 이번 revision의 핵심 개선이 심사에서 인정받기 어렵다.

### 2. The evaluation must prove that the new binding/linking path is actually included

Evaluation은 “sampled RS evaluations, Merkle openings, QA-NIZK/CP-link checks”가 포함되었다고 말한다. 그러나 main table의 숫자는 이전 버전과 동일해 보이며, 새로 추가된 message commitment verification과 CP-link path가 어느 정도 cost를 차지하는지 component breakdown이 없다.

이것은 사소한 reporting 문제가 아니다. 이번 버전의 security-evaluation correspondence는 다음 질문에 달려 있다.

> Table 1의 constraint/proving/proof-size 수치가 theorem에서 필요한 message binding과 CP-link consistency를 실제로 포함하는가?

현재 원고는 “포함한다”고 서술하지만, S&P 리뷰어는 artifact 없이 그 주장을 검증하기 어렵다. 특히 `Msg.Verify`가 Pedersen-style vector commitment라면 cost model이 매우 중요하다. 이것이 빠져 있거나 native/off-circuit으로 처리된다면, 보안 정리와 실험 수치 사이의 gap이 다시 열린다.

**Required before submission:** main evaluation 또는 appendix에 component-level breakdown을 추가하라.

| Component | Constraints | Prove time share | Verify time share | Proof bytes |
|---|---:|---:|---:|---:|
| folds |  |  |  |  |
| sampled RS evaluations |  |  |  |  |
| Merkle openings |  |  |  |  |
| message commitment verification |  |  |  |  |
| CP-link / QA-NIZK linking |  |  |  |  |

최소한 `k=1024`, `k=4096`, GPT-2 workload에 대해 이 breakdown이 필요하다. 이 표가 없으면 “new backend is implemented and measured”라는 주장이 약하다.

### 3. Raw input certification is still outside the system

이번 버전은 raw input certification gap을 더 정확히 표현한다. Intermediate-vector backend는 구현했다고 주장하고, raw input commitments `cm_A, cm_B, cm_C`는 certified input으로 가정한다. 이 framing은 이전보다 낫다.

하지만 논문이 여전히 verifiable computation, zkML/GPT-2 workload, matrix multiplication bottleneck을 전면에 내세우기 때문에, raw input certification은 critical하게 남는다. 실제 deployment에서 verifier는 다음을 알아야 한다.

- `cm_A, cm_B, cm_C`가 raw matrices/tensors의 row-wise encodings임을 누가 증명하는가?
- 이 certification의 proof size, verifier time, setup, public input size는 얼마인가?
- GPT-2 workload에서 commitments are reused across claims인지, 매 claim마다 새로 필요한지?
- model weights와 activations의 commitment lifecycle은 무엇인가?

현재 논문은 “deployment interface”라고 정직하게 말하지만, S&P systems/security paper로는 이것만으로는 약하다. 특히 GPT-2 case study를 사용한다면, 최소한 one concrete deployment path가 있어야 한다.

**Required before submission:** raw input certification을 완전히 구현하지 않더라도, one concrete deployment model을 정하고 비용과 trust boundary를 표로 제시하라. 예: public model weights, private activations, per-layer commitments, commitment reuse, verifier checks, preprocessing/setup cost. 이 표가 없으면 GPT-2 case study는 “checking-layer microbenchmark” 이상으로 해석되기 어렵다.

### 4. Baseline comparison remains too narrow for S&P significance

Freivalds SNARK baseline은 중요하고, 논문이 그 baseline 대비 좋은 결과를 보여주는 것도 사실이다. 그러나 S&P에서 “large matrix multiplication for VC/zkML” contribution으로 제출하려면 Freivalds 하나만으로는 significance defense가 약하다.

특히 지금 논문은 CP-link/message commitment backend를 사용하므로, 다음 계열과의 tradeoff가 더 중요해졌다.

- sumcheck/GKR-style systems;
- dedicated matrix VC / polynomial commitment approaches;
- code-based SNARKs or committed-codeword systems;
- batching-heavy zkML systems.

현재 related-work table은 qualitative positioning으로는 개선됐지만, accept를 설득하기에는 부족하다. 최소한 “왜 Freivalds-in-SNARK가 가장 relevant한 experimental baseline인가”를 강하게 방어하거나, 대표 non-Freivalds approach 하나와 정량 또는 semi-quantitative comparison을 제공해야 한다.

**Required before submission:** main body에 critical comparison table을 넣어라. 단순 related work가 아니라 verifier model, input model, setup, prover cost, verifier cost, proof size, batching, implementation status, and whether raw inputs or certified commitments are handled를 비교해야 한다.

## What Changed My Assessment

이전 리뷰보다 점수를 올린 이유는 명확하다. Intermediate-vector binding path가 더 이상 “unimplemented global `CodeComV`”에 의존하지 않고, sampled CP-link architecture로 바뀌었다. 이 변경은 논문의 theorem-evaluation gap을 줄인다.

하지만 새 구조가 accepted paper 수준이 되려면, CP-link/message commitment backend 자체가 더 이상 black box처럼 보이면 안 된다. 지금은 “좋은 방향의 설계”와 “완전히 닫힌 제출 논문” 사이에 있다.

## Final Assessment

현재 판정은 **Borderline Reject, 3.5 / 5**다.

이전보다 S&P 제출 가능성은 높아졌다. 그러나 지금 상태로 제출하면 리뷰어가 “CP-link/message commitment backend가 실제로 무엇이고, 그 비용과 보안이 main table에 어떻게 반영되었는가?”를 물을 가능성이 높다. 이 질문에 논문이 명확히 답하지 못하면 reject될 수 있다.

다음 revision의 최우선순위는 글 다듬기가 아니라 **CP-link/message commitment primitive의 formalization과 component-level evaluation breakdown**이다.
