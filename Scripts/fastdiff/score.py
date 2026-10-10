"""Count the instructions of one function that differ from the target, from an objdiff JSON diff.

Usage: score.py <objdiff.json> <symbol substring> [--show]

Ignores what the verifier (post_process_asm.py) also ignores: symbol names and absolute addresses,
branch and call targets, and switch jump table entries. What is left are real differences:
registers, operand order, stack offsets, missing or extra instructions.
"""
import json
import re
import sys


def load(path, key):
    d = json.load(open(path))

    def ins(side):
        syms = [s for s in d[side]["symbols"] if key in s.get("name", "")]
        if not syms:
            sys.exit(f"symbol containing {key!r} not found on the {side} side")
        return syms[0]["instructions"]

    return ins("left"), ins("right")


def norm(f):
    f = re.sub(r"^(j\w+ (?:short )?)0x[0-9a-f]+$", r"\1T", f)
    f = re.sub(r"\?[^\s\],]+|\$L\d+", "SYM", f)
    f = re.sub(r"0x[0-9a-f]{6,}", "SYM", f)
    return f


def diffs(left, right):
    for a, b in zip(left, right):
        fa = (a.get("instruction") or {}).get("formatted")
        fb = (b.get("instruction") or {}).get("formatted")
        if (fa or "").startswith(".dword") or (fb or "").startswith(".dword"):
            continue
        if fa is None or fb is None:
            yield fa, fb
            continue
        if fa.startswith(("jmp", "call")) and fb.startswith(("jmp", "call")):
            continue
        if norm(fa) != norm(fb):
            yield fa, fb


def main():
    left, right = load(sys.argv[1], sys.argv[2])
    rows = list(diffs(left, right))
    if "--show" in sys.argv:
        for fa, fb in rows:
            print(f"{fa or '-':45} | {fb or '-'}")
    print(len(rows))


if __name__ == "__main__":
    main()
