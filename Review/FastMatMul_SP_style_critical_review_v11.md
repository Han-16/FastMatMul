# FastMatMul Critical S&P-Style Review v11

검토 대상: `FastMatMul/main.tex` 및 포함 LaTeX 소스, 2026-05-26 현재 수정본  
리뷰 원칙: S&P 제출 전 accept/reject에 직접 영향을 줄 **critical issue만** 기록함.

## Overall Recommendation

**Recommendation: Borderline Reject / Weak Reject**

**Overall score: 3.5 / 5**

이번 버전은 v10 대비 실질적으로 개선되었다. `wireCom/wireV`, compact leaf handle, CP-link syntax, proof-material accounting, constraint accounting, normalized comparison이 추가되어 이전 리뷰의 주요 지적을 상당 부분 반영했다. 특히 sampled matrix columns가 serialized proof data가 아니라 Groth16 witness라는 점은 이제 명확하다.

그럼에도 S&P에 바로 제출하기에는 아직 위험하다. 남은 핵심 문제는 논문의 중심 backend인 **CP-linked sampled-opening backend가 아직 독립적으로 audit 가능한 primitive 수준으로 완전히 닫히지 않았다**는 점이다. 현재 설명은 방향은 맞지만, syntax와 soundness game, concrete cost가 일부 불명확하다.

## Critical Issues Only

### 1. CP-link primitive syntax is still not fully coherent

현재 정의는 다음 구조를 둔다.

- `Γ = wireCom(para, a; ρ)`는 Groth16 witness value `a`에 대한 public wire handle이다.
- `L`은 Merkle tree가 authenticate하는 compact leaf handle이다.
- `cpLinkP(para,T,Γ,L,a,ρ)`가 `Γ`와 `L`이 같은 sampled object value에 bind됨을 증명한다.

하지만 as written, `cpLinkP`의 witness에 **leaf handle opening randomness**가 없다. 만약 `L`도 Pedersen-style handle이라면, `L`이 같은 `a`에 대한 commitment임을 증명하려면 보통 `L`의 opening randomness 또는 equivalent witness가 필요하다. 반대로 `L`이 deterministic handle이라면 hiding/binding syntax와 cost가 달라지는데, 그 점이 명시되어 있지 않다.

이 문제는 단순 notation 문제가 아니다. Soundness proof는 “authenticated leaf handle `L` is bound to the same value used by the Groth16 fold relation”에 의존한다. 그런데 CP-link relation의 witness가 `L`의 opening을 어떻게 알고 증명하는지 불명확하면, `epsilon_link`의 의미가 black-box assumption으로 남는다.

**Required before submission:** CP-link relation을 정확히 써야 한다. 예를 들어 Pedersen handles라면 `Γ = ρ_Γ H + <a,G>`와 `L = ρ_L H + <a,G>`를 두고, CP-link witness가 `(a, ρ_Γ, ρ_L)` 또는 `(a, ρ_Γ - ρ_L)` 중 무엇인지 명시하라. 또한 scalar/vector-valued object에 대해 같은 relation이 어떻게 적용되는지, proof size가 `d=k`일 때 왜 보고된 크기로 유지되는지 명확히 하라.

### 2. CP-link proof size and setup/key size are not yet auditably justified

논문은 QA-NIZK/CP-link proof가 compact하고, main table에서 `k=4096` proof size가 `104 KB`라고 보고한다. Proof-size contradiction은 이전보다 많이 줄었지만, 아직 다음이 불명확하다.

- vector-valued matrix column handle의 dimension은 `d=k`인데, CP-link proof size가 dimension에 어떻게 의존하는가?
- `Link.Setup(1^λ,d_max)`가 `d_max=k`에 대해 생성하는 public parameters/CRS size는 얼마인가?
- `G_1,...,G_d` 같은 generator material이 setup/key size에 포함되는가?
- proof bytes table에 public wire handles, leaf handles, Merkle paths, CP-link proofs가 각각 몇 개, 몇 bytes로 들어가는가?

현재 artifact는 setup/key size를 보고하지 않고, proof-material table도 object category 수준이다. S&P 리뷰어가 `104 KB` proof size와 `O(k)` checking cost를 독립적으로 재계산하기에는 정보가 부족하다.

**Required before submission:** representative rows에 대해 byte-level accounting을 추가하라. 최소한 `k=1024`, `k=4096`에서 wire handles, leaf handles, Merkle paths, Groth16 proof, CP-link proofs, message commitments, public roots의 개수와 byte size를 분해해야 한다. 또한 CRS/setup/key size를 별도 표로 보고하라.

### 3. Security theorem still relies on a backend assumption that needs a sharper game

Theorem은 `epsilon_cc <= epsilon_msg + epsilon_link`로 soundness를 정리한다. 하지만 `epsilon_link`의 game은 아직 충분히 날카롭지 않다. 현재 설명은 adversary가 accepting tuple을 만들었는데 `L`이 같은 value에 bind되지 않는 경우를 막는다고 말한다. 그러나 실제 composed protocol에서는 다음을 함께 다뤄야 한다.

- Groth16 knowledge soundness 또는 extractability로 `a`와 `ρ_Γ`를 어떻게 얻는가?
- auxiliary CP-link proof와 Groth16 proof가 같은 `Γ`와 transcript `T`에 묶였다는 것을 어떤 game에서 보장하는가?
- Merkle position binding은 `L`에 대한 binding이고, `L`에서 raw column value로의 binding은 CP-link/handle binding에 의존하는데, 이 두 binding을 어떻게 composition하는가?
- Fiat-Shamir transcript에서 adversary가 `Γ`, `L`, `τ`를 adaptive하게 고르는 순서가 game에 반영되는가?

현재 proof sketch는 직관적으로 맞는 방향이지만, S&P cryptography reviewer에게는 “backend soundness assumed”로 보일 가능성이 있다.

**Required before submission:** CP-linked backend에 대한 explicit security game을 제시하고, main theorem proof에서 “condition on no backend failure”가 정확히 그 game의 failure event와 일치함을 보여라. 특히 Groth16 extractor와 CP-link soundness의 composition boundary를 명시해야 한다.

### 4. Raw-input certification remains the main systems-level limitation

논문은 이 점을 정직하게 제한하고 있다. `cm_A, cm_B, cm_C`는 certified encoded roots로 가정되며, raw matrices 또는 ML tensors에서 이 roots를 생성/인증하는 비용은 online checker 밖에 있다. GPT-2도 “checking-layer case study over certified roots”라고 낮춰 쓴 점은 좋다.

하지만 S&P systems/security 관점에서는 여전히 중요한 limitation이다. 특히 activation/output matrices는 per-request object라서, static model weights처럼 쉽게 amortize되지 않는다. 현재 성능 결과가 실제 verifiable inference pipeline에서 유지되는지는 아직 불명확하다.

**Required before submission:** raw-to-certified-root path를 최소 하나의 concrete deployment model로 제시하라. 완전 구현이 어렵다면, certification cost가 online checker gain을 상쇄하지 않는다는 analytical bound 또는 cost estimate라도 필요하다.

## Decision-Relevant Assessment

v11 현재 원고는 S&P 제출권에 가까워졌다. 이전의 큰 contradiction들은 많이 줄었다.

- `CodeComV` black box 문제는 CP-linked sampled-opening backend로 상당히 구체화되었다.
- sampled matrix columns와 proof-size accounting 문제는 wire/leaf handle 설명으로 상당히 해소되었다.
- Freivalds baseline 사용도 이제 어느 정도 방어 가능하다.

남은 blocker는 backend formalization이다. 이 논문은 이제 아이디어 논문이라기보다, `wire handle + leaf handle + CP-link`라는 구체 backend에 기대는 protocol/evaluation paper가 되었다. 따라서 그 backend가 완전히 formal하고 auditable해야 한다.

## What Would Change the Decision

판정을 올리려면 다음 두 가지가 가장 중요하다.

1. CP-link relation과 soundness game을 정확히 formalize하고, leaf handle opening witness 및 Groth16 extraction/composition을 명확히 한다.
2. Proof bytes, CRS/setup/key size, and constraint components를 representative rows에서 재계산 가능하게 분해한다.

이 두 항목이 닫히면 **Borderline Accept**까지 올라갈 수 있다.

## Final Recommendation

**Borderline Reject / Weak Reject, 3.5 / 5.**

현재 원고는 상당히 개선되었지만, S&P 제출 직전 기준으로는 central backend가 아직 충분히 검증 가능하게 명세되지 않았다. 다음 revision은 더 많은 headline number보다, CP-link backend의 formal game과 byte/constraint accounting을 닫는 데 집중해야 한다.
