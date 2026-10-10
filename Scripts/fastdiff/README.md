# fastdiff: score one function in a few seconds

A full `build.py` + `compare_target_asm.py` round trip takes about two minutes. When you try many
source variants of one function, this loop is much faster: compile only its TU, diff only that
function against the target object, and count the instructions that really differ.

```bash
# once per TU: target object from 10.5.exe (WIP/STUB functions only)
python3 Scripts/generate_target_asm_for_objs.py char.cpp && (cd Scripts/asm && ./make_objs.sh)

# strip the diagnostics from the function you work on (they add code)
sed -i -E 's/^(\s*)(WIP_IMPLEMENTED|NOT_IMPLEMENTED);\s*$/\1;/' Source/char.cpp

Scripts/fastdiff/fast.sh char.cpp '?state_8_5520A0@Char_B4@@QAEXXZ'          # -> 6
Scripts/fastdiff/fast.sh char.cpp '?state_8_5520A0@Char_B4@@QAEXXZ' --show   # the rows, then the count
```

Mangled names come from `nm Scripts/asm/<file>.cpp.obj`. `ERR` means the TU didn't compile
(`build_vc6/fastdiff_build.log`).

`score.py` ignores what the verifier ignores too (symbol names, absolute addresses, branch and
call targets, jump table entries), so 0 here should mean `compare_target_asm.py` reports MATCH.
Always confirm a 0 with the full build: the linked exe is the real check.

`swap_search.py` tries every swap of two adjacent independent statements in a function and scores
each one (about 5 s per variant):

```bash
python3 Scripts/fastdiff/swap_search.py char.cpp '?state_8_5520A0@Char_B4@@QAEXXZ' 'void Char_B4::state_8_5520A0()'
```

It restores the file afterwards. Lines it reports with a lower score than `base` are worth a look;
check that a swap keeps the behaviour before you keep it.
