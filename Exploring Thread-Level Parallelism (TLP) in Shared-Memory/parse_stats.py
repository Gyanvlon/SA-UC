#!/usr/bin/env python3
# Parse gem5 stats.txt to extract:
# - sim_seconds (if present)
# - system.cpuN.numCycles or similar
# - committed instructions per cpu (e.g., system.cpuN.commit.committedInsts)
# This parser is intentionally robust: it prints lines that match common metric names,
# and otherwise prints a best-effort summary.

import sys
import re
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: parse_stats.py <stats.txt>")
    sys.exit(1)

p = Path(sys.argv[1])
if not p.exists():
    print("File not found:", p)
    sys.exit(2)

lines = p.read_text().splitlines()

# Helpful keys to search for (common names across gem5 variants)
keys = {
    'sim_seconds': re.compile(r'^\s*sim_seconds\s+([\d\.Ee+-]+)'),
    'sim_ticks': re.compile(r'^\s*sim_ticks\s+([\d\.Ee+-]+)'),
    'system_tick': re.compile(r'^\s*system.cpu.*numCycles\s+([\d\.Ee+-]+)'),
    'committed_insts': re.compile(r'^\s*system.cpu.*committedInsts\s+([\d\.Ee+-]+)'),
    'insts': re.compile(r'^\s*system.cpu.*numInsts\s+([\d\.Ee+-]+)'),
    'floatSimd_util': re.compile(r'.*FloatSimd.*util.*\s+([\d\.Ee+-]+)'),
}

found = {}
for key, rx in keys.items():
    found[key] = []

for line in lines:
    for key, rx in keys.items():
        m = rx.match(line)
        if m:
            found[key].append((line.strip(), m.group(1)))

# Print summary
print("Parsed stats summary from", p)
for key, entries in found.items():
    if entries:
        print(f"\n{key} entries:")
        for e in entries:
            print("  ", e[0])
    else:
        print(f"\n{key}: NOT FOUND")

# Heuristics: compute IPC per CPU if cycles and inst counts found
# Try to find per-cpu cycles and insts by regex
cycles = {}
insts = {}
for line in lines:
    cm = re.match(r'^\s*system\.cpu(\d+)\..*numCycles\s+([\d\.Ee+-]+)', line)
    if cm:
        cpu = int(cm.group(1))
        cycles[cpu] = float(cm.group(2))
    im = re.match(r'^\s*system\.cpu(\d+)\..*(numInsts|committedInsts)\s+([\d\.Ee+-]+)', line)
    if im:
        cpu = int(im.group(1))
        insts[cpu] = float(im.group(3))

if cycles and insts:
    print("\nPer-CPU IPC estimates:")
    for cpu in sorted(set(list(cycles.keys()) + list(insts.keys()))):
        c = cycles.get(cpu, None)
        i = insts.get(cpu, None)
        if c and i:
            ipc = i / c
            print(f" CPU{cpu}: insts={i:.0f} cycles={c:.0f} IPC={ipc:.4f}")
        else:
            print(f" CPU{cpu}: missing data (insts={i} cycles={c})")
else:
    print("\nCould not compute IPC: cycles or inst counts missing or different metric names.")