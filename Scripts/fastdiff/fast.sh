#!/bin/bash
# fast.sh <file.cpp> <mangled symbol> [--show]
# Compiles one TU (build.py --single_cpp, a few seconds) and prints how many instructions of the
# function still differ from the target object Scripts/asm/<file.cpp>.obj (see README.md).
# Prints ERR when the TU doesn't compile (log: build_vc6/fastdiff_build.log).
set -u
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CPP=$1
SYM=$2
SHOW=${3:-}
cd "$ROOT"
[ -f venv/bin/activate ] && . venv/bin/activate
export WINEDEBUG=-all
mkdir -p build_vc6
LOG=build_vc6/fastdiff_build.log
OUT=build_vc6/fastdiff_diff.json
TARGET=Scripts/asm/$CPP.obj
[ -f "$TARGET" ] || { echo "no $TARGET: run Scripts/generate_target_asm_for_objs.py $CPP and make_objs.sh" >&2; exit 2; }
rm -f "Source/$CPP.obj"
timeout 300 python3 build.py --single_cpp "$CPP" > "$LOG" 2>&1
[ -f "Source/$CPP.obj" ] || { echo ERR; exit 1; }
objdiff-cli diff -1 "$TARGET" -2 "Source/$CPP.obj" "$SYM" -o "$OUT" --format json > /dev/null 2>&1 || { echo ERR; exit 1; }
KEY=$(echo "$SYM" | sed 's/^?//' | cut -d@ -f1)
python3 Scripts/fastdiff/score.py "$OUT" "$KEY" $SHOW
