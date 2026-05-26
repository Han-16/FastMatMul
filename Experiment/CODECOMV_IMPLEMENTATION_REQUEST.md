# FastMatMul CodeComV 구현 및 실험 요청서

## 목적

현재 FastMatMul 논문의 가장 큰 gap은 standalone `CodeComV` backend가 구체적으로 구현 및 측정되지 않았다는 점입니다.

논문 본문은 `FastMatMul`을 matrix-multiplication checking layer로 정리하고 있으며, soundness theorem은 다음 전제를 필요로 합니다.

```text
CodeComV(cm_v, v, sigma_v) = 1
```

이 검증이 accept하면 commitment root `cm_v`의 모든 accepting opening이 같은 벡터 `v`의 encoding `Enc(v)`에 전역적으로 묶여 있어야 합니다.

즉, sampled positions에서만 맞는 값이 아니라 full codeword에 대한 global codeword binding이 필요합니다.

S&P 제출 가능성을 높이려면 `CodeComV`를 포함한 end-to-end 비용과 strict-security parameter 실험이 필요합니다.

## 1. Concrete CodeComV Backend 결정

먼저 primary backend 하나를 정해주세요.

반드시 문서화할 항목:

```text
backend_name:
code_family:
rate_rho:
codeword_length_n:
relative_distance_delta:
commitment_scheme:
opening_scheme:
sigma_v_contents:
CodeComV_location: in_snark / auxiliary_verifier / hybrid
security_assumption:
```

가능한 backend 후보:

```text
Dense encoder check
Expander-code / Brakedown-style committed-codeword backend
Reed-Solomon + polynomial commitment backend
KZG / CPLink-style commitment-to-codeword linking backend
```

중요한 점:

```text
CodeComV가 없으면 FastMatMul의 proximity soundness가 성립하지 않습니다.
따라서 CodeComV를 제거하는 방향은 불가능하고, 반드시 어떤 형태로든 구현 또는 명시적 backend로 닫아야 합니다.
```

## 2. CodeComV 단독 벤치마크

`CodeComV`만 분리해서 비용을 측정해주세요.

최소 matrix range:

```text
k = 2^7, 2^8, 2^9, 2^10, 2^11, 2^12
```

가능하면:

```text
k = 2^13
```

필수 측정 항목:

```text
constraints
prove_time_s
verify_time_s
sigma_size_bytes
proof_size_bytes
setup_time_s
pk_size_bytes
vk_size_bytes
peak_rss_bytes
status
```

권장 CSV 파일명:

```text
codecom_backend_results.csv
```

CSV schema:

```csv
backend,k,log_k,n,rate,delta,t,security_mode,component,constraints,prove_time_s,verify_time_s,proof_size_bytes,sigma_size_bytes,setup_time_s,pk_size_bytes,vk_size_bytes,peak_rss_bytes,run_id,seed,status,notes
```

예시:

```csv
BrakedownStyle,1024,10,2048,0.5,0.5,130,strict_proximity,codecom,123456,1.23,0.04,98765,4321,0.50,1000000,20000,3000000000,1,42,success,
```

## 3. FastMatMul + CodeComV End-to-End 벤치마크

현재 논문 숫자는 fold/opening/linking layer 중심입니다.

S&P 리뷰어를 설득하려면 `CodeComV` 포함 total number가 필요합니다.

필수 측정 항목:

```text
total_constraints
total_prove_time_s
total_verify_time_s
total_proof_size_bytes
setup_time_s
pk_size_bytes
vk_size_bytes
peak_rss_bytes
status
```

권장 CSV 파일명:

```text
fmm_end_to_end_results.csv
```

CSV schema:

```csv
variant,k,log_k,n,rate,delta,t,security_mode,includes_codecom,constraints,prove_time_s,verify_time_s,proof_size_bytes,setup_time_s,pk_size_bytes,vk_size_bytes,peak_rss_bytes,run_id,seed,status,notes
```

예시:

```csv
FastMatMul-CodeCom,1024,10,2048,0.5,0.5,130,strict_proximity,true,900000,21.3,0.41,14000000,3.1,5000000,50000,4200000000,1,42,success,
```

## 4. Strict Security Parameter 실험

현재 main table은 `t=128`을 사용합니다.

하지만 `delta = 1/2`이고 proximity error가 `4(1-delta)^t`라면:

```text
t = 128  ->  2^-126 proximity term
t = 130  ->  2^-128 proximity term
t = 133  ->  conservative per-term 2^-131 budget
```

따라서 최소한 다음 query counts를 비교해주세요.

```text
t = 128
t = 130
t = 133
```

최소 측정 범위:

```text
k = 2^10, 2^11, 2^12
```

가능하면 전체 range에서 측정:

```text
k = 2^7 ... 2^13
```

## 5. Component Breakdown

총 constraints만 있으면 병목을 알 수 없습니다.

아래 component별로 분리 측정해주세요.

```text
fold
equality
opening
linking
codecom
snark_overhead
total
```

각 component별 측정 항목:

```text
constraints
prove_time_s
verify_time_s
proof_size_bytes
peak_rss_bytes
```

권장 CSV 파일명:

```text
component_breakdown.csv
```

CSV schema:

```csv
variant,k,log_k,n,rate,delta,t,security_mode,component,constraints,prove_time_s,verify_time_s,proof_size_bytes,peak_rss_bytes,run_id,seed,status,notes
```

## 6. Proof Size Breakdown

proof size를 아래 항목으로 분해해주세요.

```text
snark_proof
commitment_roots
sampled_encoded_columns
merkle_paths
kzg_or_cplink_openings
sigma_v
other_auxiliary
total
```

권장 CSV 파일명:

```text
proof_size_breakdown.csv
```

CSV schema:

```csv
variant,k,log_k,t,component,size_bytes,run_id,status,notes
```

## 7. 반복 실행 및 메모리

각 핵심 실험은 최소 3회 반복해주세요.

```text
run_id = 1, 2, 3
```

기록할 항목:

```text
mean
stddev
peak_rss_bytes
status: success / OOM / timeout / error
```

OOM 또는 timeout이 발생한 경우:

```text
failure_stage:
last_logged_metric:
peak_rss_before_failure:
timeout_limit_s:
```

## 8. Setup 및 Key Size

S&P 리뷰어는 setup/key size를 물을 가능성이 큽니다.

측정 항목:

```text
setup_time_s
setup_peak_rss_bytes
pk_size_bytes
vk_size_bytes
srs_size_bytes
param_file_size_bytes
```

권장 CSV 파일명:

```text
setup_key_results.csv
```

CSV schema:

```csv
variant,k,log_k,n,rate,delta,t,setup_time_s,setup_peak_rss_bytes,pk_size_bytes,vk_size_bytes,srs_size_bytes,param_file_size_bytes,run_id,status,notes
```

## 9. 재현 정보

아래 정보를 별도 파일로 남겨주세요.

권장 파일명:

```text
system_info.json
reproduction_commands.md
```

필수 항목:

```text
cpu:
num_cores:
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
hash_function:
backend_libraries:
random_seed:
matrix_distribution:
memory_measurement_method:
```

`reproduction_commands.md`에는 각 CSV를 생성한 정확한 command를 적어주세요.

예시:

```bash
cargo run --release --bin bench_codecom -- --backend brakedown-style --k 1024 --t 130 --seed 42 --measure-memory
cargo run --release --bin bench_fastmatmul -- --variant codecom --k 1024 --t 130 --seed 42 --measure-memory
```

## 10. 성공 기준

S&P 제출 관점에서 최소 성공 기준은 다음입니다.

```text
1. concrete CodeComV backend가 하나 정해져 있다.
2. 해당 backend의 relative distance delta가 문서화되어 있다.
3. CodeComV 단독 constraints/time/size가 측정되어 있다.
4. FastMatMul + CodeComV end-to-end total number가 있다.
5. t=130 strict proximity number가 있다.
6. 가능하면 t=133 conservative budget number가 있다.
7. peak RSS와 최소 3회 반복 평균/표준편차가 있다.
8. setup/key size가 있다.
9. 재현 command와 system info가 있다.
```

## 11. 우선순위

시간이 부족하면 아래 순서대로 진행해주세요.

```text
P0. primary CodeComV backend 결정
P1. CodeComV 단독 벤치마크
P2. FastMatMul + CodeComV end-to-end 벤치마크
P3. t=130 / t=133 strict-security 실험
P4. component breakdown
P5. proof-size breakdown
P6. repeated runs, peak RSS, setup/key sizes
P7. stronger external baseline comparison
```

## 12. 논문 반영 방식

실험 결과가 나오면 논문에는 다음 식으로 반영할 예정입니다.

```text
Current claim:
FastMatMul achieves O(tk) checking-layer constraints under a conditional linear-time CodeComV backend model.

Target claim after experiments:
FastMatMul instantiated with [backend_name] achieves [measured total constraints/time/proof size], including CodeComV and input-certification costs where applicable.
```

핵심은 conditional backend claim을 end-to-end measured claim으로 바꾸는 것입니다.

