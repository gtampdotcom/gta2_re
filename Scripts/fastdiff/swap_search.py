"""Try swapping each pair of adjacent independent statements in one function and score each variant.

Usage: swap_search.py <file.cpp> <mangled symbol> "<text of the function's definition line>"

Each variant is compiled with fast.sh (a few seconds). Prints the base score and one line per
swap: source line, score, the two statements. The source file is restored at the end.
Strip WIP_IMPLEMENTED/NOT_IMPLEMENTED from the function first, since both add code.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def simple(line):
    t = line.strip()
    if not t.endswith(";") or "{" in t or "}" in t:
        return False
    return not t.startswith(("return", "break", "case", "goto", "continue", "//"))


def lhs(line):
    return line.split("=")[0].strip().rstrip("+-*/|&").strip() if "=" in line else ""


def main():
    cpp, sym, start = sys.argv[1:4]
    path = os.path.join(ROOT, "Source", cpp)
    orig = open(path).read()
    lines = orig.splitlines(keepends=True)
    s = next(i for i, l in enumerate(lines) if start in l)
    e = next(i for i in range(s, len(lines)) if lines[i] == "}\n")

    def score(text):
        open(path, "w").write(text)
        r = subprocess.run([os.path.join(HERE, "fast.sh"), cpp, sym], capture_output=True, text=True)
        return r.stdout.strip()

    try:
        print("base", score(orig), flush=True)
        for i in range(s, e - 1):
            a, c = lines[i], lines[i + 1]
            if not (simple(a) and simple(c)):
                continue
            if len(a) - len(a.lstrip()) != len(c) - len(c.lstrip()):
                continue
            la, lc = lhs(a), lhs(c)
            # skip pairs where one statement reads what the other writes
            if la and la in c.split("=", 1)[-1]:
                continue
            if lc and lc in a.split("=", 1)[-1]:
                continue
            m = lines[:]
            m[i], m[i + 1] = c, a
            print(i + 1, score("".join(m)), a.strip()[:50], "<->", c.strip()[:50], flush=True)
    finally:
        open(path, "w").write(orig)


if __name__ == "__main__":
    main()
