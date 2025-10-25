#!/bin/bash
# Run a single simulation
# Author: Gyanvlon

GEM5_PATH="../build/ARM/gem5.opt"
CONFIG_PATH="configs/iot_microprocessor.py"

WORKLOAD="workloads/bin/sensor_simulation"
FREQ="200MHz"
VOLT="0.75V"

while [[ $# -gt 0 ]]; do
    case $1 in
        --workload) WORKLOAD="$2"; shift 2 ;;
        --freq) FREQ="$2"; shift 2 ;;
        --volt) VOLT="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "=========================================="
echo "Running Single Simulation"
echo "=========================================="
echo "Workload: $WORKLOAD"
echo "Frequency: $FREQ"
echo "Voltage: $VOLT"
echo "=========================================="
echo ""

$GEM5_PATH $CONFIG_PATH \
    --cmd=$WORKLOAD \
    --cpu-clock=$FREQ \
    --cpu-voltage=$VOLT \
    --l2-voltage=$VOLT

echo ""
echo "=========================================="
echo "Simulation complete!"
echo "Results: m5out/"
echo "=========================================="