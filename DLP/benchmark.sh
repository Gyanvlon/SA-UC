#!/bin/bash
# Run DLP Benchmarks in gem5
# Author: Gyanvlon
# Date: 2025-11-02

GEM5_PATH="/path/to/gem5"
GEM5_BIN="$GEM5_PATH/build/X86/gem5.opt"
CONFIG_SCRIPT="gem5_configs/dlp_system.py"
RESULTS_DIR="gem5_results"

mkdir -p $RESULTS_DIR

echo "=========================================="
echo "  DLP Assignment - gem5 Simulation"
echo "  Author: Gyanvlon"
echo "=========================================="

# CPU configurations to test
CPU_TYPES=("TimingSimpleCPU" "MinorCPU" "O3CPU")
CORE_COUNTS=(1 2 4 8)

# Run vector benchmark
echo -e "\n[1/3] Running Vector Benchmark..."
for cpu in "${CPU_TYPES[@]}"; do
    for cores in "${CORE_COUNTS[@]}"; do
        echo "  Testing $cpu with $cores cores..."
        $GEM5_BIN \
            --outdir=$RESULTS_DIR/vector_${cpu}_${cores}cores \
            $CONFIG_SCRIPT \
            --cpu-type=$cpu \
            --num-cores=$cores \
            --cmd=gem5_benchmarks/vector_benchmark
    done
done

# Run SIMD benchmark
echo -e "\n[2/3] Running SIMD Benchmark..."
for cpu in "${CPU_TYPES[@]}"; do
    echo "  Testing $cpu..."
    $GEM5_BIN \
        --outdir=$RESULTS_DIR/simd_${cpu} \
        $CONFIG_SCRIPT \
        --cpu-type=$cpu \
        --num-cores=1 \
        --cmd=gem5_benchmarks/simd_benchmark
done

# Run loop parallelism benchmark
echo -e "\n[3/3] Running Loop Parallelism Benchmark..."
for cores in "${CORE_COUNTS[@]}"; do
    echo "  Testing with $cores cores..."
    $GEM5_BIN \
        --outdir=$RESULTS_DIR/loop_${cores}cores \
        $CONFIG_SCRIPT \
        --cpu-type=O3CPU \
        --num-cores=$cores \
        --cmd=gem5_benchmarks/loop_benchmark
done

echo -e "\n=========================================="
echo "  Simulation Complete!"
echo "  Results saved in: $RESULTS_DIR/"
echo "=========================================="