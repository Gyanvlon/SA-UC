#!/usr/bin/env bash
# Script to automate experiments:
# - Vary opLat/issueLat combinations summing to 7
# - Vary thread (cpu) counts
# - Run gem5 with timestamps and save stats directories
#
# Adapt GEM5_BIN and GEM5_RUN_PY as needed.

GEM5_BIN=build/X86/gem5.opt     # path to your built gem5 binary
RUN_PY=run_minor.py
BINARY=./daxpy
VEC_N=2000000
REPS=50

# Ensure daxpy built
if [ ! -f "${BINARY}" ]; then
  echo "daxpy binary not found. Run 'make' first."
  exit 1
fi

# opLat / issueLat pairs where sum=7
pairs=("1:6" "2:5" "3:4" "4:3" "5:2" "6:1")
cpu_counts=(1 2 4 8)

OUTDIR=gem5_results
mkdir -p ${OUTDIR}

for p in "${pairs[@]}"; do
  op=${p%%:*}
  issue=${p##*:}
  for cpus in "${cpu_counts[@]}"; do
    name="op${op}_iss${issue}_cpus${cpus}"
    logdir="${OUTDIR}/${name}"
    mkdir -p "${logdir}"
    echo "Running ${name} ..."
    ${GEM5_BIN} ${RUN_PY} --num-cpus=${cpus} --oplat=${op} --issuelat=${issue} --cmd=${BINARY} --cmd-args="${VEC_N} ${cpus} ${REPS}" --stats-file=${logdir}/stats.txt  > ${logdir}/stdout.txt 2> ${logdir}/stderr.txt
    echo "Finished ${name}, logs in ${logdir}"
  done
done