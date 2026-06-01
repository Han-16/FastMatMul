# FastMatMul S&P-Style Review

검토 대상: `FastMatMul/main.tex` 및 포함된 LaTeX 소스, 2026-05-22 수정본  
리뷰 양식: IEEE S&P 실제 양식을 정확히 알 수 없으므로, 보안/암호학 학회에서 흔히 쓰는 S&P-style 점수형 리뷰 양식으로 작성함.

## Overall Recommendation

**Recommendation: Weak Reject / Borderline Reject**

**Overall score: 2.5 / 5**

현재 원고는 이전 버전보다 상당히 개선되었다. 특히 주장을 “완전한 end-to-end 시스템”이 아니라 “matrix-checking layer”로 제한했고, QA-NIZK 기반 구현, GPT-2 workload 사례, 하드웨어 및 timing scope, Fiat-Shamir 손실과 구체적인 `t` 선택의 차이를 명시한 점은 긍정적이다.

그러나 S&P 제출 품질로 보기에는 아직 핵심적인 gap이 남아 있다. 논문의 주된 asymptotic 및 실험적 이득은 linear-time code-commitment backend, 특히 독립적으로 구현 및 측정된 `CodeComV`가 존재한다는 조건에 의존한다. 현재 artifact는 이 backend를 독립적으로 구현하거나 측정하지 않으며, 본문도 이를 명시한다. 따라서 현재 결과는 설득력 있는 checking-layer prototype이지만, S&P accept 수준의 완결된 cryptographic system/evaluation으로 보기는 어렵다.

## Score Summary

| Category | Score | Rationale |
|---|---:|---|
| Overall merit | 2.5 / 5 | 흥미로운 아이디어와 개선된 서술이 있으나 핵심 backend가 조건부임 |
| Novelty | 3.5 / 5 | Freivalds, code proximity, SNARK circuit reduction의 조합은 흥미롭고 응용 가치가 있음 |
| Technical soundness | 3.0 / 5 | 보안 정리는 훨씬 명확해졌지만 concrete backend와 parameter certificate가 미완성 |
| Significance | 3.0 / 5 | matrix multiplication SNARK 병목을 줄이는 방향은 중요하나 현재는 layer-level result |
| Evaluation | 2.5 / 5 | QA-NIZK 및 GPT-2 사례는 개선이나 end-to-end/backend/memory/variance가 부족 |
| Presentation | 3.5 / 5 | 제한사항과 scope가 명확해졌고 읽기 쉬우나 S&P 제출 형식 및 claim framing 보완 필요 |
| Reproducibility | 2.5 / 5 | 일부 artifact column은 언급되지만 핵심 backend, peak RSS, 반복실험 통계가 없음 |
| Reviewer confidence | 4 / 5 | 암호 프로토콜 구조, SNARK evaluation, 보안 주장 관점에서 충분히 판단 가능 |

## Paper Summary

이 논문은 큰 행렬곱 검증을 SNARK 안에서 직접 수행하지 않고, Freivalds-style randomized check와 error-correcting code proximity check를 결합해 matrix multiplication checking layer의 circuit size를 줄이는 프로토콜을 제안한다. 주장하는 비용은

`O(tk + t log n + E_cc(k))`

이며, 선택된 code-commitment backend의 검증 비용 `E_cc(k)`가 linear-time이면 checking circuit은 `O(tk)`가 된다.

보안 정리는 certified encoded input commitments 및 code-commitment backend에 상대적인 computational soundness를 주장하며, error term은 대략

`epsilon_SNARK + epsilon_cc + epsilon_bind + (k-1)/|F| + 4(1-delta)^t`

이고 Fiat-Shamir non-interactive variant에는 추가 random-oracle loss `epsilon_FS(q_H)`가 붙는다.

구현은 `fmQA`라는 QA-NIZK 기반 multiplication-checking layer를 평가한다. 주요 결과는 `k=4096`에서 Freivalds SNARK baseline 대비 constraint `30.29x` 감소, proving time `7.18x` 개선, proof size `104 KB`이며, `k=8192`에서는 `126 KB` proof를 보고한다. GPT-2-style workload에서는 36개 matrix multiplication claim에 대해 constraint `2.30x`, proving time `1.77x` 개선을 보인다.

## Strengths

1. **Scope가 훨씬 명확해졌다.**  
   본문은 현재 구현이 end-to-end system이 아니라 multiplication-checking layer라는 점을 명시한다. 이는 이전 버전에서 가장 위험했던 overclaim을 상당 부분 완화한다.

2. **보안 정리의 조건과 손실항이 더 명시적이다.**  
   certified commitments, `CodeComV`, position binding, global codeword binding, Fiat-Shamir loss, grinding bound, `4(1-delta)^t` union bound가 더 분명해졌다. 특히 `t=128`이 `delta=1/2`일 때 strict 128-bit proximity가 아니라 `2^-126` proximity term이라는 설명은 정직하고 중요하다.

3. **QA-NIZK 기반 구현은 실용성 면에서 이전보다 설득력이 있다.**  
   proof size가 `k=4096`에서 `104 KB`, `k=8192`에서 `126 KB`로 제시되어, 이전의 큰 proof-size 우려가 줄었다. verifier overhead는 남아 있지만, primary artifact가 더 현실적인 방향으로 이동했다.

4. **GPT-2 workload case study가 추가되어 응용 맥락이 좋아졌다.**  
   단일 행렬곱 benchmark뿐 아니라 36개 matrix multiplication claim으로 구성된 workload를 제시한 점은 S&P 독자에게 더 의미 있는 evidence가 된다.

5. **실험 조건과 limitation disclosure가 개선되었다.**  
   CPU, RAM, field size, `rho`, `n`, `t`, timing scope, 제외된 비용을 명시하고, standalone `CodeComV`, peak memory, repeated-run variance가 없다는 점을 숨기지 않는다.

## Major Weaknesses

### 1. 핵심 contribution이 여전히 conditional backend에 의존한다

가장 큰 문제는 `E_cc(k)=O(k)`를 만족하는 code-commitment backend가 실험적으로 닫히지 않았다는 점이다. 논문은 theorem을 modular하게 서술하고, 현재 artifact가 standalone `CodeComV`를 구현/측정하지 않는다고 명시한다. 이 정직한 서술은 좋지만, S&P acceptance 관점에서는 여전히 major blocker다.

현재 실험 결과는 “linear-time backend가 주어졌을 때 checking layer가 빠르다”를 보여준다. 하지만 전체 시스템의 성능, soundness, verifier cost, proof size, setup/key size는 실제 backend 선택에 따라 크게 달라질 수 있다. 특히 dense codeword-validity check를 사용하면 quadratic overhead가 다시 등장한다는 점을 본문도 인정한다. 따라서 논문 제목/초록/결론의 임팩트는 구현이 실제로 닫은 범위보다 커 보일 수 있다.

S&P 제출 전에는 다음 중 하나가 필요하다.

- concrete `CodeComV` backend를 선택하고, position binding/global codeword binding을 포함한 전체 relation을 구현 및 측정한다.
- 또는 논문을 명확히 theoretical/modular protocol paper로 재포지셔닝하고, 실험 claim을 checking-layer microbenchmark로 낮춘다.

### 2. concrete security parameterization이 아직 deployment certificate 수준은 아니다

본문은 `t=128`이 `delta=1/2`에서 proximity term `2^-126`에 해당하고 strict 128-bit proximity에는 `t=130`이 필요하다고 설명한다. 이 수정은 좋다. 하지만 main experimental table은 여전히 `t=128`을 사용한다. 또한 실제 선택 backend의 certified distance `delta`가 무엇인지, aggregate soundness budget을 `SNARK`, `CodeCom`, binding, Freivalds term, FS loss 사이에 어떻게 배분하는지 명확한 deployment certificate가 없다.

S&P 리뷰어는 “실험에 사용한 parameter가 논문이 주장하는 보안 수준을 만족하는가?”를 확인하려 할 가능성이 높다. 현재 원고는 그 질문에 부분적으로만 답한다.

필요한 보완은 다음과 같다.

- main benchmark에 strict target parameter row를 추가한다. 예: `lambda=128`, backend-certified `delta`, required `t`.
- `epsilon_SNARK`, `epsilon_cc`, `epsilon_bind`, `epsilon_FS(q_H)`, `(k-1)/|F|`, proximity term을 포함한 concrete soundness budget table을 제공한다.
- `delta=1/2`가 실제 backend에서 어떻게 보장되는지, 또는 더 작은 `delta`일 때 비용이 어떻게 변하는지 제시한다.

### 3. evaluation이 아직 S&P artifact/evidence 수준에 부족하다

현재 evaluation은 이전보다 강해졌지만, top-tier systems/security venue 기준으로는 아직 부족하다.

부족한 항목은 다음과 같다.

- standalone `CodeComV` cost가 없다.
- peak resident memory가 없다.
- repeated-run variance 또는 confidence interval이 없다.
- setup/key size가 없다.
- verifier time이 QA-NIZK/opening material 때문에 Freivalds보다 큰데, application-level impact 분석이 부족하다.
- Freivalds baseline은 `k=8192`에서 측정되지 않았다.
- baseline이 사실상 optimized Freivalds SNARK 하나로 제한된다.
- proving time이 native matrix multiplication과 setup을 제외하는데, headline speedup에서는 이 scope가 더 강하게 반복되어야 한다.

GPT-2 case study는 좋은 추가이지만, 여기서도 `fmQA` verification은 `4.94s`로 Freivalds `0.49s`보다 약 `10x` 느리다. 이 overhead가 실제 verifiable inference setting에서 허용 가능한지, batching이나 amortization으로 줄일 수 있는지 분석이 필요하다.

### 4. claim framing이 아직 조심스러워야 한다

초록은 “We present a verifiable computation protocol”이라고 말하면서, 뒤에서 “multiplication-checking layer” 및 “relative to certified encoded input commitments and code-commitment backend”라고 제한한다. 본문은 이 제한을 상당히 잘 설명하지만, S&P 심사에서는 초록과 introduction의 첫인상이 중요하다.

현재 수준에서는 다음 표현이 더 안전하다.

- “a matrix-multiplication checking layer for verifiable computation”
- “conditional on a code-commitment backend”
- “not yet an end-to-end commitment-generation system”

즉, contribution을 낮추라는 뜻이 아니라, 논문이 실제로 증명하고 측정한 범위와 claim의 범위를 완전히 일치시켜야 한다.

### 5. 제출 형식과 polish가 아직 S&P-ready가 아니다

빌드 결과는 15 pages이고, `main.tex`에는 여전히 ACM CCS metadata, placeholder DOI/ISBN, ACM bibliography style이 남아 있다. 로그에도 ACM keywords/CCS concepts 관련 warning이 있다. S&P 제출 전에는 IEEE S&P template, page limit, anonymity, artifact appendix 위치, reference formatting을 재정리해야 한다.

## Detailed Comments

### Security proof

보안 proof structure는 이전보다 훨씬 낫다. input roots가 `r` 전에 certified되고, intermediate roots가 query tuple `I` 전에 고정되어야 한다는 ordering을 명시한 점은 중요하다. with-replacement sampling도 명확해졌다.

다만 proof가 의존하는 backend contract가 실제 instantiation에서 어떻게 만족되는지 더 구체화되어야 한다. 특히 `CodeComV(cm_v, v, sigma_v)=1`과 position opening `openV(pi_j, a, cm_v, j)=1`이 동시에 어떤 cryptographic assumption 아래에서 global codeword binding과 position binding을 보장하는지, 그리고 그 비용이 circuit 안에서 어떻게 나타나는지 명확한 instantiation section이 필요하다.

### Evaluation

`fmQA`의 primary benchmark는 좋은 방향이다. `k=4096`에서 constraint `1,667,305` 대 Freivalds `50,495,818`, proving time `56.44s` 대 `405.04s`는 layer-level result로는 강하다. 또한 proof size가 `104,388B`로 정리된 것은 긍정적이다.

하지만 이 수치를 “matrix multiplication VC 전체의 성능”으로 읽으면 안 된다. 현재 표는 dense codeword-validity check를 제외하고, standalone `CodeComV`를 포함하지 않는다. 이 사실이 caption과 text에는 있지만, abstract/conclusion의 headline number에서도 같은 조건을 반복해야 한다.

### Presentation

논문은 현재 상당히 읽기 쉬워졌다. 특히 limitation paragraph는 S&P 리뷰어에게 신뢰를 준다. 다만 “linear-time backend model”이라는 표현이 여러 번 나오지만, 독자가 실제 선택 가능한 backend 후보와 tradeoff를 한눈에 보기 어렵다. 관련 연구 또는 construction 후반에 backend comparison table을 추가하는 것이 좋다.

추천 table column은 다음과 같다.

| Backend candidate | Setup | Assumption | `E_cc(k)` | proof/opening size | verifier cost | certified `delta` | implemented? |
|---|---|---:|---:|---:|---:|---:|---|

## Questions for Authors

1. 실제 S&P submission에서 선택할 concrete `CodeComV` backend는 무엇인가?
2. 해당 backend의 certified relative distance `delta`는 얼마이며, main benchmark의 `t`는 그 `delta`에 대해 어떤 security level을 달성하는가?
3. raw input matrix에서 certified encoded input commitments까지의 end-to-end pipeline은 누가 수행하고, verifier는 무엇을 신뢰하는가?
4. `fmQA` verifier가 GPT-2 workload에서 Freivalds보다 약 `10x` 느린데, target deployment에서 이 tradeoff는 왜 acceptable한가?
5. peak memory와 repeated-run variance를 추가하면 Freivalds OOM 또는 large-`k` failure claim이 어떻게 바뀌는가?
6. setup/key sizes와 proof material breakdown은 어떻게 되는가?

## Required Revisions Before S&P Submission

1. **Concrete backend closure**  
   `CodeComV`를 실제 구현하고, theorem에서 요구하는 binding/proximity assumptions와 evaluation table을 연결해야 한다. 이것이 어렵다면 논문을 “conditional checking-layer protocol”로 명확히 낮춰야 한다.

2. **Concrete security table**  
   target `lambda`, field size, `delta`, `t`, Freivalds error, proximity error, SNARK error, backend error, binding error, Fiat-Shamir loss를 한 표로 정리해야 한다. Main benchmark도 strict parameter와 scaling parameter를 구분해야 한다.

3. **Full evaluation metrics**  
   peak RSS, repeated-run variance, setup/key size, proof breakdown, standalone backend cost, end-to-end cost를 추가해야 한다.

4. **Baseline expansion**  
   Freivalds만으로는 충분하지 않을 수 있다. 최소한 관련 matrix-checking SNARK/VC approaches와의 qualitative comparison, 가능하면 quantitative comparison을 추가해야 한다.

5. **S&P formatting pass**  
   ACM CCS metadata와 placeholder DOI/ISBN을 제거하고 IEEE S&P format/page limit/anonymity에 맞춰야 한다.

## Final Assessment

이 수정본은 이전보다 훨씬 좋은 논문이다. 특히 QA-NIZK implementation, proof-size reduction, GPT-2 case study, explicit limitation disclosure는 실질적인 진전이다.

그럼에도 현재 상태에서 S&P accept를 기대하기는 어렵다. 이유는 단순하다. 논문의 가장 중요한 성능 claim이 아직 independently implemented and measured code-commitment backend 없이 conditional model 위에 서 있다. S&P 수준으로 올리려면 이 conditional gap을 실제 backend와 end-to-end evaluation으로 닫거나, 논문의 positioning을 명확히 theoretical/modular result로 바꾸어 claim을 줄여야 한다.

현재 판정은 **Weak Reject / Borderline Reject**이다. 강한 revision 이후에는 borderline accept까지 갈 가능성이 있다.
