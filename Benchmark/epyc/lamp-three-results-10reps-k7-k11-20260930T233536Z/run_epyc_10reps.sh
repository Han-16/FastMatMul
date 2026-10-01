#!/usr/bin/env bash
# Manual EPYC run of LAMP, zkMatrix and a separately labelled zkMaP variant.
# Default is plan-only. No VM start/stop or automatic shutdown.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
checkout="$HOME/FastMatMul-comparison"
mode=plan
include_batch=0
result_dir=""

while (( $# )); do
  case "$1" in
    --plan) mode=plan; shift ;;
    --run) mode=run; shift ;;
    --status) mode=status; shift ;;
    --include-batch) include_batch=1; shift ;;
    --checkout) checkout="${2:?--checkout needs a path}"; shift 2 ;;
    *) printf '지원하지 않는 옵션: %s\n' "$1" >&2; exit 2 ;;
  esac
done

checkout="$(cd "$checkout" && pwd)"
if [[ "$mode" == status ]]; then
  python3 - "$checkout" <<'PY'
import json, time, sys
from pathlib import Path
roots = sorted((Path(sys.argv[1]) / 'benchmark/comparison').glob('vm_three_10reps_k7_k11_*'))
if not roots:
    raise SystemExit('이번 10회 실험 폴더가 아직 없습니다.')
print('결과 폴더:', roots[-1])
if (roots[-1] / 'run-state.json').exists():
    print('전체 상태:', json.loads((roots[-1] / 'run-state.json').read_text())['state'])
for stage in ('square', 'batch'):
    path = roots[-1] / stage / 'manifest.json'
    if not path.exists():
        print(stage, ': 시작 전 또는 이번 실행에서 선택하지 않음')
        continue
    m = json.loads(path.read_text())
    commands = m.get('commands', [])
    done = sum(c.get('status') == 'completed' and c.get('verified_record_count', 0) == c.get('expected_verified_record_count', -1) for c in commands)
    print(stage, ':', m.get('run_state'), '| 완료 명령:', done, '/', m.get('expected_command_count'))
    if m.get('active_build'):
        print('컴파일 중:', m['active_build'])
    if m.get('run_state') == 'running_command' and commands:
        c = commands[-1]
        print('실행 중:', Path(c['argv'][0]).name, '| 경과:', round(time.time() - c['started_unix']), '초')
for stage in ('zkmap-square', 'zkmap-batch'):
    path = roots[-1] / stage / 'progress.json'
    if not path.exists():
        print(stage, ': 시작 전 또는 선택하지 않음')
        continue
    m = json.loads(path.read_text())
    done = sum(c['status'] == 'completed' for c in m['commands'])
    print(stage, ':', m['run_state'], '| 완료 설정:', done, '/', m['expected_command_count'])
    if m.get('active_command'):
        c = m['active_command']
        records = roots[-1] / stage / c['name'] / 'attempts.jsonl'
        rows = records.read_text().splitlines() if records.exists() else []
        print('실행 중:', c['name'], '| 현재 기록:', len(rows), '| 경과:', round(time.time() - c['started_unix']), '초')
PY
  ps -u "$USER" -o pid,etime,pcpu,pmem,comm --sort=-pcpu | head -12 || true
  exit 0
fi

cd "$checkout"
expected_head=b34d2287c30730a3990d92630185a0a792a2897f
[[ "$(git rev-parse HEAD)" == "$expected_head" ]] || {
  printf '측정할 코드 버전이 FastMatMul b34d228과 다릅니다. 먼저 버전을 확인하세요.\n' >&2
  exit 1
}
changed_files="$(git diff --name-only HEAD)"
if [[ -n "$changed_files" && "$changed_files" != scripts/comparison/configs.json ]]; then
  printf '설정 외의 소스 변경이 있습니다. 먼저 변경 내용을 확인하세요.\n%s\n' "$changed_files" >&2
  exit 1
fi
for required in run_epyc_zkmap.py zkmap_10reps.json prepare_comparison_3reps.py comparison_10reps.json; do
  [[ -f "$script_dir/$required" ]] || { printf '업로드할 준비 파일이 누락됐습니다: %s\n' "$required" >&2; exit 1; }
done
[[ -f cmd/zkmap/main.go && -f scripts/comparison/run_zkmap.py ]] || {
  printf 'zkMaP 코드 또는 runner가 없습니다. 새 저장소를 확인하세요.\n' >&2; exit 1;
}

python3 "$script_dir/prepare_comparison_3reps.py" "$checkout" \
  --profiles "$script_dir/comparison_10reps.json" > /dev/null

python3 - "$checkout" "$include_batch" <<'PY'
import json, subprocess, sys
from pathlib import Path
root = Path(sys.argv[1])
profiles = [('server_square_k7_k11_10reps', set(range(7, 12)), 55, 100)]
if sys.argv[2] == '1':
    profiles.append(('server_batch_q1_q10_10reps', {7}, 110, 200))
configs = json.loads((root / 'scripts/comparison/configs.json').read_text())
for name, exponents, command_count, proof_count in profiles:
    cfg = configs[name]
    assert cfg['repetitions'] == 10 and cfg['threads'] == 32
    assert cfg['rho'] == '1/2' and cfg['queries'] == 309
    plan = json.loads(subprocess.check_output([sys.executable, str(root / 'scripts/comparison/run.py'), '--config', name, '--scheme', 'both', '--plan'], text=True))
    commands = plan['commands']
    assert len(commands) == command_count
    assert {int(c[c.index('-K') + 1]) for c in commands} == exponents
    records = sum(int(c[c.index('-repetitions') + 1]) if Path(c[0]).name == 'zkmatrix' else 1 for c in commands)
    assert records == proof_count
    for c in commands:
        if Path(c[0]).name == 'zkmatrix':
            assert int(c[c.index('-max-matrix-elements') + 1]) >= 2 ** (2 * int(c[c.index('-K') + 1]))
    if 'batch' in name:
        assert {int(c[c.index('-batch') + 1]) for c in commands} == set(range(1, 11))
    print(name, '| 행렬 크기:', ','.join(str(2**k) for k in sorted(exponents)), '| 각 10회 | 총 증명:', records, flush=True)
PY

zkmap_stage=square
[[ "$include_batch" == 1 ]] && zkmap_stage=both
python3 "$script_dir/run_epyc_zkmap.py" --checkout "$checkout" --profile "$zkmap_stage" --plan | python3 -c '
import json, sys
p=json.load(sys.stdin)
assert p["variant"] == "completeness-roots-v1"
assert p["security_certified"] is False and p["comparison_eligible_as_published_zkmap"] is False
square=[c for c in p["commands"] if c["name"].startswith("square")]
assert [c["n"] for c in square] == [128,256,512,1024,2048]
for item in p["commands"]:
    c=item["command"]
    assert c[c.index("-repetitions")+1] == "10" and c[c.index("-threads")+1] == "32"
    assert c[c.index("-input")+1] == "random"
assert len(p["commands"]) in (5,15)
print("zkMaP completeness-roots-v1 | 행렬 크기: 128,256,512,1024,2048 | 각 10회 | 증명:",len(p["commands"])*10)
print("주의: 수정판의 측정이며, 원문 zkMaP의 soundness 또는 성능 재현으로 취급하지 않습니다.")
'

if [[ "$mode" == plan ]]; then
  printf '계획 확인 완료. 실험은 시작하지 않았습니다.\n'
  exit 0
fi

export PATH="$HOME/.local/lamp-go-1.26.2/bin:$PATH"
export GOMAXPROCS=32
[[ "$(go version)" == 'go version go1.26.2 linux/amd64' ]] || {
  printf 'Go 버전이 기존 측정 환경과 다릅니다. 설치 상태를 확인하세요.\n' >&2
  exit 1
}

stamp="$(date -u +%Y%m%dT%H%M%SZ)"
result_dir="$checkout/benchmark/comparison/vm_three_10reps_k7_k11_$stamp"
mkdir -p "$checkout/benchmark/comparison"
mkdir "$result_dir"
archive="$HOME/lamp-three-results-10reps-k7-k11-$stamp.tar.gz"

set_state() {
  python3 - "$result_dir" "$1" <<'PY'
import json, sys
from pathlib import Path
p=Path(sys.argv[1])/'run-state.json'
t=p.with_suffix('.tmp')
t.write_text(json.dumps({'state':sys.argv[2]})+'\n')
t.replace(p)
PY
}

failure() {
  code=$?
  trap - ERR
  set_state failed || true
  printf '실험이 오류로 중단됐습니다. 결과와 로그를 확인하세요: %s\n' "$result_dir" >&2
  if tar --exclude='*/bin' -czf "$archive" -C "$result_dir" .; then
    printf '중단 시점 자료를 보존한 파일: %s\n' "$archive" >&2
  fi
  exit "$code"
}
trap failure ERR

cp scripts/comparison/configs.json "$result_dir/configs.json"
cp "$script_dir/"{run_epyc_10reps.sh,run_epyc_zkmap.py,zkmap_10reps.json,comparison_10reps.json,prepare_comparison_3reps.py} "$result_dir/"
cp SOURCE_PROVENANCE.json "$result_dir/"
cp docs/comparison/ZKMAP_COMPLETENESS_REPAIR.md "$result_dir/"
git rev-parse HEAD > "$result_dir/source_commit.txt"
set_state validation
python3 - "$result_dir" <<'PY'
import json, platform, sys
from pathlib import Path
Path(sys.argv[1], 'comparison-scope.json').write_text(json.dumps({
    'repository':'https://github.com/lysias9049/FastMatMul',
    'source_commit':'b34d2287c30730a3990d92630185a0a792a2897f',
    'square_sizes':[128,256,512,1024,2048], 'repetitions':10, 'threads':32,
    'scheme_labels':['LAMP','independent zkMatrix','zkMaP completeness-roots-v1'],
    'zkmap_comparison_eligible_as_published_protocol':False,
    'zkmap_security_certified':False,
    'zkmap_missing_checks':['projection binding to ABC commitments','degree constraints','zero-knowledge hiding'],
    'timing_scope':'commit-inclusive online prove; setup and actual AB computation separate',
    'python':sys.version, 'os':platform.platform()
},indent=2)+'\n')
PY
printf '결과 폴더: %s\n기본 검증 시작\n' "$result_dir"
python3 -m unittest discover -s scripts/comparison -p 'test_*.py' > "$result_dir/runner-tests.log" 2>&1 || {
  cat "$result_dir/runner-tests.log"; false
}
go test ./crypto/zkmatrix ./crypto/zkmap ./cmd/zkmap > "$result_dir/protocol-tests.log" 2>&1 || {
  cat "$result_dir/protocol-tests.log"; false
}
set_state zkmap_build_and_preflight
mkdir "$result_dir/bin" "$result_dir/zkmap-preflight"
go build -o "$result_dir/bin/zkmap" ./cmd/zkmap > "$result_dir/zkmap-build.log" 2>&1 || {
  cat "$result_dir/zkmap-build.log"; false
}
# Check the small normal-input variant before spending time on any large grid.
python3 - "$checkout" "$script_dir" "$result_dir" <<'PY'
import sys
from pathlib import Path
sys.path.insert(0,sys.argv[2])
from run_epyc_zkmap import load_runner, measured_call
root, result=Path(sys.argv[1]),Path(sys.argv[3])
runner=load_runner(root,Path(sys.argv[2])/'zkmap_10reps.json')
c=[str(result/'bin/zkmap'),'-variant','completeness-roots-v1','-K','2','-repetitions','1','-threads','32','-max-matrix-elements','16','-input','random','-output',str(result/'zkmap-preflight/attempts.jsonl')]
raise SystemExit(measured_call(runner,c,result/'zkmap-preflight',300))
PY

printf '기본 검증 통과. 단일 행렬 128~2048, 각 10회 시작\n'
date -u
set_state lamp_zkmatrix_square
python3 scripts/comparison/run.py --config server_square_k7_k11_10reps \
  --scheme both --plan > "$result_dir/square-plan.json"
python3 scripts/comparison/run.py --config server_square_k7_k11_10reps \
  --scheme both --output "$result_dir/square"

if [[ "$include_batch" == 1 ]]; then
  printf '단일 행렬 완료. 배치 q=1~10, 각 10회 시작\n'
  date -u
  set_state lamp_zkmatrix_batch
  python3 scripts/comparison/run.py --config server_batch_q1_q10_10reps \
    --scheme both --plan > "$result_dir/batch-plan.json"
  python3 scripts/comparison/run.py --config server_batch_q1_q10_10reps \
    --scheme both --output "$result_dir/batch"
fi

printf 'LAMP·zkMatrix 완료. zkMaP 수정판 단일 행렬 128~2048, 각 10회 시작\n'
date -u
set_state zkmap_square
python3 "$script_dir/run_epyc_zkmap.py" --checkout "$checkout" --profile square --plan > "$result_dir/zkmap-square-plan.json"
python3 "$script_dir/run_epyc_zkmap.py" --checkout "$checkout" --profile square \
  --binary "$result_dir/bin/zkmap" --execute --output "$result_dir/zkmap-square"
if [[ "$include_batch" == 1 ]]; then
  set_state zkmap_batch
  python3 "$script_dir/run_epyc_zkmap.py" --checkout "$checkout" --profile batch --plan > "$result_dir/zkmap-batch-plan.json"
  python3 "$script_dir/run_epyc_zkmap.py" --checkout "$checkout" --profile batch \
    --binary "$result_dir/bin/zkmap" --execute --output "$result_dir/zkmap-batch"
fi

set_state complete
tar --exclude='*/bin' -czf "$archive" -C "$result_dir" .
date -u
printf '전체 실험 완료. 다운로드할 파일:\n%s\n' "$archive"
printf '다운로드 완료를 확인한 뒤 Google Cloud에서 VM을 중지하고 상태를 확인하세요.\n'
