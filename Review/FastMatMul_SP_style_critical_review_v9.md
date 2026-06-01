# FastMatMul Critical S&P-Style Review

검토 대상: `FastMatMul/main.tex` 및 포함 LaTeX 소스, 2026-05-26 현재 수정본  
리뷰 원칙: S&P 제출 전 accept/reject에 직접 영향을 줄 **critical issue만** 기록함. 문장 polish, 소규모 formatting, 사소한 설명 개선은 제외함.

## Overall Recommendation

**Recommendation: Weak Reject / Not ready for S&P submission**

**Overall score: 3.0 / 5**

이번 수정본은 이전보다 한 단계 진전했다. 가장 큰 변화는 기존의 추상적 `CodeComV` gap을 줄이고, message commitment + sampled RS evaluation + Merkle opening + QA-NIZK/CP-link로 구성된 구체적 intermediate backend를 제시한 점이다. 또한 theorem-to-artifact correspondence table, component breakdown, deployment boundary, related-work comparison도 추가되어 논문의 방어력이 좋아졌다.

하지만 S&P 제출 관점에서는 아직 위험하다. 이제 핵심 blocker는 단순히 “`CodeComV`가 없다”가 아니라, **새 CP-linked construction이 보안 정리와 평가 수치에 정확히 대응하는지 불명확하다**는 점이다. 특히 Groth16 witness와 auxiliary CP-link/opening verifier 사이의 연결, 그리고 proof-size accounting이 현재 설명만으로는 충분히 검증되지 않는다.

## Critical Issues Only

### 1. CP-link와 Groth16 witness의 연결이 충분히 formal하지 않다

새 construction은 SNARK 내부에서 `\hat e_{v,j}=enc(v)_j`를 계산하고, auxiliary `CP-link / QA-NIZK`가 이 값을 외부 Merkle leaf `e_{v,j}`와 연결한다고 설명한다. 이 변경은 방향은 좋지만, 현재 원고의 formal interface는 아직 S&P 리뷰어를 설득하기 어렵다.

문제는 `\hat e_{v,j}`가 Groth16 witness 내부 값이라는 점이다. Auxiliary verifier가 `cpLinkV(tau, \hat e, e)`를 검증하려면 다음 중 하나가 명확해야 한다.

- `\hat e`가 public value로 노출된다.
- Groth16 proof 안의 private witness wire에 대한 commitment가 있고, CP-link가 그 commitment와 external leaf를 연결한다.
- Groth16 relation과 CP-link proof가 같은 commitment/opening statement를 공유한다.

현재 논문은 “SNARK-side committed value”라는 표현을 쓰지만, 그 commitment가 무엇인지, Groth16 proof와 CP-link proof가 어떤 common reference/string/commitment를 공유하는지, adversary가 SNARK에서는 `\hat e`를 쓰고 CP-link에서는 다른 값을 쓰는 것을 어떻게 막는지 충분히 formalize하지 않는다.

이는 minor clarity 문제가 아니다. Soundness proof는 accepted CP-link가 “the sampled external opening equals the circuit-computed `enc(v)_j`”라는 사실에 의존한다. 이 연결이 정확히 정의되지 않으면 theorem의 핵심 conditioning step이 성립하지 않는다.

**Required before submission:** CP-link를 별도 cryptographic primitive로 정의하라. 최소한 setup, prove, verify, public statement, witness, binding target, soundness game, Fiat-Shamir transcript binding, and how it links to the Groth16 witness commitment를 명시해야 한다. 지금처럼 `cpLinkV(tau, \hat e, e)`만 쓰면 central security assumption이 black box로 남는다.

### 2. Proof-size accounting appears inconsistent with sampled matrix-column openings

논문은 matrix commitments가 encoded columns에 대한 Merkle roots라고 정의한다. Fold check는 각 sampled position `j`에서 `enc(A)^(j)`, `enc(B)^(j)`, `enc(C)^(j)`라는 길이 `k` column을 필요로 한다. 만약 Merkle openings와 opened columns가 auxiliary proof data로 verifier에게 제공된다면, proof size는 최소한 `Omega(tk)` field elements가 되어야 한다.

예를 들어 `k=4096`, `t=128`, field element가 32 bytes라고 하면, 세 입력 행렬의 sampled columns만으로도 대략

`3 * 128 * 4096 * 32 ≈ 50 MB`

수준이다. 하지만 논문은 `k=4096`에서 `fmQA` proof size를 약 `104 KB`로 보고한다. 이 수치는 길이-`k` sampled matrix columns가 public proof material에 포함된 경우와 맞지 않는다.

반대로 sampled columns가 Groth16 witness 안에 숨어 있고 verifier에게 공개되지 않는다면, auxiliary Merkle verifier는 그 columns를 직접 검증할 수 없다. 이 경우 Merkle verification이 Groth16 내부에 있어야 하거나, matrix-column values에 대해서도 별도의 commitment/link proof가 필요하다. 그러나 현재 설명은 Merkle path verification을 auxiliary verifier가 수행한다고 쓰고, CP-link는 주로 intermediate vector leaves에 대해 설명한다.

즉 현재 원고는 다음 셋 중 무엇인지 명확하지 않다.

- sampled matrix columns are public auxiliary data: then proof size table is wrong or incomplete.
- sampled matrix columns are private Groth16 witnesses: then auxiliary Merkle opening story is incomplete.
- sampled matrix columns are linked through another commitment mechanism: then that mechanism must be formally specified and measured.

**Required before submission:** proof-size accounting table을 relation data type별로 분해하라. 특히 sampled input-matrix columns, intermediate vector leaves, Merkle paths, Groth16 proof, CP-link proof, public commitments가 각각 public proof bytes인지, SNARK witness인지, auxiliary witness인지 명확히 해야 한다. 현재 `104 KB` claim은 이 설명 없이는 신뢰하기 어렵다.

### 3. The theorem-to-artifact correspondence is improved but not yet auditably complete

새 evaluation table은 theorem component와 artifact component를 대응시키려는 점에서 개선이다. 하지만 “evaluated artifact matches the online multiplication-checking relation”이라는 주장은 아직 너무 강하다.

이유는 두 가지다.

첫째, CP-link가 Groth16 witness와 어떻게 연결되는지 formal하지 않으므로, artifact가 theorem의 `epsilon_cc` assumption을 실제로 만족하는지 확인할 수 없다.

둘째, Merkle openings가 auxiliary로 처리되는 경우, Groth16 relation이 fold에 사용한 matrix/vector values와 auxiliary verifier가 인증한 values가 동일하다는 것을 보장하는 연결이 모든 opened object에 대해 필요하다. 현재 설명은 intermediate vector leaves에 대해서는 CP-link를 말하지만, matrix columns와 fold inputs 전체에 대해 동일한 correspondence가 닫혀 있는지 불명확하다.

**Required before submission:** “full verifier acceptance relation”을 하나의 formal relation으로 다시 써라. Groth16 verifier, auxiliary Merkle verifier, CP-link verifier가 각각 어떤 public values를 공유하고, 어떤 hidden values를 bind하며, 전체 accept가 어떤 single statement에 대한 proof인지 보여야 한다.

### 4. Raw-input certification remains outside the evaluated system

이전보다 boundary는 명확해졌다. 논문은 이제 raw input certification을 online checker 밖으로 빼고, certified encoded roots를 precondition으로 둔다. 이 선택은 modular paper로는 가능하다.

하지만 S&P 제출에서 GPT-2 workload와 verifiable computation application을 강하게 내세우는 경우, raw tensors에서 certified encoded commitments까지의 pipeline이 빠진 것은 여전히 critical limitation이다. 특히 activation/output matrices는 per-request object이므로, model weights처럼 amortize된다고 보기 어렵다. 현재 deployment table은 이 gap을 인정하지만, 비용이나 verifier trust model을 닫지는 않는다.

이 문제는 앞의 CP-link/proof-size 문제가 해결된 뒤에도 남는다. 현재 논문은 “online multiplication checker”로는 설득력이 커졌지만, “VC for ML workload”로는 아직 end-to-end story가 부족하다.

**Required before submission:** 최소 하나의 concrete deployment mode를 선택해서 raw-to-certified-root cost, verifier checks, public input size, amortization 가능 여부를 정량 또는 준정량으로 제시하라. 완전 구현이 어렵다면 GPT-2 결과를 “checking-layer case study”로 더 낮춰야 한다.

## Decision-Relevant Assessment

이 버전은 이전보다 좋아졌다. 특히 추상적 `CodeComV`를 계속 들고 가는 대신, CP-linked sampled-opening backend로 실제 구현 경계를 좁힌 점은 의미 있는 진전이다. 따라서 이전 리뷰의 “standalone `CodeComV` 미구현”이라는 비판은 더 이상 같은 형태로 적용되지 않는다.

하지만 새 구조가 성공하려면 CP-link/SNARK/Merkle 세 검증 세계가 하나의 statement에 단단히 묶여야 한다. 현재 원고는 그 부분을 충분히 formal하게 닫지 못했고, proof-size 수치도 sampled matrix-column openings와 직관적으로 맞지 않는다. 이 두 문제는 S&P 리뷰에서 바로 공격받을 가능성이 높다.

## What Would Change the Decision

판정을 올리려면 다음 두 가지가 가장 중요하다.

1. CP-link primitive와 Groth16 witness-linking semantics를 formalize하고, theorem proof에서 해당 soundness game을 정확히 사용하라.
2. Proof-size/proof-material accounting을 object별로 다시 제시해 `104 KB` claim이 sampled matrix-column openings와 모순되지 않음을 보여라.

그 다음 우선순위가 raw-input certification pipeline과 broader baseline comparison이다.

## Final Recommendation

**Weak Reject, 3.0 / 5.**

현재는 제출 가능한 형태에 가까워졌지만, 아직 S&P에 바로 내기에는 central consistency risk가 있다. 다음 revision은 더 많은 실험을 추가하기보다, **CP-link와 Groth16 witness의 formal binding, 그리고 proof-size accounting**을 먼저 닫아야 한다.
