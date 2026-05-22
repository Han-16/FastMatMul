# FastMatMul S&P 실험 요청서

이 문서는 FastMatMul 논문을 S&P 수준으로 끌어올리기 위해 추가로 필요한
실험을 정리한 요청서입니다. 구현 담당자가 논문 전체를 모르더라도 실험 목적과
필요 산출물을 이해할 수 있도록 배경부터 적습니다.

## 1. 현재 논문의 상태

현재 FastMatMul 논문은 `A B = C` 형태의 committed matrix multiplication을
SNARK 안에서 직접 계산하지 않고, 더 작은 checking layer로 검증하는 방식을
제안합니다.

핵심 아이디어는 다음과 같습니다.

1. 입력 행렬 `A`, `B`, `C`는 이미 인코딩되어 commitment가 잡혀 있다고
   가정합니다.
2. verifier가 Freivalds challenge `r`를 뽑습니다.
3. prover는 native/off-circuit으로
   `x = rA`, `y = xB`, `z = rC`를 계산합니다.
4. prover는 `x`, `y`, `z`도 codeword로 인코딩하고 commitment를 만듭니다.
5. verifier는 random encoded positions `I`를 뽑고, 그 위치들에서만 fold
   relation과 equality relation을 확인합니다.

이 방식은 SNARK constraint를 대략 `O(tk)`로 줄입니다. 여기서 `k`는 행렬
크기이고, `t`는 sampled position 개수입니다.

하지만 이 주장이 sound하려면 중요한 조건이 하나 필요합니다. prover가
`x`, `y`, `z` commitment를 만들 때, 그 commitment가 정말로 `Enc(x)`,
`Enc(y)`, `Enc(z)` 전체 codeword에 묶여 있어야 합니다. sampled position에서만
그럴듯한 값을 내면 안 됩니다. 이 역할을 하는 추상 backend가 논문에서
`CodeCom`입니다.

현재 리뷰의 가장 큰 지적은:

> FastMatMul checking layer는 좋아 보이지만, `CodeCom` backend가 실제로
> 구현/측정되지 않았으므로 end-to-end verifiable matrix multiplication system
> 이라고 보기 어렵다.

따라서 이번 실험의 최우선 목표는 `CodeCom`을 하나 concrete하게 정하고, 그
비용을 독립적으로 그리고 end-to-end로 측정하는 것입니다.

## 2. CodeCom이 무엇인가?

`CodeCom`은 "commitment root `cm_v`가 어떤 vector `v`의 정직한 encoding
`Enc(v)` 전체에 묶여 있다"는 사실을 증명/검증하는 backend입니다.

논문에서 필요한 interface는 다음과 같습니다.

```text
sigma_v <- CodeCom.Prove(cm_v, v, Enc(v))
accept  <- CodeCom.Verify(cm_v, v, sigma_v)
```

여기서:

- `v`: 길이 `k`인 vector입니다. 예: `x`, `y`, `z`.
- `Enc(v)`: linear error-correcting code로 인코딩한 길이 `n` codeword입니다.
- `cm_v`: `Enc(v)`에 대한 commitment root입니다.
- `sigma_v`: `cm_v`가 정말 `Enc(v)`에 연결되어 있음을 보이는 proof 또는 witness
  material입니다.
- `CodeCom.Verify`: 위 연결 관계를 검증하는 verifier relation입니다. 이것이
  SNARK circuit 안에 들어가거나, 또는 auxiliary proof로 검증될 수 있습니다.

### 2.1 왜 CodeCom이 필요한가?

FastMatMul은 `I = (j_1, ..., j_t)` 위치에서만 fold check를 합니다. 만약
`cm_x`, `cm_y`, `cm_z`가 full codeword에 묶여 있지 않다면, 악의적인 prover는
`I`를 본 다음 sampled positions에서만 맞는 값을 만들어 낼 수 있습니다. 그러면
code distance를 이용한 soundness proof가 깨집니다.

따라서 필요한 보장은 sampled positions만 맞는 것이 아니라:

> `CodeCom.Verify(cm_v, v, sigma_v)`가 accept하면, `cm_v`의 모든 accepting
> opening은 `Enc(v)`의 해당 coordinate와 일치해야 한다.

논문에서는 이를 **global codeword-binding**이라고 부릅니다.

### 2.2 CodeCom backend 후보

이번 실험에서는 최소 하나의 concrete backend를 primary instantiation으로
정해야 합니다.

가능한 방향은 세 가지입니다.

1. **In-circuit encoder check**
   - SNARK circuit 안에서 `Enc(v)`를 직접 계산하고, commitment root와 연결합니다.
   - 장점: 가장 명확하고 구현/검증이 쉽습니다.
   - 단점: dense generator code를 쓰면 `O(k^2)`가 되어 FastMatMul의 `O(k)` 장점이
     줄어듭니다. expander-style linear-time encoder를 쓰면 더 좋습니다.

2. **Brakedown/Orion-style committed-codeword backend**
   - code-based proof system의 encoded oracle/commitment 방식을 backend로 씁니다.
   - 장점: 논문 컨셉과 가장 잘 맞고, linear-time backend claim을 뒷받침할 수
     있습니다.
   - 단점: 알고리즘, proof contents, verifier cost를 정확히 명시하고 구현해야
     합니다.

3. **Commitment-to-codeword linking proof**
   - `cm_v`가 `Enc(v)`에 연결되어 있음을 별도 linking proof로 보입니다.
   - 장점: 현재 CPLink/KZG 계열 구현과 연결될 수 있습니다.
   - 단점: proof size와 verifier cost가 커질 수 있습니다.

S&P 제출을 목표로 하면 2번 또는 3번 중 하나를 제대로 구현/측정하는 것이 가장
좋습니다. 시간이 부족하면 1번을 "concrete but possibly expensive backend"로
구현해서 end-to-end soundness와 비용을 먼저 보여주는 것도 의미가 있습니다.

## 3. 가장 중요한 실험: CodeComV 비용 측정

### 목표

`CodeCom.Verify`가 실제로 얼마의 비용을 갖는지 독립적으로 측정합니다. 이 결과가
없으면 논문은 계속 "conditional checking-layer result"에 머뭅니다.

### 측정 대상

각 `k`에 대해 다음을 측정하십시오.

- `CodeComV` constraint count
- `CodeComV` proving time
- `CodeComV` verification time
- `sigma_v` size
- `CodeCom` setup time, 필요한 경우
- `CodeCom` proving key size, 필요한 경우
- `CodeCom` verifying key size, 필요한 경우
- peak RSS memory

### 권장 k 범위

기본:

```text
k in {2^7, 2^8, 2^9, 2^10, 2^11, 2^12}
```

가능하면:

```text
k = 2^13
```

### 중요한 기록 사항

`CodeCom`이 어떤 형태인지 반드시 로그에 남겨야 합니다.

- `sigma_v`가 SNARK witness 안에 들어가는가?
- `sigma_v`가 auxiliary proof data로 따로 붙는가?
- `CodeComV`가 SNARK circuit 안에서 검증되는가?
- 아니면 SNARK 밖에서 별도 verifier가 검증하는가?
- commitment root는 Merkle인가, KZG인가, CPLink인가, 다른 것인가?
- opening verifier는 무엇인가?
- 어떤 code를 쓰는가?
- 그 code의 proven relative distance `delta`는 얼마인가?

## 4. End-to-end FastMatMul + CodeCom 실험

### 목표

현재 논문은 multiplication-checking layer만 측정합니다. S&P 리뷰어가 원하는 것은
`CodeCom`까지 포함한 end-to-end 비용입니다.

### 측정해야 할 variant

가능한 범위에서 다음 variant를 측정하십시오.

- `FastMatMul-Merkle + CodeCom`
- `FastMatMul-KZG + CodeCom`
- `FastMatMul-CPLink + CodeCom`
- `Freivalds` baseline

시간이 부족하면 적어도 primary backend 하나에 대해:

```text
FastMatMul-primary + CodeCom
Freivalds
```

를 측정하십시오.

### 측정 항목

각 `k`, 각 `t`, 각 run에 대해:

- total constraints
- total proving time
- total verification time
- total proof size
- setup time
- proving key size
- verifying key size
- peak RSS memory
- status: success / OOM / timeout / error

## 5. Strict security parameter 실험

현재 논문 표의 main experiment는 `t=128`입니다. 하지만 `delta=1/2`라고 해도
4-way union bound 때문에 strict 128-bit proximity soundness에는 `t=130`이
필요합니다.

공식은 다음입니다.

```text
t = ceil((lambda + 2) / log2(1 / (1 - delta)))
```

예를 들어 `delta = 1/2`, `lambda = 128`이면:

```text
t = 130
```

논문에서는 aggregate 128-bit budget도 언급합니다. 대략 각 error term을
`2^-131` 이하로 잡는 예시를 쓰면:

```text
t = ceil(133 / log2(1 / (1 - delta)))
```

`delta = 1/2`이면:

```text
t = 133
```

### 반드시 측정할 t

최소:

```text
t = 128
t = 130
```

가능하면:

```text
t = 128
t = 130
t = 133
```

### 왜 필요한가?

리뷰어는 "논문이 security parameter를 정직하게 설명하는 것은 좋지만, main table은
strict security number로도 보여줘야 한다"고 지적했습니다. `t=128`에서 `t=130`은
대부분의 checking-layer 비용이 약 `1.6%` 증가하는 정도라서, 실험 부담은 크지 않을
가능성이 높습니다.

## 6. Component breakdown 실험

### 목표

total constraints만 있으면 리뷰어가 어느 부분이 비용을 지배하는지 알 수 없습니다.
아래 component별로 constraint/time/size를 나눠서 기록해야 합니다.

### 필요한 component

가능하면 다음 항목을 분리하십시오.

- `fold`
  - `enc_x[j] = Fold(enc_A[j], r)`
  - `enc_y[j] = Fold(enc_B[j], x)`
  - `enc_z[j] = Fold(enc_C[j], r)`
- `equality`
  - `enc_y[j] = enc_z[j]`
- `opening`
  - Merkle path verification
  - KZG opening verification
  - other opening verification
- `codecom`
  - `CodeCom.Verify(cm_v, v, sigma_v)`
- `linking`
  - CPLink or KZG linking material, if applicable
- `snark_overhead`
  - public input handling
  - miscellaneous circuit overhead
- `total`

### 최소 범위

전체 `k` 범위가 어렵다면 최소 아래 세 지점만이라도 component breakdown을
남기십시오.

```text
k = 2^10
k = 2^11
k = 2^12
```

## 7. Memory와 반복 실행

Freivalds가 `k=4096`에서 OOM이 난다는 주장은 peak memory 로그가 있어야
방어할 수 있습니다.

### 반복 횟수

각 실험을 최소 3회 반복하십시오.

```text
run_id = 1, 2, 3
```

가능하면 5회가 더 좋습니다.

### 기록할 항목

- wall-clock proving time
- wall-clock verification time
- setup time
- peak RSS memory
- exit status
- OOM이면 OOM 발생 시점과 직전 peak RSS
- timeout이면 timeout limit

macOS/Linux에서 peak RSS를 기록하는 방식은 환경에 따라 다릅니다. 구현 환경에
맞는 방식을 정하고, 문서에 적어주십시오. 예를 들면:

- `/usr/bin/time -l` on macOS
- `/usr/bin/time -v` on Linux
- process-level memory sampler
- Rust 내부 allocator/memory profiler

## 8. Setup/key size 실험

리뷰어가 setup/key size를 직접 물었습니다. 각 backend별로 다음을 측정하십시오.

- setup time
- proving key size
- verifying key size
- SRS size, KZG류이면
- generated parameter file size
- setup memory peak

가능하면 setup도 `k`별로 측정하십시오.

## 9. Proof size breakdown

현재 proof size가 최대 24-48 MB 수준이라 deployment concern이 있습니다. total size만
있으면 어느 부분이 큰지 알 수 없습니다.

각 proof를 아래 항목으로 나눠 기록하십시오.

- SNARK proof
- commitment roots
- sampled encoded columns
- Merkle authentication paths
- KZG openings
- CPLink proof/linking material
- `sigma_v`
- other auxiliary proof data
- total

## 10. 시스템 정보와 재현성 정보

실험 결과와 함께 반드시 아래 정보를 남겨주십시오.

- CPU model
- number of cores/threads used
- GPU 사용 여부
- RAM size
- OS and version
- Rust version
- cargo profile: debug/release
- compiler flags
- feature flags
- curve/backend library name and version
- hash function
- field modulus or curve field
- random seed
- matrix distribution
- git commit hash
- exact command used to run each experiment

## 11. 추천 CSV 파일 구조

아래 CSV를 생성해주면 논문 표로 옮기기 쉽습니다.

### 11.1 `codecom_backend_results.csv`

`CodeCom` 단독 비용입니다.

```csv
backend,k,log_k,n,rate,delta,t,security_mode,component,constraints,prove_time_s,verify_time_s,proof_size_bytes,sigma_size_bytes,setup_time_s,pk_size_bytes,vk_size_bytes,peak_rss_bytes,run_id,seed,status,notes
```

예시:

```csv
BrakedownStyle,1024,10,2048,0.5,0.5,130,strict_proximity,codecom,123456,1.23,0.04,98765,4321,0.50,1000000,20000,3000000000,1,42,success,
```

### 11.2 `fmm_end_to_end_results.csv`

FastMatMul 전체 비용입니다. 반드시 `CodeCom` 포함 여부를 표시하십시오.

```csv
variant,k,log_k,n,rate,delta,t,security_mode,includes_codecom,constraints,prove_time_s,verify_time_s,proof_size_bytes,setup_time_s,pk_size_bytes,vk_size_bytes,peak_rss_bytes,run_id,seed,status,notes
```

예시:

```csv
FastMatMul-Merkle,1024,10,2048,0.5,0.5,130,strict_proximity,true,900000,21.3,0.41,14000000,3.1,5000000,50000,4200000000,1,42,success,
```

### 11.3 `component_breakdown.csv`

component별 constraint/time/size입니다.

```csv
variant,k,log_k,n,rate,delta,t,security_mode,component,constraints,prove_time_s,verify_time_s,proof_size_bytes,peak_rss_bytes,run_id,seed,status,notes
```

component 값은 가능한 한 아래 이름을 사용하십시오.

```text
fold
equality
opening
codecom
linking
snark_overhead
total
```

### 11.4 `proof_size_breakdown.csv`

proof size 상세 분석입니다.

```csv
variant,k,log_k,t,component,size_bytes,run_id,status,notes
```

component 값:

```text
snark_proof
commitment_roots
sampled_encoded_columns
merkle_paths
kzg_openings
cplink_linking
sigma_v
other_auxiliary
total
```

### 11.5 `setup_key_results.csv`

setup/key size 측정입니다.

```csv
variant,k,log_k,n,rate,delta,t,setup_time_s,setup_peak_rss_bytes,pk_size_bytes,vk_size_bytes,srs_size_bytes,param_file_size_bytes,run_id,status,notes
```

### 11.6 `system_info.md` 또는 `system_info.json`

실험 환경을 사람이 읽을 수 있게 적어주십시오.

필수 항목:

```text
machine_name:
cpu:
cores:
ram:
gpu:
os:
rustc_version:
cargo_version:
git_commit:
build_profile:
feature_flags:
curve:
field:
hash:
backend_libraries:
memory_measurement_method:
```

### 11.7 `reproduction_commands.md`

각 CSV를 생성한 정확한 명령을 적어주십시오.

예시:

```bash
cargo run --release --bin bench_fastmatmul -- --variant merkle --k 1024 --t 130 --seed 42 --measure-memory
cargo run --release --bin bench_codecom -- --backend brakedown-style --k 1024 --t 130 --seed 42
```

실제 명령 이름은 구현체에 맞게 바꾸면 됩니다.

## 12. 우선순위

시간이 부족하면 아래 순서대로 해주십시오.

### Priority 0: backend 결정

먼저 primary `CodeCom` backend를 하나 정해야 합니다.

결정 후 반드시 아래를 문서화하십시오.

- backend 이름
- 사용하는 code
- rate `rho`
- codeword length `n`
- relative distance `delta`
- commitment/opening scheme
- `sigma_v` 내용
- `CodeCom.Verify`가 SNARK 안인지 밖인지
- security assumption

### Priority 1: CodeComV 단독 측정

가장 중요합니다. 이것이 없으면 S&P 리뷰어가 계속 "conditional result"라고 볼
가능성이 큽니다.

### Priority 2: FastMatMul + CodeCom end-to-end 측정

checking layer만이 아니라 `CodeCom` 포함 total number를 만들어야 합니다.

### Priority 3: `t=130` strict proximity table

`t=128`과 `t=130`을 비교할 수 있게 해주십시오. 가능하면 `t=133`도 추가하십시오.

### Priority 4: component breakdown

비용이 어디서 나오는지 설명하기 위한 표입니다.

### Priority 5: memory, variance, setup/key size

OOM claim과 systems evaluation credibility를 위해 필요합니다.

### Priority 6: stronger baseline

가능하면 아래 중 하나를 추가하십시오.

- generic Brakedown/Orion-style proof of Freivalds relation
- sumcheck/GKR matrix multiplication verification
- zkMatrix or committed-matrix multiplication comparison
- realistic zkML matrix layer

시간이 없으면 구현 comparison 대신, 같은 환경에서 돌릴 수 있는 공개 artifact나
paper-reported normalized comparison이라도 정리해주십시오.

## 13. 성공 기준

최소 성공 기준은 다음입니다.

1. concrete `CodeCom` backend 하나가 정해져 있다.
2. 그 backend의 `delta`가 문서화되어 있다.
3. `CodeComV` 단독 constraint/time/size가 있다.
4. `FastMatMul + CodeCom` end-to-end total number가 있다.
5. `t=130` strict proximity number가 있다.
6. peak RSS와 3회 반복 평균/표준편차가 있다.
7. setup/key size가 있다.
8. 재현 명령과 시스템 정보가 있다.

이 기준을 만족하면 논문은 더 이상 "checking-layer-only conditional result"에
머물지 않고, S&P 리뷰어에게 end-to-end system evidence를 제시할 수 있습니다.

