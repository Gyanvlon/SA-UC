#!/bin/bash
# Run DVFS comparison across all operating points
# Author: Gyanvlon

GEM5_PATH="../build/ARM/gem5.opt"
CONFIG_PATH="configs/iot_microprocessor_dvfs.py"
WORKLOAD="workloads/bin/sensor_simulation"

echo "=========================================="
echo "DVFS Operating Point Comparison"
echo "=========================================="
echo "Workload: $WORKLOAD"
echo ""

mkdir -p results

declare -a OPS=("low_power" "balanced" "high_perf" "max_perf")

for op in "${OPS[@]}"; do
    echo ""
    echo "=========================================="
    echo "Testing: $op"
    echo "=========================================="

    OUTPUT_DIR="results/m5out_${op}"

    $GEM5_PATH $CONFIG_PATH \
        --cmd=$WORKLOAD \
        --operating-point=$op \
        --outdir=$OUTPUT_DIR

    if [ -f "$OUTPUT_DIR/stats.txt" ]; then
        echo ""
        echo "Quick Results for $op:"
        echo "----------------------"
        grep "sim_seconds" $OUTPUT_DIR/stats.txt | head -1
        grep "system.cpu.ipc" $OUTPUT_DIR/stats.txt | head -1
    fi
    echo ""
done

echo ""
echo "=========================================="
echo "All DVFS tests complete!"
echo "=========================================="
echo "Results: results/"
echo ""
echo "Run analysis:"
echo "  python3 scripts/analyze_results.py"
echo "=========================================="