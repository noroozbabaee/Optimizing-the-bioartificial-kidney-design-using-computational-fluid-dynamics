"""Static audit of the generated COMSOL Model Java files.

Run:  python3 src/audit_comsol_java.py

This does NOT prove the models open in COMSOL (no COMSOL here). It checks the
things that HAVE actually broken File>Open on the university COMSOL 6.4 build,
plus internal consistency that a compiler cannot see.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
COMSOL = REPO / "comsol"
FILES = ["BAK_IO.java", "BAK_OI.java", "BAK_OI_fair.java"]

# Calls that this COMSOL 6.4 build rejected with Unknown parameter / feature ID.
BANNED = {
    r'setIndex\("D_c"': "D_c is not a property on 6.4",
    r'setIndex\("Dc"': "Dc rejected by this 6.4 build",
    r'setIndex\("c0"': "c0 rejected by this 6.4 build",
    r'setIndex\("N0"': "N0 rejected; set flux in GUI",
    r'\.set\("is"': "species name is not a property",
    r'\.set\("isc"': "species name is not a property",
    r'\.set\("isd"': "species name is not a property",
    r'"ConvectionDiffusion"': "unknown feature ID on 6.4",
    r'"ReactingFlowDilutedSpecies"': "multiphysics create blocks File>Open",
    r"minput_velocity_src": "unknown on 6.4",
    r'\.set\("FluidFlow"': "unknown multiphysics property",
    r'\.set\("DilutedSpecies"': "unknown multiphysics property",
    r'feature\("cdm1"\)': "default feature tag may not exist",
    r'feature\("init1"\)': "default feature tag may not exist",
    r'prop\("ShapeProperty"\)': "property may not exist on 6.4",
    r"System\.exit": "kills the COMSOL server on File>Open",
    r"model\.save": "IOException during File>Open",
}


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def audit(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8")
    code = strip_comments(raw)
    problems: list[str] = []

    for pattern, why in BANNED.items():
        for m in re.finditer(pattern, code):
            line = code[: m.start()].count("\n") + 1
            problems.append(f"banned call {pattern} (~line {line}): {why}")

    non_ascii = [i + 1 for i, ln in enumerate(raw.splitlines()) if not ln.isascii()]
    if non_ascii:
        problems.append(f"non-ASCII on lines {non_ascii} (Windows compile encoding)")

    if path.stem != re.search(r"public class (\w+)", raw).group(1):
        problems.append("class name does not match file name")

    main_body = re.search(r"public static void main\([^)]*\)\s*\{(.*?)\n  \}", raw, re.S)
    if main_body and main_body.group(1).count(";") != 1:
        problems.append("main() must contain only run();")

    # Every named selection must be created before use.
    created = set(re.findall(r'selection\(\)\.create\("(\w+)"', code))
    created |= set(re.findall(r'boxEdge\(model, "(\w+)"', code))
    created |= set(re.findall(r'explicitDomain\(model, "(\w+)"', code))
    for used in set(re.findall(r'\.named\("(\w+)"\)', code)):
        if used not in created:
            problems.append(f"selection '{used}' used but never created")

    # Every selection must declare an entity dimension.
    for block in re.findall(r'selection\(\)\.create\("(\w+)", "(\w+)"\)', code):
        tag, kind = block
        if kind in {"Box", "Explicit"}:
            scope = code.split(f'create("{tag}", "{kind}")', 1)[1][:600]
            if "entitydim" not in scope and ".geom(" not in scope:
                problems.append(f"selection '{tag}' has no entitydim")

    # Physics feature tags must be created before they are configured.
    for phys, tag in re.findall(r'physics\("(\w+)"\)\.feature\("(\w+)"\)', code):
        if f'physics("{phys}").create("{tag}"' not in code:
            problems.append(f"physics {phys} uses feature '{tag}' that is never created")

    return problems


def main() -> int:
    failed = False
    for name in FILES:
        path = COMSOL / name
        if not path.exists():
            print(f"MISSING {name}")
            failed = True
            continue
        problems = audit(path)
        if problems:
            failed = True
            print(f"FAIL {name}")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"OK   {name}")
    if failed:
        print("\nAudit found problems.")
        return 1
    print("\nAll files pass the static COMSOL 6.4 audit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
