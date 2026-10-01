#!/usr/bin/env python3
"""LAMP·zkMatrix 비교 설정을 구현 저장소에 추가한다. 실험은 실행하지 않는다.

사용법: python3 prepare_comparison_3reps.py /path/to/LAMP-comparison
기본값은 이 스크립트와 같은 폴더의 comparison_3reps.json이다.
10회 설정: python3 prepare_comparison_3reps.py /path/to/LAMP-comparison --profiles /path/to/comparison_10reps.json
검증한 소스: comparison/zkmatrix-benchmarks, 317b4cba9b1d0da17697a9435ad3539380f6a58c.
FastMatMul b34d228의 동일 runner에도 사용할 수 있다. zkMaP 설정은 별도 JSON으로 관리한다.
기존 설정은 보존하며, 같은 설정을 다시 추가하는 것은 허용한다.
"""

import argparse
import json
from pathlib import Path
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkout", type=Path, help="comparison 브랜치의 저장소 경로")
    parser.add_argument("--profiles", type=Path,
                        default=Path(__file__).with_name("comparison_3reps.json"),
                        help="추가할 설정 JSON 파일; 기본값은 comparison_3reps.json")
    args = parser.parse_args()
    root = args.checkout.resolve()
    target = root / "scripts/comparison/configs.json"
    required = [target, root / "scripts/comparison/run.py"]
    required.extend(root / "cmd" / name / "main.go" for name in ("lamp", "lamp_batch", "zkmatrix"))
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        parser.error("comparison 브랜치 파일을 찾을 수 없음: " + ", ".join(missing))

    existing = json.loads(target.read_text(encoding="utf-8"))
    additions = json.loads(args.profiles.read_text(encoding="utf-8"))
    for name, config in additions.items():
        if name in existing and existing[name] != config:
            parser.error(f"다른 내용의 설정이 이미 있음: {name}. 덮어쓰지 않았음.")
    changed = any(name not in existing for name in additions)
    if changed:
        existing.update(additions)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent, delete=False) as handle:
                temporary = Path(handle.name)
                json.dump(existing, handle, indent=2, ensure_ascii=False)
                handle.write("\n")
            temporary.replace(target)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    print(f"{'설정 추가 완료' if changed else '이미 같은 설정이 있음'}: {target}")
    print("실험은 실행하지 않았음. 저장소에서 다음 명령으로 실행 계획만 확인할 수 있음:")
    for name in additions:
        print(f"python3 scripts/comparison/run.py --config {name} --scheme both --plan")


if __name__ == "__main__":
    main()
