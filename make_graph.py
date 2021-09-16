#!/usr/bin/env python

import os.path
from os import walk
import re
from glob import glob
from pathlib import Path

from_import = re.compile(r"^from (.*) import")
module_import = re.compile(r"^import (.*)")


def code_name(p):
    return f"{p.parent}.{p.stem}".replace('/', '.')

def emit_deps(filename):
    with open(filename) as f:
        for line in f:
            if m := (from_import.match(line) or module_import.match(line)):
                dep = m.group(1)
                #if Path(f"{dep}.py").exists():
                yield (code_name(filename), dep)



if __name__ == "__main__":

    #ignore = {"rowrow", "test", "music", "midi"}
    ignore = {"eartraining.music", "eartraining.midi"}

    deps = set()

    for root, dirs, files in os.walk("eartraining"):
        for name in files:
            p = Path(os.path.join(root, name))
            if p.match("*.py"):
                deps.update(emit_deps(p))

    print("digraph G {")
    print("  rankdir=LR;")
    for a, b in sorted(deps):
        if (not ({a, b} & ignore)) and b.startswith("eartraining"):
            print(f'  "{a}" -> "{b}";')
    print("}")
