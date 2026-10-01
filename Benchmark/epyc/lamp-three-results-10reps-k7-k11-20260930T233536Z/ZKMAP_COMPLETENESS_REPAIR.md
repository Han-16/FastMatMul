# Completeness 수정판: completeness-roots-v1

- 날짜: 2026-10-01
- 사용자 요청: 원문의 completeness 실패 부분을 수정하여 구현한다. soundness/zero knowledge 보완은 이번 범위가 아니며, 서버·성능 실험 없이 작은 입력의 로컬 테스트만 수행한다.
- 원본 경로: `-variant paper` (기본값). 기존 Prove/VerifyAppendixE/진단 배치 계산을 보존했다.
- 수정 경로: `-variant completeness-roots-v1`. 구현은 `crypto/zkmap/completeness.go`, 직렬화는 `crypto/zkmap/completeness_wire.go`, CLI 연결은 `cmd/zkmap/completeness.go`.
- 수정판을 원문 zkMaP나 원저자 구현의 성능으로 표시하지 않는다.

## 1. 현재 원문 completeness 문제의 정확한 범위

정상 행렬곱 C=AB에 대해서 projection은 다음을 보장한다.

\[
\mu=y_L^TCy_R=\sum_{i=0}^{n-1}a_i b_i,
\quad a=y_L^TA,\ b=By_R.
\]

Appendix E 17행의 witness가 다항식이 되려면 별도의 조건

\[
\mu=P_a(y)P_b(y)
\]

가 필요하다. 일반 interpolation/coefficient encoding에서 내적은 한 점에서의 평가값 곱과 같지 않다. 원문의 보간 노드가 미정의이므로 모든 가능한 저자 의도를 반박한 것으로 주장하지 않으며, 현재의 명시된 해석과 그 식의 completeness 실패를 기록한다.

간단한 대수적 예: n=2, A=B=C=I, y=2. 이 경우 a=(1,4), b=(1,2), mu=9다. 단위근 (1,−1) 보간에서는

\[
P_a(X)=(5-3X)/2,\qquad P_b(X)=(3-X)/2.
\]

따라서 P_a(2)P_b(2)=−1/4이며 원문 witness의 나머지는 37/4≠0이다. 여기서 y=2는 수식의 대수적 예시이지 특정 Fiat–Shamir hash 출력에 대한 주장이나 공격이 아니다. 실제 hash-derived challenge를 사용하는 기존 정상 입력 실패 테스트도 보존했다.

## 2. 선택한 수정과 completeness 도출

단위근 보간은 유지한다. H={1,omega,...,omega^(n−1)}이고 omega의 차수는 n이다. P_a(omega^i)=a_i, P_b(omega^i)=b_i, 두 다항식의 차수는 n−1 이하이다. h=P_aP_b의 계수를 h_j라 쓰면 단위근 합으로부터

\[
\sum_{i=0}^{n-1}h(\omega^i)=n(h_0+h_n)=\sum_i a_i b_i=\mu
\]

가 성립한다. 차수 2n−2 이하이므로 합에서 남는 항은 차수 0과 n뿐이다. 따라서 n h(X)−mu를 X^n−1로 나눈 remainder R의 상수항은 0이며,

\[
\boxed{nP_a(X)P_b(X)-\mu=Q(X)(X^n-1)+XT(X)}
\]

로 표현할 수 있다. deg Q,deg T≤n−2이다. 이 항등식은 n이 field characteristic의 배수가 아닐 때 모든 정상 projection에 대해 성립한다. BN254의 사용한 power-of-two n=2,...,8192는 이 조건을 만족한다.

이것은 one-point product를 내적이라고 간주하지 않고 내적을 정확하게 나타내는 수정안이다. 최소한의 유일한 수정안이라고 주장하지 않는다. 상수 remainder가 0인지 확인하며, 나머지를 버리거나 mu를 평가값 곱으로 덮어쓰지 않는다.

## 3. 실제 curve 검증

기존 ABC row-major commitment와 structured projection은 유지한다. 다음 public G2 powers를 setup에 추가한다.

\[
\{G_2,sG_2,\ldots,s^nG_2\}.
\]

G1 matrix SRS는 기존 n²개를 사용한다. 추가 G2 powers는 같은 setup scalar로 생성하며 prover/verifier에는 scalar를 전달하거나 보관하지 않는다. 새로운 public SRS와 variant를 challenge에 묶는다.

수정 proof는 다음 다섯 점이다.

\[
V_a=P_a(s)G_1,\quad V_b=P_b(s)G_2,\quad V_\mu=\mu G_1,
\quad V_Q=Q(s)G_1,\quad V_T=T(s)G_1.
\]

verifier는

\[
e(nV_a,V_b)=e(V_\mu,G_2)\,e(V_Q,s^nG_2-G_2)\,e(V_T,sG_2)
\]

를 검사한다. 위 다항식 항등식을 X=s에서 평가하고 pairing의 bilinearity를 적용하면 정상 proof가 항상 이 식을 만족한다. 이는 일반 정상 입력에 대한 대수적 completeness 근거이며 security proof가 아니다.

## 4. 이에 맞는 배치 식

원래 weighted challenge z=Σrho^(i−1)y_i로 서로 다른 divisors를 하나로 만드는 방식은 유지하지 않는다. 새 항등식의 고정 G2 인자를 가진 RHS 점만 각각 가중합하고, LHS의 product pairing은 claim마다 보존한다.

\[
\prod_i e(n\rho^{i-1}V_{a,i},V_{b,i})=
e(\sum_i\rho^{i-1}V_{\mu,i},G_2)
e(\sum_i\rho^{i-1}V_{Q,i},s^nG_2-G_2)
e(\sum_i\rho^{i-1}V_{T,i},sG_2).
\]

각 단일 식에 같은 weight를 적용해 곱한 것이므로 정상 배치에서도 completeness가 성립한다. rho=0도 포함한다. 원문의 constant-size batch 성능을 유지한다고 주장하지 않는다.

## 5. 바뀌는 비용과 남겨둔 경계

| 항목 | 수정판 |
| --- | --- |
| G1 SRS | 기존 n²점 |
| G2 SRS | 기존 2점에서 n+1점 |
| single pairing terms | 4개 |
| single payload | ZKC1 marker 4B + G1 4점 128B + G2 1점 64B = 196B |
| public ABC statement | 96B (SRS와 dimensions 제외) |
| batch pairing terms | q+3개 |
| batch payload | ZKB1 marker/count 8B + q개 product pairs 96q B + RHS 3개 점 96B = 104+96q B |
| batch rho context | 32B 별도 |

projection polynomial을 원래 ABC commitment에 연결하는 proof, polynomial degree 제약을 보장하는 proof, hiding은 추가하지 않았다. 새 verifier는 inner-product polynomial identity를 검사하며, 제공된 ABC 점은 형식 검사만 한다. 따라서 정상 입력 수락이 matrix relation의 soundness 또는 zero knowledge를 뜻하지 않는다. 이는 이전의 누락된 연결 검사를 완성하는 작업과 분리된 completeness 수정이다.

압축/GPT-2/rectangular 확장도 이번 작업에서 추가하지 않았다. 이 수정의 SRS·proof·pairing 비용이 원문과 다르므로 향후 비교에는 별도 variant 이름과 측정 정의를 사용해야 한다.

## 6. 작은 로컬 테스트 실행

```sh
cd /path/to/LAMP
go test ./...
go build -o bin/zkmap ./cmd/zkmap
./bin/zkmap -variant completeness-roots-v1 -K 2 -threads 2 -output complete-small.jsonl
./bin/zkmap -variant completeness-roots-v1 -K 2 -threads 2 -batch 3 -output complete-batch-small.jsonl
```

인코딩 override나 원본 verifier/batch-product override는 이 경로에서 허용하지 않는다. 기본값은 여전히 paper다. 서버용 runner는 보완 버전을 명시적으로 선택하며, CLI 기본값은 원문 진단 경로 paper다.

결과 기록은 `docs/comparison/zkmap_tests_20261001/`에 둔다. 일반 정상 입력 n=2,4,8 및 여러 seed, q=1,2,3, polynomial identity, 실제 pairing, canonical encode/decode 재검증을 테스트한다. 서버·성능 실험은 실행하지 않는다.

## 7. 비교 브랜치 통합

기준 브랜치는 `comparison/zkmatrix-benchmarks`, 기준 커밋은 `317b4cba9b1d0da17697a9435ad3539380f6a58c`다. 새 브랜치 `comparison/zkmap-completeness`에 기존 모듈 의존성을 그대로 사용해 `crypto/zkmap`, `cmd/zkmap`을 추가했다. 기존 LAMP·zkMatrix·zkMaP 진단 구현과 측정 결과는 수정하지 않았다.

`python3 scripts/comparison/run_zkmap.py --profile both --plan`은 보완 버전을 선택한 17개 서버 명령만 출력한다. 실행하려면 바이너리를 빌드하고 `--execute --output /new/results/path`를 명시해야 한다. 실패·누락된 원시 records, 불일치한 variant 또는 직렬화 재검증 실패를 성공 실행으로 취급하지 않는다. 기존 `run.py`는 LAMP·zkMatrix용으로 유지하며, 이 variant를 그 기존 결과 집계에 자동으로 섞지 않는다.

`verification_succeeded=true`는 이 변형의 pairing 식 수락만 뜻한다. 모든 CLI records에는 `security_certified=false`, `comparison_eligible_as_published_zkmap=false`가 들어간다. 비교 표에서는 variant를 별도 표기한다.
