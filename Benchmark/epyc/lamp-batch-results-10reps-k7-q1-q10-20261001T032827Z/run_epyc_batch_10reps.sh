#!/usr/bin/env bash
# Batch-only EPYC comparison. Default: inspect the plan without running Go.
set -Eeuo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
checkout="$HOME/FastMatMul-comparison"
mode=plan
result_dir=""
archive=""
while (( $# )); do
  case "$1" in
    --plan) mode=plan; shift ;;
    --run) mode=run; shift ;;
    --status) mode=status; shift ;;
    --checkout) checkout="${2:?--checkout needs a path}"; shift 2 ;;
    *) printf '지원하지 않는 옵션: %s\n' "$1" >&2; exit 2 ;;
  esac
done
checkout="$(cd "$checkout" && pwd)"

if [[ "$mode" == status ]]; then
  python3 "$script_dir/epyc_batch_tools.py" status --checkout "$checkout"
  exit 0
fi

cd "$checkout"
[[ "$(git rev-parse HEAD)" == b34d2287c30730a3990d92630185a0a792a2897f ]] || {
  printf '측정할 코드 버전이 FastMatMul b34d228과 다릅니다.\n' >&2; exit 1;
}
changed_files="$(git diff --name-only HEAD)"
if [[ -n "$changed_files" && "$changed_files" != scripts/comparison/configs.json ]]; then
  printf '설정 외의 소스 변경이 있습니다:\n%s\n' "$changed_files" >&2; exit 1
fi
python3 - "$checkout" <<'PY'
import subprocess, sys
from pathlib import Path
root = Path(sys.argv[1])
files = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=root, text=True).splitlines()
unexpected = [p for p in files if Path(p).suffix == '.go' or Path(p).name in {'go.mod', 'go.sum', 'go.work', 'go.work.sum'} or p.startswith('scripts/comparison/')]
if unexpected:
    raise SystemExit('추적되지 않은 구현/runner 파일을 먼저 확인하세요: ' + ', '.join(unexpected))
PY
for required in prepare_comparison_3reps.py comparison_batch_10reps.json epyc_batch_tools.py; do
  [[ -f "$script_dir/$required" ]] || { printf '준비 파일 누락: %s\n' "$required" >&2; exit 1; }
done
python3 "$script_dir/prepare_comparison_3reps.py" "$checkout" \
  --profiles "$script_dir/comparison_batch_10reps.json" > /dev/null
python3 "$script_dir/epyc_batch_tools.py" plan --checkout "$checkout"
if [[ "$mode" == plan ]]; then
  printf '계획 확인 완료. 실험은 시작하지 않았습니다.\n'
  exit 0
fi

export PATH="$HOME/.local/lamp-go-1.26.2/bin:$PATH"
export GOMAXPROCS=32
[[ "$(go version)" == 'go version go1.26.2 linux/amd64' ]] || {
  printf 'Go 버전이 기존 서버 측정 환경과 다릅니다.\n' >&2; exit 1;
}
python3 - <<'PY'
import os, platform
from pathlib import Path
if platform.system() != 'Linux' or (os.cpu_count() or 0) < 32:
    raise SystemExit('기존 EPYC 서버의 Linux/32 vCPU 환경에서 실행하세요.')
cpu = Path('/proc/cpuinfo').read_text()
if 'EPYC 7B13' not in cpu:
    raise SystemExit('CPU가 기존 측정 서버의 AMD EPYC 7B13과 다릅니다.')
memory = next(int(line.split()[1]) * 1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith('MemTotal:'))
if memory < 240 * (1 << 30):
    raise SystemExit('기존 측정 서버의 메모리 환경과 다릅니다.')
PY
# The kernel releases this lock even when the SSH session or VM ends.
exec 9> "$checkout/.lamp-epyc-batch.lock"
flock -n 9 || { printf '다른 배치 전용 실행이 진행 중입니다.\n' >&2; exit 1; }

stamp="$(date -u +%Y%m%dT%H%M%SZ)"
result_dir="$checkout/benchmark/comparison/vm_batch_10reps_k7_q1_q10_$stamp"
archive="$HOME/lamp-batch-results-10reps-k7-q1-q10-$stamp.tar.gz"
mkdir -p "$checkout/benchmark/comparison"
mkdir "$result_dir"
set_state() {
  python3 - "$result_dir" "$1" <<'PY'
import json, sys, time
from pathlib import Path
p = Path(sys.argv[1]) / 'run-state.json'
t = p.with_suffix('.tmp')
t.write_text(json.dumps({'state': sys.argv[2], 'updated_unix': time.time()}) + '\n')
t.replace(p)
PY
}
cleanup() {
  code=$?
  trap - EXIT
  if [[ "$code" != 0 && -d "$result_dir" ]]; then
    set_state failed || true
    printf '실험이 중단됐습니다. 로그를 확인하세요: %s\n' "$result_dir" >&2
    if tar --exclude='*/bin' -czf "$archive" -C "$result_dir" .; then
      printf '중단 시점 자료를 보존한 파일: %s\n' "$archive" >&2
    fi
  fi
  exit "$code"
}
trap cleanup EXIT

cp scripts/comparison/configs.json "$result_dir/configs.json"
cp "$script_dir/"{run_epyc_batch_10reps.sh,epyc_batch_tools.py,comparison_batch_10reps.json,prepare_comparison_3reps.py} "$result_dir/"
cp SOURCE_PROVENANCE.json "$result_dir/"
git rev-parse HEAD > "$result_dir/source_commit.txt"
python3 - "$result_dir" <<'PY'
import json, sys
from pathlib import Path
Path(sys.argv[1], 'comparison-scope.json').write_text(json.dumps({
    'repository': 'https://github.com/lysias9049/FastMatMul',
    'source_commit': 'b34d2287c30730a3990d92630185a0a792a2897f',
    'workload': 'batch', 'matrix_size': 128, 'batch_sizes': list(range(1, 11)),
    'repetitions': 10, 'threads': 32, 'rho': '1/2', 'queries': 309,
    'scheme_labels': ['LAMP', 'independent zkMatrix'], 'expected_records': 200,
    'timing_scope': 'commit-inclusive online prove; setup, compile and actual AB computation separate'
}, indent=2) + '\n')
PY

printf '결과 폴더: %s\n기본 검증 시작\n' "$result_dir"
set_state validation
python3 -m unittest discover -s scripts/comparison -p 'test_run.py' > "$result_dir/runner-tests.log" 2>&1 || {
  cat "$result_dir/runner-tests.log"; exit 1;
}
go test ./crypto/zkmatrix ./cmd/lamp_batch > "$result_dir/protocol-tests.log" 2>&1 || {
  cat "$result_dir/protocol-tests.log"; exit 1;
}
python3 "$script_dir/epyc_batch_tools.py" plan --checkout "$checkout" --save "$result_dir/batch-plan.json"
printf '기본 검증 통과. LAMP·zkMatrix 배치 1~10, 각 10회 시작\n'
date -u
set_state lamp_zkmatrix_batch
python3 "$script_dir/epyc_batch_tools.py" run --checkout "$checkout" --output "$result_dir/batch"
python3 "$script_dir/epyc_batch_tools.py" check --output "$result_dir/batch"
set_state complete
tar --exclude='*/bin' -czf "$archive" -C "$result_dir" .
date -u
printf '전체 배치 실험 완료. 다운로드할 파일:\n%s\n' "$archive"
sha256sum "$archive"
printf '다운로드 완료를 확인한 뒤 Google Cloud에서 VM을 중지하고 상태를 확인하세요.\n'
