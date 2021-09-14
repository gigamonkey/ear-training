#!/usr/bin/env python

import re
from glob import glob
from pathlib import Path

from_import = re.compile(r"^from (.*) import")
module_import = re.compile(r"^import (.*)")


def emit_deps(filename):
    with open(filename) as f:
        for line in f:
            if m := (from_import.match(line) or module_import.match(line)):
                dep = m.group(1)
                if Path(f"{dep}.py").exists():
                    yield (filename.stem, dep)


if __name__ == "__main__":

    ignore = {"rowrow", "test", "music", "midi"}

    deps = set()

    for f in glob("*.py"):
        deps.update(emit_deps(Path(f)))

    print("digraph G {")
    print("  rankdir=LR;")
    for a, b in sorted(deps):
        if not ({a, b} & ignore):
            print(f"  {a} -> {b};")
    print("}")
