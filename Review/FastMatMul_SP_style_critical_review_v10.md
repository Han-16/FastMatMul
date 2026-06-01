# FastMatMul Critical S&P-Style Review v10

검토 대상: `FastMatMul/main.tex` 및 포함 LaTeX 소스, 2026-05-26 현재 수정본  
리뷰 원칙: S&P 제출 전 accept/reject에 직접 영향을 줄 **critical issue만** 기록함. 사소한 문장, 표 위치, formatting, minor clarity는 제외함.

## Overall Recommendation

**Recommendation: Borderline Reject / Weak Reject**

**Overall score: 3.5 / 5**

이번 수정본은 이전보다 분명히 좋아졌다. 특히 이전 리뷰의 핵심 문제였던 “Groth16 witness와 auxiliary CP-link/opening verifier가 어떻게 연결되는가”에 대해 `wire handle` 구조를 도입했고, raw sampled matrix columns가 proof bytes가 아니라 Groth16 witness data라는 점도 명확히 설명했다. 따라서 이전 버전에서 제기된 proof-size contradiction은 상당 부분 해소되었다.

하지만 S&P 제출 직전 관점에서는 아직 risk가 남아 있다. 이제 문제는 아이디어의 방향이 아니라, **wire-handle/leaf-handle/CP-link backend가 독립적인 cryptographic primitive로 충분히 formalized and instantiated 되었는가**이다. 현재 원고는 이 backend를 설명하지만, S&P 리뷰어가 soundness assumption과 구현 비용을 audit할 수 있을 정도의 formal definition은 아직 부족하다.

## Critical Issues Only

### 1. Wire-handle / leaf-handle / CP-link backend is still under-specified

현재 구조는 다음과 같다.

- Groth16 witness는 sampled matrix column 또는 vector leaf `a_{\chi,j}`를 사용한다.
- Groth16 relation은 `wireV(Γ_{\chi,j}, a_{\chi,j}, ρ_{\chi,j}) = 1`을 증명한다.
- Auxiliary verifier는 Merkle path로 compact leaf handle `L_{\chi,j}`를 인증한다.
- CP-link는 `Γ_{\chi,j}`와 `L_{\chi,j}`가 같은 sampled object value에 bind된다고 주장한다.

이 구조는 이전보다 훨씬 낫다. 그러나 아직 central backend가 완전한 cryptographic primitive로 정의되어 있지 않다. 특히 다음이 명확하지 않다.

- `wireCom`, `wireV`의 정확한 scheme과 binding assumption
- `L_{\chi,j}`가 길이-`k` matrix column 또는 scalar vector coordinate에 어떻게 bind되는지
- `cpLinkP/cpLinkV`가 어떤 relation을 증명하는지
- CP-link soundness game에서 adversary가 무엇을 위조해야 하는지
- `wire handle`과 `leaf handle`이 vector-valued object와 scalar-valued object를 어떻게 공통 interface로 처리하는지
- 이 backend의 setup, CRS, public parameters, proof size, verifier cost가 어떤 assumption에 의존하는지

현재 theorem은 `epsilon_cc`를 message-binding/CP-link consistency error로 둔다. 하지만 그 error가 어떤 primitive의 어떤 game에서 나오는지 충분히 구체화되어 있지 않으면, security theorem이 사실상 “linking backend가 안전하다고 가정한다”에 머문다.

**Required before submission:** `wireCom/leaf-handle/CP-link`를 별도 subsection으로 formalize하라. 최소한 algorithms, syntax, public statement, witness, completeness, binding/linking soundness game, concrete instantiation, and measured cost를 넣어야 한다. 이 부분이 닫히면 논문의 technical soundness는 상당히 강해진다.

### 2. The proof-size story is now plausible, but only if compact handles are concretely instantiated

이전 버전의 가장 큰 수치상 문제는 sampled matrix columns가 public proof data라면 `k=4096,t=128`에서 수십 MB가 되어야 하는데, 논문은 `104 KB` proof를 주장한다는 점이었다. 이번 버전은 이를 다음 방식으로 해결한다.

- raw sampled matrix columns are private Groth16 witness values;
- serialized proof contains compact wire handles, leaf handles, Merkle paths, Groth16 proof, and CP-link material;
- publishing raw columns would add `Θ(tk)` field elements, but the current artifact avoids this.

이 설명은 방향상 타당하다. 다만 compact handle이 실제로 어떤 commitment인지, 길이-`k` column에 대한 handle이 몇 bytes인지, 그 opening을 Groth16 안에서 검증하는 비용이 어떻게 current constraint table에 들어가는지 아직 완전히 audit 가능하지 않다.

특히 `wire-handle openings`가 Groth16 constraints에 포함된다고 하지만, per-gadget breakdown은 없다. `k=4096`에서 constraint `1,667,305`가 fold, RS evaluation, message opening, wire opening 중 어디에 얼마나 쓰이는지 알 수 없다. S&P 리뷰어가 proof-size와 constraint count를 cross-check하기 어렵다.

**Required before submission:** object별 proof-material accounting을 추가하라. 예:

| Object | Raw value size | Serialized? | Commitment/handle size | Verified where | Cost included where |
|---|---:|---:|---:|---|---|
| sampled matrix column | `k` field elems | no | wire/leaf handle | Groth16 + AuxV | constraints + proof bytes |
| sampled vector leaf | 1 field elem | no/public handle only | wire/leaf handle | Groth16 + AuxV | constraints + proof bytes |
| Merkle path | `O(log n)` hashes | yes | path bytes | AuxV | proof bytes/verifier time |
| CP-link proof | backend-dependent | yes | proof bytes | AuxV | proof bytes/verifier time |

그리고 representative rows에서 constraint breakdown을 최소 2개 지점, 예를 들어 `k=1024`와 `k=4096`, 제공하라. 이 보완 없이는 `104 KB` result가 구현을 신뢰해야만 받아들여지는 숫자로 남는다.

### 3. Raw-input certification remains outside the evaluated system

현재 원고는 이 한계를 정직하게 인정한다. `cm_A, cm_B, cm_C`는 certified encoded roots로 가정되고, raw matrices 또는 ML tensors에서 이 roots를 생성하고 인증하는 비용은 online checker 밖에 있다. GPT-2 결과도 “checking-layer case study over certified roots”로 낮아졌다. 이는 좋은 수정이다.

하지만 S&P 제출에서 여전히 중요한 limitation이다. 특히 activation/output matrices는 per-request로 생성되므로, model weights처럼 한번 certify하고 amortize하기 어렵다. 논문이 verifiable computation 또는 ML workload를 motivation으로 유지한다면 reviewer는 다음을 물을 가능성이 높다.

- per-request activation roots는 누가 certify하는가?
- verifier는 raw activation/output과 certified root의 관계를 어떻게 신뢰하는가?
- input certification cost가 online checking gain을 상쇄하지 않는가?
- certified-root interface가 실제 deployment에서 natural한가?

이 문제는 논문이 “checking-layer only”로 제출된다면 reject blocker는 아닐 수 있다. 하지만 현재 abstract/introduction/evaluation이 여전히 VC/ML application을 강하게 언급하므로, S&P에서는 critical limitation으로 남는다.

**Required before submission:** 하나의 deployment model을 선택해 raw-to-certified-root path를 정량 또는 준정량으로 설명하라. 완전 구현이 어렵다면 abstract와 contribution에서 GPT-2를 “end-to-end VC workload”가 아니라 “certified-root checking-layer workload”라고 더 명확히 제한해야 한다.

### 4. Baseline comparison is defensible but still narrow

Freivalds-in-SNARK baseline은 이제 꽤 잘 방어되어 있다. 같은 Groth16 stack, 같은 committed matrix-multiplication statement, 직접적인 `O(k^2)` baseline이라는 점에서 primary baseline으로 타당하다.

그러나 S&P significance를 설득하려면 broader landscape 방어가 아직 약하다. Related work table은 개선되었지만 여전히 qualitative이다. Sumcheck/GKR, dedicated matrix VC, code-based SNARK와 직접 head-to-head가 어렵다는 설명은 이해되지만, reviewer가 “왜 이 접근이 top-tier contribution인가?”를 물을 때 Freivalds 하나만으로는 부족할 수 있다.

이 이슈는 앞의 formal backend 문제보다 덜 치명적이다. 그래도 accept 가능성을 높이려면 최소한 하나의 non-Freivalds family에 대해 normalized analytical comparison을 main body에서 더 강하게 제공하는 것이 좋다.

**Required before submission:** quantitative implementation까지는 아니어도, proof size / prover work / verifier work / setup / input model / batching 여부를 기준으로 representative alternatives와 normalized comparison을 추가하라.

## Decision-Relevant Assessment

이 버전은 v8 대비 실질적으로 개선되었다. 특히 다음 두 점은 긍정적이다.

- sampled matrix columns가 serialized proof data가 아니라 Groth16 witness라는 점을 명확히 하여 proof-size contradiction을 줄였다.
- `wire handle`을 public statement에 넣고 Groth16이 그 opening을 증명하게 하여, Groth16 witness와 auxiliary verifier 사이의 연결 구조를 제시했다.

남은 문제는 이제 논문 전체의 방향이 아니라 backend formalization의 완성도다. `wireCom`, compact leaf handles, CP-link가 정확히 정의되고 cost breakdown이 보강되면, 이 논문은 borderline accept까지 갈 수 있다. 반대로 이 부분이 계속 black-box assumption처럼 보이면, S&P 리뷰에서는 “핵심 linking primitive가 논문 안에서 충분히 명세되지 않았다”는 이유로 reject될 가능성이 높다.

## What Would Change the Decision

판정을 올리기 위한 최우선 수정은 다음 두 가지다.

1. `wireCom/leaf-handle/CP-link` backend를 formal primitive로 정의하고, theorem이 그 soundness game을 정확히 사용하도록 정리한다.
2. proof-material and constraint accounting을 object별로 분해해 `104 KB` proof size와 `O(k)` constraint growth를 독립적으로 검증 가능하게 만든다.

그 다음이 raw-input certification model과 broader comparison이다.

## Final Recommendation

**Borderline Reject / Weak Reject, 3.5 / 5.**

현재 논문은 S&P 제출권에 가까워졌다. 하지만 지금 바로 제출하기에는 central backend formalization이 아직 약하다. 다음 revision에서 wire-handle/CP-link primitive와 accounting을 닫으면, reject에서 borderline accept로 넘어갈 가능성이 있다.
